from __future__ import annotations

import math
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, Iterable, List, Sequence

import frappe
from frappe import unscrub
from frappe.utils import get_datetime, now_datetime

MIN_QUERY_LENGTH = 2

STOPWORDS: set[str] = {
    "not",
    "and",
    "the",
    "for",
    "with",
    "from",
    "your",
    "you",
    "was",
    "were",
    "has",
    "have",
    "had",
    "this",
    "that",
    "into",
    "onto",
    "upon",
    "been",
    "being",
    "are",
    "will",
    "shall",
    "should",
    "would",
    "could",
    "may",
    "might",
    "can",
    "because",
    "about",
    "over",
    "under",
    "after",
    "before",
    "between",
}


@dataclass(slots=True)
class QueryContext:
    raw: str
    normalized: str
    uppercase: str
    tokens: tuple[str, ...]
    digits: str
    is_email: bool
    is_numeric: bool

    @property
    def plain_terms(self) -> tuple[str, ...]:
        ordered: List[str] = []
        for index, term in enumerate((self.normalized, *self.tokens)):
            if not term:
                continue
            if index > 0 and len(term) < 3 and not any(ch.isdigit() for ch in term):
                continue
            if index > 0 and term in STOPWORDS:
                continue
            if term not in ordered:
                ordered.append(term)
        return tuple(ordered)

    @property
    def like_terms(self) -> tuple[str, ...]:
        return tuple(f"%{term}%" for term in self.plain_terms if term)


@dataclass(slots=True)
class SearchTarget:
    doctype: str
    label: str
    icon: str
    fields: Sequence[str] = ()
    search_fields: Sequence[str] = ()
    id_fields: Sequence[str] = ()
    phone_fields: Sequence[str] = ()
    email_fields: Sequence[str] = ()
    build_title: Callable[[Dict[str, Any]], str] | None = None
    build_subtitle: Callable[[Dict[str, Any]], str | None] | None = None
    build_route: Callable[[Dict[str, Any]], str] | None = None
    build_meta: Callable[[Dict[str, Any]], Dict[str, Any]] | None = None
    extra_filters: Callable[[QueryContext], Dict[str, Any]] | None = None
    order_by: str = "modified desc"
    external: bool = False

    def fieldset(self) -> List[str]:
        fields: set[str] = {"name", "modified"}
        for seq in (
            self.fields,
            self.search_fields,
            self.id_fields,
            self.phone_fields,
            self.email_fields,
        ):
            for field in seq:
                if field:
                    fields.add(field)
        return list(fields)


def build_query_context(query: str) -> QueryContext:
    raw = (query or "").strip()
    normalized = raw.lower()
    uppercase = raw.upper()
    tokens = tuple(filter(None, re.split(r"[\s,;/]+", normalized)))
    digits = re.sub(r"\D", "", raw)
    is_email = bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", raw))
    is_numeric = raw.isdigit()
    return QueryContext(
        raw=raw,
        normalized=normalized,
        uppercase=uppercase,
        tokens=tokens,
        digits=digits,
        is_email=is_email,
        is_numeric=is_numeric,
    )


def _lead_title(doc: Dict[str, Any]) -> str:
    return doc.get("lead_name") or doc.get("customer_name") or doc.get("name") or ""


def _lead_subtitle(doc: Dict[str, Any]) -> str:
    status = doc.get("status")
    return f"Lead • {status}" if status else "Lead"


def _lead_route(doc: Dict[str, Any]) -> str:
    name = doc.get("name")
    return f"/leads/{name}" if name else "/leads/view/list"


def _ticket_title(doc: Dict[str, Any]) -> str:
    return doc.get("subject") or doc.get("ticket_subject") or doc.get("name") or ""


def _ticket_subtitle(doc: Dict[str, Any]) -> str:
    status = doc.get("status") or ""
    priority = doc.get("priority") or ""
    pieces = ["Ticket"]
    if status:
        pieces.append(f"• {status}")
    if priority:
        pieces.append(f"• {priority}")
    return " ".join(pieces)


