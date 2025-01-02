import frappe
from frappe.utils import add_days, nowdate, getdate

def update_dates():
    """
    Update the end_date, status, and handle subscription_end_date for all documents with a start_date set.
    """
    documents = frappe.get_all(
        "Dorplay Activation Codes",  # Replace with your actual doctype name
        filters={"start_date": ["is", "set"]},  # Ensure start_date is present
        fields=["name", "start_date", "updated_end_date", "status", "subscription_end_date"]
    )

    for doc_data in documents:
        doc = frappe.get_doc("Dorplay Activation Codes", doc_data.name)
        print(doc, "doc==============18")
        
        start_date = doc.start_date
        print(start_date, "start_date=============22")
        
        # Calculate the updated end date as one day after the start date
        end_date = add_days(start_date, 1)
        print(end_date, "end_date================24")
        
        doc.updated_end_date = end_date

        # Get today's date for comparison
        today = getdate(nowdate())
        
        # Check if updated_end_date has passed
        if doc.updated_end_date <= today:
            print("Updated end date passed, setting status to Non-Saleable")
            doc.status = "Non-Saleable"
        
        # Check if subscription_end_date has passed
        if doc.subscription_end_date and getdate(doc.subscription_end_date) <= today:
            print("Subscription end date passed, setting status to Invalid")
            doc.status = "Invalid"

        # Save the document and commit the changes
        doc.save()
        frappe.db.commit()

