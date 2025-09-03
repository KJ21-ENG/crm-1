import frappe
import os
from datetime import datetime, timezone



@frappe.whitelist()
def create_email_account(data):
	service = data.get("service")
	service_config = email_service_config.get(service)
	if not service_config:
		return "Service not supported"

	try:
		email_doc = frappe.get_doc(
			{
				"doctype": "Email Account",
				"email_id": data.get("email_id"),
				"email_account_name": data.get("email_account_name"),
				"service": service,
				"enable_incoming": data.get("enable_incoming"),
				"enable_outgoing": data.get("enable_outgoing"),
				"default_incoming": data.get("default_incoming"),
				"default_outgoing": data.get("default_outgoing"),
				"email_sync_option": "ALL",
				"initial_sync_count": 100,
				"create_contact": 1,
				"track_email_status": 1,
				"use_tls": 1,
				"use_imap": 1,
				"smtp_port": 587,
				**service_config,
			}
		)
		if service == "Frappe Mail":
			email_doc.api_key = data.get("api_key")
			email_doc.api_secret = data.get("api_secret")
			email_doc.frappe_mail_site = data.get("frappe_mail_site")
			email_doc.append_to = "CRM Lead"
		else:
			email_doc.append("imap_folder", {"append_to": "CRM Lead", "folder_name": "INBOX"})
			email_doc.password = data.get("password")
			# validate whether the credentials are correct
			email_doc.get_incoming_server()

		# if correct credentials, save the email account
		email_doc.save()
	except Exception as e:
		frappe.throw(str(e))


email_service_config = {
	"Frappe Mail": {
		"domain": None,
		"password": None,
		"awaiting_password": 0,
		"ascii_encode_password": 0,
		"login_id_is_different": 0,
		"login_id": None,
		"use_imap": 0,
		"use_ssl": 0,
		"validate_ssl_certificate": 0,
		"use_starttls": 0,
		"email_server": None,
		"incoming_port": 0,
		"always_use_account_email_id_as_sender": 1,
		"use_tls": 0,
		"use_ssl_for_outgoing": 0,
		"smtp_server": None,
		"smtp_port": None,
		"no_smtp_authentication": 0,
	},
	"GMail": {
		"email_server": "imap.gmail.com",
		"use_ssl": 1,
		"smtp_server": "smtp.gmail.com",
	},
	"Outlook": {
		"email_server": "imap-mail.outlook.com",
		"use_ssl": 1,
		"smtp_server": "smtp-mail.outlook.com",
	},
	"Sendgrid": {
		"smtp_server": "smtp.sendgrid.net",
		"smtp_port": 587,
	},
	"SparkPost": {
		"smtp_server": "smtp.sparkpostmail.com",
	},
	"Yahoo": {
		"email_server": "imap.mail.yahoo.com",
		"use_ssl": 1,
		"smtp_server": "smtp.mail.yahoo.com",
		"smtp_port": 587,
	},
	"Yandex": {
		"email_server": "imap.yandex.com",
		"use_ssl": 1,
		"smtp_server": "smtp.yandex.com",
		"smtp_port": 587,
	},
}


@frappe.whitelist()
def get_default_referral_code():
	"""Get default referral code from FCRM Settings"""
	try:
		fcrm_settings = frappe.get_single("FCRM Settings")
		if fcrm_settings and fcrm_settings.default_referral_code:
			return {
				"success": True,
				"default_referral_code": fcrm_settings.default_referral_code
			}
		else:
			return {
				"success": False,
				"message": "Default referral code not configured"
			}
	except Exception as e:
		frappe.log_error(f"Error getting default referral code: {str(e)}")
		return {
			"success": False,
			"message": "Error retrieving default referral code",
			"error": str(e)
		}