def _ticket_route(doc: Dict[str, Any]) -> str:
    name = doc.get("name")
    return f"/tickets/{name}" if name else "/tickets/view/list"


def _customer_title(doc: Dict[str, Any]) -> str:
    return doc.get("customer_name") or doc.get("name") or ""


def _customer_subtitle(doc: Dict[str, Any]) -> str:
    organization = doc.get("organization")
    return f"Customer • {organization}" if organization else "Customer"


def _customer_route(doc: Dict[str, Any]) -> str:
    name = doc.get("name")
    return f"/customers/{name}" if name else "/customers/view/list"


def _task_title(doc: Dict[str, Any]) -> str:
    return doc.get("title") or doc.get("name") or ""


def _task_subtitle(doc: Dict[str, Any]) -> str:
    status = doc.get("status")
    return f"Task • {status}" if status else "Task"


def _task_route(doc: Dict[str, Any]) -> str:
    name = doc.get("name")
    return f"/tasks/view/list?open={name}" if name else "/tasks/view/list"


def _note_title(doc: Dict[str, Any]) -> str:
    return doc.get("title") or doc.get("name") or ""


def _note_subtitle(doc: Dict[str, Any]) -> str:
    reference = doc.get("reference_doctype")
    return f"Note • {reference}" if reference else "Note"


def _note_route(doc: Dict[str, Any]) -> str:
    name = doc.get("name")
    return f"/notes/view/list?open={name}" if name else "/notes/view/list"


def _call_log_title(doc: Dict[str, Any]) -> str:
    customer = doc.get("customer_name") or doc.get("customer")
    caller = doc.get("from") or doc.get("to")
    return customer or caller or doc.get("name") or ""


def _call_log_subtitle(doc: Dict[str, Any]) -> str:
    call_type = doc.get("type") or "Call"
    status = doc.get("status")
    return f"{call_type} • {status}" if status else call_type


def _call_log_route(doc: Dict[str, Any]) -> str:
    name = doc.get("name")
    return f"/call-logs/view/list?open={name}" if name else "/call-logs/view/list"


def _support_page_title(doc: Dict[str, Any]) -> str:
    return doc.get("page_name") or doc.get("name") or ""


def _support_page_subtitle(doc: Dict[str, Any]) -> str:
    return "Support Page • Active" if doc.get("is_active") else "Support Page"


def _support_page_route(doc: Dict[str, Any]) -> str:
    link = doc.get("support_link")
    if link:
        return link
    name = doc.get("name")
    return f"/support-pages/view/list" if not name else f"/support-pages/view/list?open={name}"


def _clean_snippet(content: str | None, length: int = 300) -> str:
    """Return a plain-text snippet from HTML/text content, truncated to `length`.

    - Strips HTML tags, unescapes HTML entities, collapses whitespace and trims.
    - Returns an empty string for falsy input.
    """
    if not content:
        return ""
    try:
        # Remove HTML tags
        text = re.sub(r"(?s)<[^>]*>", " ", str(content))
        # Unescape HTML entities using stdlib
        try:
            import html as _html

            text = _html.unescape(text)
        except Exception:
            # fallback: keep as-is if unescape unavailable
            pass

        # Collapse whitespace
        text = re.sub(r"\s+", " ", text).strip()

        if length and len(text) > int(length):
            # Use ellipsis to indicate truncation
            return text[: int(length)].rstrip() + "…"
        return text
    except Exception:
        # On any unexpected error, return a safe stringified fallback
        try:
            return str(content)[: int(length)]
        except Exception:
            return ""


