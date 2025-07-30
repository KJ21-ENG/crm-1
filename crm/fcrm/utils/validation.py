import re
import frappe
from frappe import _

def validate_pan_number(pan_number):
    """
    Validate PAN card number format
    - 10 characters long
    - First 5 characters are letters (uppercase)
    - Next 4 characters are numbers
    - Last character is a letter (uppercase)
    """
    if not pan_number:
        return

    pan_pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')
    if not pan_pattern.match(pan_number):
        frappe.throw(
            _("Invalid PAN Card Number. It should be in the format: ABCDE1234F")
        )

def validate_aadhaar_number(aadhaar_number):
    """
    Validate Aadhaar card number format
    - 12 digits
    - No special characters or spaces
    """
    if not aadhaar_number:
        return

    aadhaar_pattern = re.compile(r'^[0-9]{12}$')
    if not aadhaar_pattern.match(aadhaar_number):
        frappe.throw(
            _("Invalid Aadhaar Card Number. It should be a 12-digit number without spaces or special characters")
        )

def validate_identity_documents(doc):
    """
    Validate both PAN and Aadhaar card numbers for a document
    """
    if hasattr(doc, 'pan_card_number'):
        validate_pan_number(doc.pan_card_number)
    if hasattr(doc, 'aadhaar_card_number'):
        validate_aadhaar_number(doc.aadhaar_card_number) 