@frappe.whitelist()
def get_backup_status(max_items: int = 60):
	"""Return backup status and recent files for the current site.

	- Detects the current site via Frappe context and inspects
	  sites/<site>/private/backups
	- Returns whether a database backup exists for today
	- Returns recent backup files (db/public/private/site_config) sorted by mtime desc

	Args:
		max_items: Maximum number of files to return

	Returns:
		Dict with keys: site, backup_dir, today_backup_exists, latest, files
	"""

	try:
		# Resolve current site and backup directory
		site = frappe.local.site
		backup_dir = frappe.get_site_path('private', 'backups')

		if not os.path.isdir(backup_dir):
			return {
				"site": site,
				"backup_dir": backup_dir,
				"today_backup_exists": False,
				"latest": {},
				"files": [],
			}

		# Collect files and metadata (only gz archives)
		entries = []
		for fname in sorted(os.listdir(backup_dir)):
			fpath = os.path.join(backup_dir, fname)
			if not os.path.isfile(fpath):
				continue
			# Only show compressed files (.gz/.tgz/.tar.gz)
			lower_fname = fname.lower()
			if not (
				lower_fname.endswith('.gz')
				or lower_fname.endswith('.tgz')
				or lower_fname.endswith('.tar.gz')
			):
				continue

			stat = os.stat(fpath)
			modified_ts = stat.st_mtime
			modified = datetime.fromtimestamp(modified_ts, tz=timezone.utc)

			# Infer backup type from filename
			lower = fname.lower()
			if 'database.sql.gz' in lower or lower.endswith('.sql.gz'):
				btype = 'database'
			elif 'private-files' in lower:
				btype = 'private_files'
			elif 'public-files' in lower:
				btype = 'public_files'
			elif 'site_config_backup.json' in lower:
				btype = 'site_config'
			else:
				btype = 'archive'

			entries.append(
				{
					"name": fname,
					"type": btype,
					"size": stat.st_size,
					"modified": modified.isoformat(),
				}
			)

		# Sort newest-first
		entries.sort(key=lambda x: x["modified"], reverse=True)
		entries = entries[: int(max_items or 60)]

		# Determine if a database backup exists today (server local date)
		today = datetime.now(timezone.utc).date()
		today_backup_exists = any(
			item["type"] == "database"
			and datetime.fromisoformat(item["modified"]).date() == today
			for item in entries
		)

		# Latest by type
		latest = {}
		for item in entries:
			latest.setdefault(item["type"], item)

		return {
			"site": site,
			"backup_dir": backup_dir,
			"today_backup_exists": bool(today_backup_exists),
			"latest": latest,
			"files": entries,
		}

	except Exception as e:
		frappe.log_error(f"Error reading backup status: {str(e)}")
		return {
			"site": frappe.local.site if getattr(frappe.local, 'site', None) else None,
			"error": str(e),
			"today_backup_exists": False,
			"latest": {},
			"files": [],
		}



@frappe.whitelist()
def download_backup(filename: str):
    """Securely serve a backup file from the site's private/backups directory.

    Call via: /api/method/crm.api.settings.download_backup?filename=<name>
    """
    import mimetypes

    try:
        if not filename:
            frappe.throw("filename is required")

        backup_dir = frappe.get_site_path('private', 'backups')
        # Prevent path traversal
        requested = os.path.normpath(os.path.join(backup_dir, filename))
        if not requested.startswith(os.path.normpath(backup_dir) + os.sep) and requested != os.path.normpath(backup_dir):
            frappe.throw("Invalid filename")

        if not os.path.exists(requested) or not os.path.isfile(requested):
            frappe.throw("File not found")

        # Guess mime
        mime_type, _ = mimetypes.guess_type(requested)
        if not mime_type:
            mime_type = 'application/octet-stream'

        with open(requested, 'rb') as f:
            content = f.read()

        frappe.response.filename = os.path.basename(requested)
        frappe.response.filecontent = content
        frappe.response.type = 'download'
        frappe.response.headers = {
            'Content-Type': mime_type,
        }

    except Exception as e:
        frappe.log_error(f"Error serving backup file {filename}: {str(e)}")
        frappe.throw(str(e))