SEARCH_TARGETS: tuple[SearchTarget, ...] = (
    SearchTarget(
        doctype="CRM Lead",
        label="Leads",
        icon="user-plus",
        fields=(
            "lead_name",
            "status",
            "mobile_no",
            "alternative_mobile_no",
            "phone",
            "email",
            "organization",
            "client_id",
            "customer_id",
            "pod_id",
            "pan_card_number",
            "aadhaar_card_number",
        ),
        search_fields=(
            "lead_name",
            "customer_id",
            "client_id",
            "organization",
            "pod_id",
            "pan_card_number",
            "aadhaar_card_number",
        ),
        id_fields=("name", "client_id", "customer_id", "pod_id"),
        phone_fields=("mobile_no", "alternative_mobile_no", "phone"),
        email_fields=("email",),
        build_title=_lead_title,
        build_subtitle=_lead_subtitle,
        build_route=_lead_route,
        build_meta=lambda doc: {
            "status": doc.get("status"),
            "mobile_no": doc.get("mobile_no"),
            "email": doc.get("email"),
            "organization": doc.get("organization"),
        },
    ),
    SearchTarget(
        doctype="CRM Ticket",
        label="Tickets",
        icon="life-buoy",
        fields=(
            "subject",
            "ticket_subject",
            "status",
            "priority",
            "mobile_no",
            "phone",
            "email",
            "customer_name",
            "customer_id",
            "pan_card_number",
            "aadhaar_card_number",
        ),
        search_fields=("subject", "customer_name", "customer_id"),
        id_fields=("name", "customer_id"),
        phone_fields=("mobile_no", "phone"),
        email_fields=("email",),
        build_title=_ticket_title,
        build_subtitle=_ticket_subtitle,
        build_route=_ticket_route,
        build_meta=lambda doc: {
            "status": doc.get("status"),
            "priority": doc.get("priority"),
            "customer": doc.get("customer_name"),
        },
    ),
    SearchTarget(
        doctype="CRM Customer",
        label="Customers",
        icon="users",
        fields=(
            "customer_name",
            "organization",
            "mobile_no",
            "alternative_mobile_no",
            "phone",
            "email",
            "referral_code",
            "pan_card_number",
            "aadhaar_card_number",
        ),
        search_fields=("customer_name", "organization", "referral_code"),
        id_fields=("name", "referral_code"),
        phone_fields=("mobile_no", "alternative_mobile_no", "phone"),
        email_fields=("email",),
        build_title=_customer_title,
        build_subtitle=_customer_subtitle,
        build_route=_customer_route,
        build_meta=lambda doc: {
            "mobile_no": doc.get("mobile_no"),
            "email": doc.get("email"),
            "referral_code": doc.get("referral_code"),
        },
    ),
    SearchTarget(
        doctype="CRM Task",
        label="Tasks",
        icon="check-square",
        fields=(
            "title",
            "status",
            "priority",
            "assigned_to",
            "reference_doctype",
            "reference_docname",
        ),
        search_fields=("title", "reference_docname"),
        id_fields=("name",),
        build_title=_task_title,
        build_subtitle=_task_subtitle,
        build_route=_task_route,
        build_meta=lambda doc: {
            "status": doc.get("status"),
            "priority": doc.get("priority"),
            "assigned_to": doc.get("assigned_to"),
            "reference_doctype": doc.get("reference_doctype"),
            "reference_docname": doc.get("reference_docname"),
        },
    ),
    SearchTarget(
        doctype="FCRM Note",
        label="Notes",
        icon="sticky-note",
        fields=("title", "reference_doctype", "reference_docname", "content"),
        # include the rich-text body so keywords in the note content are searchable
        search_fields=("title", "reference_docname", "content"),
        id_fields=("name", "reference_docname"),
        build_title=_note_title,
        build_subtitle=_note_subtitle,
        build_route=_note_route,
        build_meta=lambda doc: {
            "reference_doctype": doc.get("reference_doctype"),
            "reference_docname": doc.get("reference_docname"),
            "snippet": _clean_snippet(doc.get("content"), 300),
        },
    ),
    SearchTarget(
        doctype="CRM Call Log",
        label="Call Logs",
        icon="phone-call",
        fields=(
            "type",
            "status",
            "from",
            "to",
            "customer",
            "customer_name",
            "employee",
            "medium",
            "telephony_medium",
            "start_time",
            "note",
        ),
        search_fields=("customer_name", "customer", "employee", "note"),
        id_fields=("name",),
        phone_fields=("from", "to", "customer"),
        build_title=_call_log_title,
        build_subtitle=_call_log_subtitle,
        build_route=_call_log_route,
        build_meta=lambda doc: {
            "type": doc.get("type"),
            "status": doc.get("status"),
            "employee": doc.get("employee"),
            "start_time": doc.get("start_time"),
        },
    ),
    SearchTarget(
        doctype="CRM Support Pages",
        label="Support Pages",
        icon="book-open",
        fields=("page_name", "support_link", "description", "is_active"),
        search_fields=("page_name", "description", "support_link"),
        id_fields=("name", "support_link"),
        build_title=_support_page_title,
        build_subtitle=_support_page_subtitle,
        build_route=_support_page_route,
        build_meta=lambda doc: {
            "support_link": doc.get("support_link"),
            "is_active": doc.get("is_active"),
        },
        external=True,
    ),
)


