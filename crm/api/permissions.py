import frappe
from frappe import _
from typing import Dict, List, Optional, Tuple, Any


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


def _safe_json_loads(val: Optional[str]) -> List[str]:
    try:
        if not val:
            return []
        import json

        parsed = json.loads(val) if isinstance(val, str) else val
        return parsed if isinstance(parsed, list) else []
    except Exception:
        return []


def _is_user_assigned_to_doc(doctype: str, name: str, user: Optional[str] = None) -> bool:
    """Return True if the given user is present in the document's _assign list.

    Note: We treat empty/None _assign as "no one assigned" — i.e., returns False.
    System Manager checks should be handled by callers.
    """
    try:
        user = user or frappe.session.user
        assign = frappe.db.get_value(doctype, name, "_assign")
        assigned_list = _safe_json_loads(assign)
        return user in set(assigned_list or [])
    except Exception:
        return False


def _getattr(doc: Any, key: str) -> Optional[Any]:
    if doc is None:
        return None
    try:
        if isinstance(doc, dict):
            return doc.get(key)
        return getattr(doc, key, None)
    except Exception:
        return None


def _extract_parent_context(doc: Any) -> Tuple[Optional[str], Optional[str]]:
    """Try to determine parent reference (Lead/Ticket) for a related document.

    Supports common patterns used in this app:
    - reference_doctype + reference_docname/reference_name (Tasks, Communication)
    - attached_to_doctype + attached_to_name (File)
    """
    if not doc:
        return (None, None)

    # Preferred fields
    rdt = _getattr(doc, "reference_doctype")
    rname = _getattr(doc, "reference_docname") or _getattr(doc, "reference_name")
    if rdt and rname:
        return (rdt, rname)

    # File attachment style
    adt = _getattr(doc, "attached_to_doctype")
    aname = _getattr(doc, "attached_to_name")
    if adt and aname:
        return (adt, aname)

    return (None, None)


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


def _is_system_manager(user: Optional[str]) -> bool:
    try:
        if not user:
            user = frappe.session.user
        if user == "Administrator":
            return True
        roles = frappe.get_roles(user)
        return "System Manager" in roles
    except Exception:
        return False
@frappe.whitelist()
def can_delete_doc(doctype: str, name: str, user: Optional[str] = None) -> Dict[str, bool]:
    """Return { allowed: bool } if user can delete the given document.

    Rule: For `CRM Lead` and `CRM Ticket`, only System Manager/admins or assigned users are allowed.
    For other doctypes, rely on Frappe's has_permission("delete").
    """
    try:
        user = user or frappe.session.user
        # Special rule for core CRM parents
        if doctype in {"CRM Lead", "CRM Ticket"}:
            if _is_system_manager(user):
                return {"allowed": True}
            # Allow if user is assigned
            if _is_user_assigned_to_doc(doctype, name, user):
                return {"allowed": True}
            # Allow if user is document owner or explicit owner field
            try:
                _doc = frappe.get_value(doctype, name, ["owner", "lead_owner", "ticket_owner"], as_dict=True)
                if _doc:
                    if _doc.get("owner") == user:
                        return {"allowed": True}
                    # Permit per-doctype explicit owner
                    if doctype == "CRM Lead" and _doc.get("lead_owner") == user:
                        return {"allowed": True}
                    if doctype == "CRM Ticket" and _doc.get("ticket_owner") == user:
                        return {"allowed": True}
            except Exception:
                pass
            return {"allowed": False}

        # Fallback to standard permission for other doctypes
        try:
            doc = frappe.get_doc(doctype, name)
            allowed = bool(doc.has_permission("delete", user=user))
        except Exception:
            allowed = False
        return {"allowed": allowed}
    except Exception:
        return {"allowed": False}


@frappe.whitelist()
def get_current_user_module_permissions(user: Optional[str] = None) -> Dict[str, str]:
    """Return the effective module permission level for the current (or given) user,
    derived by combining all of their roles.
    """
    if _is_system_manager(user):
        # Full access for System Manager/Administrator
        return {m: "Read & Write" for m in MODULES}
    roles = _get_user_roles(user)
    return _aggregate_role_permissions(roles)


def user_has_module_permission(module: str, ptype: str = "read", user: Optional[str] = None) -> bool:
    user = user or frappe.session.user
    if _is_system_manager(user):
        return True
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
            module = _map_doctype_to_module(getattr(doc, "reference_doctype", None))
        else:
            module = _map_doctype_to_module(dt)

        # Enforce strict delete permissions for core CRM parents (assignment or admin only)
        # Requirement: Only assigned users and admins can delete Leads and Tickets
        ptype_normalized = (ptype or "read").lower()
        if ptype_normalized in {"delete", "cancel", "amend"}:
            try:
                target_dt = dt
                target_name = getattr(doc, "name", None)
                # When only a doctype string is passed, we cannot evaluate record-level
                if target_dt in {"CRM Lead", "CRM Ticket"} and target_name:
                    # System manager/admin bypass
                    if not _is_system_manager(user):
                        if not _is_user_assigned_to_doc(target_dt, target_name, user):
                            return False
                    # At this point, user is allowed by assignment/admin rules, so allow regardless of module gate
                    return True
            except Exception:
                # Fail safe: if we cannot determine, disallow destructive ops
                return False

        # For non-destructive ops, apply module-level gate as usual
        if module and not user_has_module_permission(module, ptype, user):
            return False

        # Next, enforce assignment-based rule for creating related docs of a specific Lead/Ticket
        # Only applies when creating a document that explicitly references a parent Lead/Ticket
        if (ptype or "").lower() in {"create"} and doc:
            parent_dt, parent_name = _extract_parent_context(doc)
            if parent_dt in {"CRM Lead", "CRM Ticket"} and parent_name:
                # System Managers bypass assignment checks
                if not _is_system_manager(user):
                    if not _is_user_assigned_to_doc(parent_dt, parent_name, user):
                        # Not assigned to the parent → treat as read-only for related creates
                        return False

        # If doctype isn't mapped to a module, allow (after assignment check above)
        if not module:
            return True

        # Allowed by module gate and assignment gate
        return True
    except Exception:
        # Fail-open to avoid hard locks in case of unexpected errors
        return True
