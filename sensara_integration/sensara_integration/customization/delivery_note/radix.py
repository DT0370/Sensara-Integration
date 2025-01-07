import requests
import frappe

# Function to get JWT token
def get_jwt_token():
    try:
        jwt_url = "https://visomdm.com/rest/login/getjwttoken"
        payload = {
            # "username": "admin@dorplay-dev", --dev
            # "password": "Pass1234!" --dev
			"username": "admin@dorplay",
            "password": "We1c0me@"
        }
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(jwt_url, json=payload, headers=headers)
        
        if response.status_code == 200:
            # token = response.json().get("token")
            token = response.json().get("data", {}).get("token")
            if not token:
                frappe.throw("Failed to retrieve JWT token.")
            return token
        else:
            frappe.throw(f"Error getting JWT token: {response.status_code}, {response.text}")
    except Exception as e:
        frappe.throw(f"An error occurred while getting JWT token: {str(e)}")

# Function to call the lock device API
def lock_device(device_id):
    try:
        lock_url = "https://visomdm.com/rest/command/send/sendcommanddatatomany"
        token = get_jwt_token()

        payload = {
            "commandData": {
                "@class": "com.viso.entities.commands.CommandRemoteExec",
                "remoteExecItem": {
                    # "repositoryItemId": "6759841f40d51015bb163fef",  # Replace with your dev lock ID
					"repositoryItemId": "66cb4b265fd42015c0cb255e",  # Replace with your dev lock ID
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
        
        if response.status_code == 200:
            frappe.logger().info(f"Lock API called successfully for Device ID: {device_id}")
        else:
            frappe.logger().error(
                f"Failed to call Lock API for Device ID: {device_id}. "
                f"Status: {response.status_code}, Response: {response.text}"
            )
            frappe.throw(
                f"Error while calling Lock API: {response.text}",
                title="API Error"
            )
    except Exception as e:
        frappe.throw(f"An error occurred while calling Lock API: {str(e)}")

# Function to get serial number (device_id) from Delivery Note
def get_serial_number(delivery_note_name):
    serial_number = None

    if not delivery_note_name:
        frappe.throw("Delivery Note name is required.")

    # Fetch the Delivery Note document
    try:
        delivery_note = frappe.get_doc("Delivery Note", delivery_note_name)
    except frappe.DoesNotExistError:
        frappe.throw(f"Delivery Note {delivery_note_name} does not exist.")

    # Iterate through the items in the Delivery Note
    if delivery_note.items:
        for item in delivery_note.items:
            # Check if the item is a non-stock item
            is_stock_item = frappe.db.get_value("Item", item.item_code, "is_stock_item")
            if is_stock_item:  # Process only non-stock items
                # Check if serial_and_batch_bundle exists
                if item.serial_and_batch_bundle:
                    try:
                        # Fetch the Serial and Batch Bundle document
                        bundle_doc = frappe.get_doc("Serial and Batch Bundle", item.serial_and_batch_bundle)
                    except frappe.DoesNotExistError:
                        frappe.throw(f"Serial and Batch Bundle {item.serial_and_batch_bundle} does not exist.")

                    # Iterate through the entries in the bundle
                    for entry in bundle_doc.entries:
                        # Extract the serial_no field
                        serial_number = entry.get("serial_no")
                        if serial_number:
                            break
            if serial_number:
                break

    return serial_number

# Main Event Function
@frappe.whitelist(allow_guest=True)
def radix_tv_locking(doc, method):
    if doc.is_renewal:
        # Get the parent delivery note
        delivery_note_name = doc.get("parent_delivery_note")
        if delivery_note_name:
            # Get the serial number from the delivery note
            device_id = get_serial_number(delivery_note_name)
            if device_id:
                # Call the locking API with the device ID
                lock_device(device_id)
                frappe.msgprint(f"Locking API called successfully for Device ID: {device_id}")
            else:
                frappe.msgprint("No Serial Number (Device ID) found for non-stock items in the Delivery Note.")
        else:
            frappe.msgprint("Parent Delivery Note is missing.")
