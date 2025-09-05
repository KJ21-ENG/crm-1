import frappe
from frappe import _
from typing import Dict, List, Optional


MODULES = [
    "Dashboard",
    "Tickets",
    "Leads",
    "Customers",
    "Support Pages",
    "Notes",
    "Tasks",
    "Call Logs",
]


PERMISSION_VALUES = ["None", "Read", "Read & Write"]


def _normalize_permission(value: Optional[str]) -> str:
    if not value:
        return "Read & Write"
    if value not in PERMISSION_VALUES:
        return "Read & Write"
    return value


def _combine_perm(a: str, b: str) -> str:
    """Combine two permission levels; highest wins.
    Order: None < Read < Read & Write
    """
    order = {"None": 0, "Read": 1, "Read & Write": 2}
    a = _normalize_permission(a)
    b = _normalize_permission(b)
    return a if order[a] >= order[b] else b


def _map_doctype_to_module(doctype: str) -> Optional[str]:
    mapping = {
        # Core modules
        "CRM Ticket": "Tickets",
        "CRM Lead": "Leads",
        "CRM Customer": "Customers",
        "CRM Support Pages": "Support Pages",
        # Ancillary doctypes used in module detail pages
        "CRM Task": "Tasks",
        "Note": "Notes",
        # Communications and Attachments map to the parent via reference_doctype
        "Communication": None,
        "Comment": None,
        "File": None,
    }
    return mapping.get(doctype)


def _get_role_permissions(role: str) -> Dict[str, str]:
    rows = frappe.get_all(
        "CRM Role Module Permission",
        filters={"role": role},
        fields=["module", "permission"],
    )
    return {r["module"]: _normalize_permission(r["permission"]) for r in rows}


def _get_user_roles(user: Optional[str] = None) -> List[str]:
    user = user or frappe.session.user
    try:
        return frappe.get_roles(user)
    except Exception:
        return []


def _aggregate_role_permissions(roles: List[str]) -> Dict[str, str]:
    aggregated: Dict[str, str] = {}
    for role in roles or []:
        rp = _get_role_permissions(role)
        for mod in MODULES:
            current = aggregated.get(mod)
            incoming = rp.get(mod)
            if incoming:
                aggregated[mod] = _combine_perm(current or "None", incoming)
    # Fill defaults for modules not explicitly set on any role
    for mod in MODULES:
        if mod not in aggregated:
            # Default to fully open to preserve existing behavior
            aggregated[mod] = "Read & Write"
    return aggregated


def _level_allows(level: str, ptype: str) -> bool:
    level = _normalize_permission(level)
    ptype = (ptype or "read").lower()
    if ptype in {"read", "report", "print", "email"}:
        return level in {"Read", "Read & Write"}
    elif ptype in {"write", "create", "submit", "cancel", "delete", "amend"}:
        return level == "Read & Write"
    return True


@frappe.whitelist()
def get_role_module_permissions(role: str) -> List[Dict[str, str]]:
    """Return explicit module permissions for a role.
    Ensures all modules are present in the response with a default value.
    """
    rp = _get_role_permissions(role)
    return [{"module": m, "permission": rp.get(m, "Read & Write")} for m in MODULES]


@frappe.whitelist()
def set_role_module_permissions(role: str, permissions: List[dict]):
    """Upsert module permissions for a role.
    `permissions` should be a list of {module, permission}.
    """
    if isinstance(permissions, str):
        # Support JSON string inputs from client
        import json

        permissions = json.loads(permissions)

    # Basic validation
    modules = {p.get("module") for p in permissions if p.get("module")}
    for m in modules:
        if m not in MODULES:
            frappe.throw(_("Invalid module: {0}").format(m))

    # Upsert each entry
    for p in permissions:
        mod = p.get("module")
        perm = _normalize_permission(p.get("permission"))
        if not mod:
            continue
        name = frappe.db.get_value(
            "CRM Role Module Permission", {"role": role, "module": mod}
        )
        if name:
            frappe.db.set_value(
                "CRM Role Module Permission", name, "permission", perm
            )
        else:
            doc = frappe.new_doc("CRM Role Module Permission")
            doc.role = role
            doc.module = mod
            doc.permission = perm
            doc.insert(ignore_permissions=True)
    frappe.db.commit()


@frappe.whitelist()
def get_current_user_module_permissions(user: Optional[str] = None) -> Dict[str, str]:
    """Return the effective module permission level for the current (or given) user,
    derived by combining all of their roles.
    """
    roles = _get_user_roles(user)
    return _aggregate_role_permissions(roles)


def user_has_module_permission(module: str, ptype: str = "read", user: Optional[str] = None) -> bool:
    user = user or frappe.session.user
    levels = get_current_user_module_permissions(user)
    level = levels.get(module, "Read & Write")
    return _level_allows(level, ptype)


def doctype_has_permission(doc=None, ptype: str = "read", user: Optional[str] = None) -> bool:
    """Generic has_permission hook to gate module doctypes by the role-module map.

    Attach this in hooks.has_permission for doctypes like CRM Ticket, CRM Lead, etc.
    """
    try:
        dt = getattr(doc, "doctype", None) if doc else None
        if not dt:
            # Fallback when only doctype string is passed
            dt = doc if isinstance(doc, str) else None

        # Handle communication/comment/file based on reference_doctype
        if dt in {"Communication", "Comment", "File"} and getattr(doc, "reference_doctype", None):
            module = _map_doctype_to_module(doc.reference_doctype)
        else:
            module = _map_doctype_to_module(dt)

        # If not mapped, allow default Frappe permission rules
        if not module:
            return True

        return user_has_module_permission(module, ptype, user)
    except Exception:
        # Fail-open to avoid hard locks in case of unexpected errors
        return True

