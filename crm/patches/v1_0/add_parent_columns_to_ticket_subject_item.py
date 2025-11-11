import frappe


def execute():
    table = "tabCRM Ticket Subject Item"

    def column_exists(column: str) -> bool:
        try:
            res = frappe.db.sql(
                """
                SELECT 1
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                  AND TABLE_NAME = %s
                  AND COLUMN_NAME = %s
                """,
                (table, column),
            )
            return bool(res)
        except Exception:
            return False

    # Add missing child-table linkage columns
    adds = []
    if not column_exists("parent"):
        adds.append("ADD COLUMN `parent` varchar(140) DEFAULT NULL")
    if not column_exists("parenttype"):
        adds.append("ADD COLUMN `parenttype` varchar(140) DEFAULT NULL")
    if not column_exists("parentfield"):
        adds.append("ADD COLUMN `parentfield` varchar(140) DEFAULT NULL")

    if adds:
        frappe.db.sql(f"ALTER TABLE `{table}` \n  " + ",\n  ".join(adds))

    # Ensure index on parent for efficient lookups
    try:
        frappe.db.sql(f"CREATE INDEX `parent` ON `{table}` (`parent`)")
    except Exception:
        # ignore if exists
        pass



