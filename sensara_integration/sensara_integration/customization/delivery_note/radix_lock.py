import requests
import frappe
from datetime import datetime, timedelta

# Function to get JWT token
def get_jwt_token():
    try:
        jwt_url = "https://visomdm.com/rest/login/getjwttoken"
        payload = {
            "username": "admin@dorplay-dev",
            "password": "Pass1234!"
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(jwt_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        token = response.json().get("data", {}).get("token")
        if not token:
            frappe.throw("Failed to retrieve JWT token.")
        return token
    except requests.RequestException as e:
        frappe.throw(f"Error getting JWT token: {str(e)}")

# Function to call the lock device API
def lock_device(device_id):
    try:
        lock_url = "https://visomdm.com/rest/command/send/sendcommanddatatomany"
        token = get_jwt_token()

        payload = {
            "commandData": {
                "@class": "com.viso.entities.commands.CommandRemoteExec",
                "remoteExecItem": {
                    "repositoryItemId": "67598407eb6cd12afc9a63d5",  # Replace with your lock ID
                    "@class": "com.viso.entities.RemoteExecItem"
                }
            },
            "deviceIds": [device_id]
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(lock_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        frappe.logger().info(f"Lock API called successfully for Device ID: {device_id}")
    except requests.RequestException as e:
        frappe.logger().error(f"Error while calling Lock API for Device ID {device_id}: {str(e)}")
        frappe.throw(f"Failed to lock device ID {device_id}: {str(e)}")

# Function to check if the end timestamp is within 7 days from today
def is_within_seven_days(subscription_end_date):
    if not subscription_end_date:
        frappe.logger().warning("Subscription end date is missing. Skipping entry.")
        return False

    try:
        # Convert subscription_end_date to a datetime object if it is a string
        if isinstance(subscription_end_date, str):
            subscription_end_date = datetime.strptime(subscription_end_date, "%Y-%m-%d %H:%M:%S")

        today = datetime.now()
        return subscription_end_date <= today - timedelta(days=7)
    except ValueError as e:
        frappe.logger().error(f"Error parsing subscription end date {subscription_end_date}: {str(e)}")
        return False

# Main Event Function
def radix_tv_locking(doc, method):
    try:
        # Fetch entries with relevant filters
        website_entries = frappe.get_all(
            "Website Data",
            filters={"subscription_end_date": ["<=", (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")]},
            fields=["name", "locked", "serial_number", "subscription_end_date"]
        )

        for entry in website_entries:
            if entry.locked:
                frappe.msgprint(f"Entry {entry.name} is already locked. Skipping...")
                continue

            if is_within_seven_days(entry.subscription_end_date):
                device_id = entry.serial_number
                if device_id:
                    lock_device(device_id)
                    # Mark the entry as locked
                    frappe.db.set_value("Website Data", entry.name, "locked", True)
                    frappe.db.commit()  # Ensure changes are saved
                    frappe.msgprint(f"Locking API called successfully for Device ID: {device_id} and entry locked.")
                else:
                    frappe.msgprint(f"No Serial Number (Device ID) found for entry: {entry.name}")
    except Exception as e:
        frappe.logger().error(f"Error in radix_tv_locking: {str(e)}")
        frappe.throw(f"An error occurred during the locking process: {str(e)}")
