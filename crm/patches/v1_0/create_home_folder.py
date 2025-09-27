import frappe

def execute():
	"""Create the Home folder if it doesn't exist"""

	# Check if Home folder already exists
	if frappe.db.exists("File", {"file_name": "Home", "is_folder": 1, "is_home_folder": 1}):
		return

	# Create the Home folder
	home_folder = frappe.get_doc({
		"doctype": "File",
		"file_name": "Home",
		"is_folder": 1,
		"is_home_folder": 1,
		"folder": "",
		"is_private": 0
	})

	home_folder.insert(ignore_permissions=True)
	frappe.db.commit()

	print("Home folder created successfully")
