import frappe
from frappe.utils import nowdate, getdate

def update_dates():
    """
    Update the start_date and status for coupons based on the provided conditions.
    """
    documents = frappe.get_all(
        "Dorplay Activation Codes",  # Replace with your actual doctype name
        filters={"start_date": ["is", "set"]},  # Ensure start_date is present
        fields=["name", "start_date", "updated_end_date", "status", "subscription_end_date", "end_date", "previous_status"]
    )

    for doc_data in documents:
        doc = frappe.get_doc("Dorplay Activation Codes", doc_data.name)
        
        # Fetch dates and status
        today = getdate(nowdate())
        start_date = getdate(doc.start_date)
        updated_end_date = getdate(doc.updated_end_date) if doc.updated_end_date else None
        subscription_end_date = getdate(doc.subscription_end_date) if doc.end_date else None
        previous_status = getattr(doc, "previous_status", None)  # Fix here

        # Condition 4.1: If the status is "In Use" and was "Saleable" before, skip this coupon code
        if doc.status == "In Use" and previous_status == "Saleable":
            # print(f"Coupon {doc.name} was 'Saleable' before and is now 'In Use'. Skipping updates.")
            continue

        # Condition 4.2: If the status is "In Use" but was "Non-Saleable" and `updated_end_date` is in the past
        if doc.status == "In Use" and previous_status == "Non-Saleable" and updated_end_date and updated_end_date < today:
            # print(f"Coupon {doc.name} status is 'In Use', was 'Non-Saleable', and `updated_end_date` is in the past. Updating `start_date` to today's date.")
            # doc.start_date = nowdate()  # Update `start_date` to today's date
            # doc.save()
            # frappe.db.commit()
            continue

        # Condition 1: If `updated_end_date` is in the past, set status to "Non-Saleable"
        if updated_end_date and updated_end_date < today:
            # print(f"Coupon {doc.name} has `updated_end_date` in the past ({updated_end_date}). Setting status to 'Non-Saleable'.")
            doc.status = "Non-Saleable"

        # Condition 2: If `updated_end_date` is ahead of today, set status to "Saleable"
        elif updated_end_date and updated_end_date >= today:
            # print(f"Coupon {doc.name} has `updated_end_date` ahead of today ({updated_end_date}). Setting status to 'Saleable'.")
            doc.status = "Saleable"

        # Condition 5: If `end_date` is in the past, set status to "Invalid"
        if subscription_end_date and subscription_end_date < today:
            # print(f"Coupon {doc.name} has `end_date` in the past ({subscription_end_date}). Setting status to 'Invalid'.")
            doc.status = "Invalid"

        # Save the document and commit the changes
        doc.save()
        frappe.db.commit()
