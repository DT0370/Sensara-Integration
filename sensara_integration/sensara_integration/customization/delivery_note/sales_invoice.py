from __future__ import unicode_literals
import frappe
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 
import frappe
import datetime


def on_submit(doc,method=None):
    if doc.is_return == 0 and doc.is_renewal == 1:
        action = "SUBSCRIPTION_UPDATE"
        body, webhook_log = create_subscription_payload(doc,action)
        put_subscription_payload(body, webhook_log)

def create_subscription_payload(doc,action):
    sensara_settings = frappe.get_doc('Sensara Integration Settings')
    headers = {
			'content-type':'application/json',
            sensara_settings.api_key: sensara_settings.api_secret
		}
    

    plan = {}
    
    tv_device_serial_number = ""

    product_bundle_list = frappe.get_all("Product Bundle", ["new_item_code"], pluck="new_item_code")

    # Initialize the entitlements list
    entitlements = []

    # Loop through the items in the Sales Invoice
    for item in doc.items:
        plan.update({"plan_id": item.item_code, "id": item.item_code})
        if item.item_code in product_bundle_list:
            product_details = frappe.get_doc("Product Bundle", item.item_code)
            for i in product_details.items:
                entitlements.append({
                    "id": item.item_code,  # ID from the Sales Invoice item
                    "entitlement_id": i.item_code,  # Assuming a field like 'product_code' exists in Product
                    "entitlement_type": "ott",
                    "entitlement_title": i.item_code  # Assuming 'product_name' exists in Product
                })
        
    if doc.parent_delivery_note:
        delivery_note = frappe.get_doc("Delivery Note", doc.parent_delivery_note)
        for dn_item in delivery_note.items:
            item_doc = frappe.get_doc("Item", dn_item.item_code)
            if item_doc.is_stock_item:
                serial_number = dn_item.serial_no  # Assuming 'serial_no' is the correct field in Delivery Note items
                print("-------------------------------------------------")
                print("Serial Number: ",serial_number)
                print("-------------------------------------------------")
                plan.update({"tv_device_serial_number": serial_number})
                break

    # Update the plan with entitlements
    plan.update({"entitlements": entitlements})

    if isinstance(doc.custom_start_timestamp_for_the_plan, datetime.datetime):
        start_timestamp = doc.custom_start_timestamp_for_the_plan.isoformat()
        end_timestamp = doc.custom_end_timestamp_for_the_plan.isoformat()
    if isinstance(doc.custom_start_timestamp_for_the_plan, str):
        try:
            start_timestamp = datetime.datetime.strptime(doc.custom_start_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
            end_timestamp = datetime.datetime.strptime(doc.custom_end_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
        except Exception as e:
            start_timestamp = datetime.datetime.strptime(doc.custom_start_timestamp_for_the_plan, "%Y-%m-%d").isoformat()
            end_timestamp = datetime.datetime.strptime(doc.custom_end_timestamp_for_the_plan, "%Y-%m-%d").isoformat()
    delivery_note_number = frappe.get_doc("Delivery Note", doc.custom_parent_delivery_note)
	body = {
            "action": action,
            "phone_number": delivery_note_number.contact_mobile,
            "country_code": doc.custom_country_code,
            "customer_id": doc.customer,
            "start_timestamp": str(start_timestamp) + "Z", 
            "end_timestamp": str(end_timestamp) + "Z",
            "subscription_id": doc.parent_delivery_note,
            "subscription_type": doc.custom_subscription_type,
            "tv_device_serial_number": plan["tv_device_serial_number"]
        } 
    body.update({"plan": plan})

    # Make the POST request
    webhook_log = frappe.new_doc("Sensara Integration Request Log")
    webhook_log.request_for = "Subscription Update"
    webhook_log.reference_document = doc.name
    webhook_log.headers = str(headers)
    webhook_log.data = str(json.dumps(body))
    webhook_log.user = doc.modified_by
    webhook_log.url = sensara_settings.base_url

    return body,webhook_log


def put_subscription_payload(body, webhook_log):

    webhook_log.request_for = "Subscription Update"    
    sensara_settings = frappe.get_doc('Sensara Integration Settings')
    headers = {
            'content-type':'application/json',
            sensara_settings.api_key: sensara_settings.api_secret
        }

    try:
        response = requests.post(sensara_settings.base_url,headers=headers,data=json.dumps(body))
        webhook_log.response = response
        try:
            webhook_log.message = str(response.json())
        except Exception as e:
            print(e)

    except HTTPError as http_err:
        webhook_log.error = http_err
        frappe.throw(_("HTTP Error {0}".format(http_err)))

    webhook_log.insert()
