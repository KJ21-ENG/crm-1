import frappe

def force_add_documentation_item():
	crm_settings = frappe.get_doc("FCRM Settings")
	
	# Check if it already exists
	exists = False
	for item in crm_settings.dropdown_items:
		if item.name1 == "documentation":
			exists = True
			break
			
	if not exists:
		print("Adding documentation dropdown item...")
		crm_settings.append("dropdown_items", {
			"name1": "documentation",
			"label": "Documentation",
			"type": "Route",
			"icon": "book-open",
			"route": "#",
			"is_standard": 1
		})
		
		# Move it before about/logout
		items = crm_settings.dropdown_items
		doc_item = items[-1]
		
		# Find about idx
		about_idx = -1
		for i, item in enumerate(items[:-1]):
			if item.name1 == "about":
				about_idx = i
				break
				
		if about_idx != -1:
			items.insert(about_idx, items.pop())
			# fix idx
			for i, item in enumerate(items):
				item.idx = i + 1
		
		crm_settings.save(ignore_permissions=True)
		frappe.db.commit()
		print("Successfully added Documentation item to FCRM Settings.")
	else:
		print("Documentation item already exists in FCRM Settings.")
