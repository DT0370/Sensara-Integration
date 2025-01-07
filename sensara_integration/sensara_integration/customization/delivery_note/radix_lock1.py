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
def lock_device(doc, method):
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
            "deviceIds": [doc.serial_number]
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        response = requests.post(lock_url, json=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        response_data = response.json()
        if response_data.get("result") == "SUCCESS":
            # Update the locked field in Website Data doctype
            website_data = frappe.get_doc("Website Data", {"subscription_id": doc.subscription_id})
            if website_data:
                website_data.locked = 1
                website_data.save(ignore_permissions=True)
                frappe.logger().info(f"Locked field updated to 1 for subscription ID: {doc.subscription_id}")

            # Submit the document after successful API call and field update
            doc.submit()

        frappe.logger().info(f"Lock API called successfully for Device ID: {doc.serial_number}")
        doc.save()
        doc.submit()
        
    except requests.RequestException as e:
        frappe.logger().error(f"Error while calling Lock API for Device ID {doc.serial_number}: {str(e)}")
        frappe.throw(f"Failed to lock device ID {doc.serial_number}: {str(e)}")