def _filter_targets(doctype: str | None) -> List[SearchTarget]:
    if not doctype:
        return list(SEARCH_TARGETS)
    target_key = doctype.strip().lower()
    return [
        target
        for target in SEARCH_TARGETS
        if target.doctype.lower() == target_key or target.label.lower() == target_key
    ]


def _build_or_filters(target: SearchTarget, ctx: QueryContext) -> List[List[str]]:
    filters: List[List[str]] = []
    seen: set[tuple[str, str, str]] = set()

    def add(field: str, operator: str, value: str) -> None:
        if not field or value is None:
            return
        key = (field, operator, value)
        if key in seen:
            return
        seen.add(key)
        filters.append([field, operator, value])

    for field in target.search_fields:
        for term in ctx.like_terms:
            add(field, "like", term)

    for field in target.id_fields:
        if ctx.raw:
            add(field, "=", ctx.raw)
        if ctx.uppercase and ctx.uppercase != ctx.raw:
            add(field, "=", ctx.uppercase)
        for term in ctx.like_terms:
            add(field, "like", term)

    if ctx.digits and len(ctx.digits) >= 4:
        digits_like = f"%{ctx.digits}%"
        for field in target.phone_fields:
            add(field, "=", ctx.digits)
            add(field, "like", digits_like)

    if ctx.is_email:
        email_like = f"%{ctx.normalized}%"
        for field in target.email_fields:
            add(field, "=", ctx.raw)
            add(field, "=", ctx.normalized)
            add(field, "like", email_like)

    if ctx.is_numeric:
        for field in target.id_fields:
            add(field, "=", ctx.raw)

    if not filters:
        fallback = ctx.like_terms or (f"%{ctx.normalized}%",)
        for term in fallback:
            add("name", "like", term)

    return filters


