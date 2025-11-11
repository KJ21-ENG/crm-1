import frappe
from frappe import _

@frappe.whitelist()
def resend_invitation(email):
    """Resend invitation to user"""
    if not email:
        frappe.throw(_("Email is required"))

    # Check if invitation exists and is pending
    invitation = frappe.get_all(
        "CRM Invitation",
        filters={
            "email": email,
            "status": "Pending"
        },
        limit=1
    )

    if not invitation:
        frappe.throw(_("No pending invitation found for this email"))

    # Get the invitation document
    invitation_doc = frappe.get_doc("CRM Invitation", invitation[0].name)
    
    # Reset invitation state
    invitation_doc.email_sent_at = None
    invitation_doc.status = "Pending"
    
    # Generate new key and save
    invitation_doc.key = frappe.generate_hash()[:12]
    invitation_doc.save(ignore_permissions=True)
    
    # Regenerate email with new key
    invitation_doc.invite_via_email()
    
    return {
        "message": _("Invitation resent successfully"),
        "key": invitation_doc.key  # For debugging
    }