def _score_doc(
    target: SearchTarget,
    doc: Dict[str, Any],
    ctx: QueryContext,
    now: datetime,
) -> tuple[float, List[Dict[str, Any]], Dict[str, float]]:
    matches: List[Dict[str, Any]] = []
    score = 0.0
    match_weight_total = 0.0
    recency_bonus = 0.0
    recorded: set[str] = set()

    def append_match(
        field: str,
        value: Any,
        weight: float,
        match_type: str,
        tokens: Iterable[str] | None = None,
    ) -> None:
        nonlocal score
        nonlocal match_weight_total
        if value in (None, ""):
            return
        text = str(value).strip()
        if not text:
            return
        key = f"{field}:{text}:{match_type}"
        if key in recorded:
            return
        recorded.add(key)
        matches.append(
            {
                "field": field,
                "label": unscrub(field),
                "value": text,
                "match_type": match_type,
                "tokens": list(tokens) if tokens else None,
                "weight": round(weight, 2),
            }
        )
        score += weight
        match_weight_total += weight

    lower_query = ctx.normalized
    upper_query = ctx.uppercase
    terms = ctx.plain_terms

    def _retain_term(term: str) -> bool:
        if not term:
            return False
        if len(term) >= 3:
            return term not in STOPWORDS
        return any(ch.isdigit() for ch in term)

    token_terms = tuple(filter(_retain_term, terms)) or (lower_query,)

    # Identifier-style fields (docname, client IDs, etc.)
    for field in target.id_fields or ("name",):
        value = doc.get(field)
        if not value:
            continue
        text = str(value).strip()
        if not text:
            continue
        value_lower = text.lower()
        value_upper = text.upper()
        if upper_query and upper_query == value_upper:
            append_match(field, text, 120, "exact")
        elif lower_query and lower_query == value_lower:
            append_match(field, text, 110, "exact")
        elif upper_query and upper_query in value_upper:
            append_match(field, text, 90, "partial")
        else:
            hits = [term for term in token_terms if term in value_lower]
            if hits:
                append_match(field, text, 70 + min(len(hits), 3) * 5, "token", hits)

    # Telephone-style matches
    if ctx.digits and len(ctx.digits) >= 4:
        for field in target.phone_fields:
            value = doc.get(field)
            if not value:
                continue
            digits_value = re.sub(r"\D", "", str(value))
            if not digits_value:
                continue
            if digits_value == ctx.digits:
                append_match(field, value, 115, "phone-exact")
            elif ctx.digits in digits_value:
                append_match(field, value, 86 + min(len(ctx.digits), 6) * 2, "phone-partial")

    # Email-style matches
    if ctx.is_email:
        for field in target.email_fields:
            value = doc.get(field)
            if not value:
                continue
            text_lower = str(value).strip().lower()
            if not text_lower:
                continue
            if text_lower == lower_query:
                append_match(field, value, 112, "email-exact")
            elif lower_query and lower_query in text_lower:
                append_match(field, value, 92, "email-partial")

    # Textual search fields
    for field in target.search_fields:
        if field in target.id_fields:
            continue
        value = doc.get(field)
        if not value:
            continue
        text = str(value).strip()
        if not text:
            continue
        boost_exact = boost_partial = boost_token = 0.0
        if target.doctype == "FCRM Note" and field == "content":
            # Normalize long-form content to a readable snippet and boost its importance
            text = _clean_snippet(text, 240)
            boost_exact = 60.0
            boost_partial = 40.0
            boost_token = 20.0
        value_lower = text.lower()
        if lower_query and lower_query == value_lower:
            append_match(field, text, 88 + boost_exact, "exact")
        elif lower_query and lower_query in value_lower:
            append_match(field, text, 74 + boost_partial, "partial")
        else:
            hits = [term for term in token_terms if term in value_lower]
            if hits:
                append_match(field, text, 60 + min(len(hits), 3) * 4 + boost_token, "token", hits)

    # Title heuristics (if title isn't a stored field)
    if target.build_title:
        title_value = target.build_title(doc)
        if title_value and isinstance(title_value, str):
            title_text = title_value.strip()
            if title_text:
                title_lower = title_text.lower()
                if lower_query and lower_query == title_lower:
                    append_match("title", title_text, 90, "exact")
                elif lower_query and lower_query in title_lower:
                    append_match("title", title_text, 70, "partial")
                else:
                    hits = [term for term in token_terms if term in title_lower]
                    if hits:
                        append_match("title", title_text, 58 + min(len(hits), 3) * 4, "token", hits)

    if not matches:
        return 0.0, [], {"matches": 0.0, "match_bonus": 0.0, "recency_bonus": 0.0}

    modified = doc.get("modified")
    if modified:
        try:
            modified_dt = get_datetime(modified)
            delta = now - modified_dt
            hours = max(0.0, delta.total_seconds() / 3600.0)
            recency_bonus = max(0.0, 24.0 - min(hours, 24.0))
            score += recency_bonus
        except Exception:
            pass

    match_bonus = len(matches) * 2.5
    score += match_bonus

    details = {
        "matches": round(match_weight_total, 2),
        "match_bonus": round(match_bonus, 2),
        "recency_bonus": round(recency_bonus, 2),
    }

    return score, matches, details


def _search_target(
    target: SearchTarget,
    ctx: QueryContext,
    per_limit: int,
    now: datetime,
) -> List[Dict[str, Any]]:
    or_filters = _build_or_filters(target, ctx)
    if not or_filters:
        return []

    filters: Dict[str, Any] = {}
    if target.extra_filters:
        extra = target.extra_filters(ctx) or {}
        filters.update(extra)

    rows = frappe.get_all(
        target.doctype,
        fields=target.fieldset(),
        filters=filters,
        or_filters=or_filters,
        order_by=target.order_by,
        limit=per_limit * 4,
    )

    results: List[Dict[str, Any]] = []
    for row in rows:
        score, matches, details = _score_doc(target, row, ctx, now)
        if score <= 0 or not matches:
            continue
        title = target.build_title(row) if target.build_title else row.get("name")
        subtitle = target.build_subtitle(row) if target.build_subtitle else None
        route = target.build_route(row) if target.build_route else row.get("name")
        meta = target.build_meta(row) if target.build_meta else {}
        results.append(
            {
                "doctype": target.doctype,
                "name": row.get("name"),
                "title": title or row.get("name"),
                "subtitle": subtitle,
                "route": route or "",
                "icon": target.icon,
                "score": round(score, 2),
                "matches": matches,
                "meta": meta or {},
                "external": target.external,
                "score_details": details,
            }
        )

    results.sort(key=lambda item: (-item["score"], (item.get("title") or "").lower()))
    return results[:per_limit]


@frappe.whitelist()
def universal_search(query: str, limit: int = 20, doctype: str | None = None) -> Dict[str, Any]:
    query = (query or "").strip()
    try:
        limit_value = int(limit)
    except (TypeError, ValueError):
        limit_value = 20
    limit_value = max(1, limit_value)

    if not query:
        return {
            "sections": [],
            "metadata": {
                "query": "",
                "normalized_query": "",
                "digits": "",
                "total_results": 0,
                "elapsed_ms": 0,
                "minimum_length": MIN_QUERY_LENGTH,
                "message": "empty_query",
            },
        }

    context = build_query_context(query)
    if (
        len(context.normalized) < MIN_QUERY_LENGTH
        and not context.is_email
        and len(context.digits) < 4
    ):
        return {
            "sections": [],
            "metadata": {
                "query": query,
                "normalized_query": context.normalized,
                "digits": context.digits,
                "total_results": 0,
                "elapsed_ms": 0,
                "minimum_length": MIN_QUERY_LENGTH,
                "message": "query_too_short",
            },
        }

    targets = _filter_targets(doctype)
    if not targets:
        return {
            "sections": [],
            "metadata": {
                "query": query,
                "normalized_query": context.normalized,
                "digits": context.digits,
                "total_results": 0,
                "elapsed_ms": 0,
                "minimum_length": MIN_QUERY_LENGTH,
                "message": "no_targets",
            },
        }

    per_limit = max(3, math.ceil(limit_value / max(len(targets), 1)))
    now = now_datetime()

    sections: List[Dict[str, Any]] = []
    total_results = 0
    timer = time.perf_counter()

    for target in targets:
        records = _search_target(target, context, per_limit, now)
        if not records:
            continue
        sections.append(
            {
                "doctype": target.doctype,
                "label": target.label,
                "icon": target.icon,
                "external": target.external,
                "results": records,
            }
        )
        total_results += len(records)

    elapsed_ms = int((time.perf_counter() - timer) * 1000)

    return {
        "sections": sections,
        "metadata": {
            "query": query,
            "normalized_query": context.normalized,
            "digits": context.digits,
            "total_results": total_results,
            "elapsed_ms": elapsed_ms,
            "minimum_length": MIN_QUERY_LENGTH,
            "targets": [target.doctype for target in targets],
        },
    }
