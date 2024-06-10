from __future__ import unicode_literals
import frappe
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 
import frappe

def on_sumbit(doc,method=None):
    headers = {
			'content-type':'application/json',
            'x-sms-key': 'caf917de-21f2-4b41-7aa0-c9d5b0ec7095'
		}

    plan = {}
    entitlements = []
    tv_device_serial_number = ""
    for packed_item in doc.packed_items:
        entitlements.append({
            "id": packed_item.parent_item,
            "entitlement_id": packed_item.item_code,
            "entitlement_type": "ott",
            "entitlement_title": packed_item.item_name
        })

    product_bundle_list = frappe.get_all("Product Bundle",["new_item_code"],pluck="new_item_code")

    
    for item in doc.items:
        if item.item_code in product_bundle_list:
            plan.update({"plan_id":item.item_code, "id":item.item_name})
        else:
            serial_batch_bundle = frappe.get_doc("Serial and Batch Bundle",item.serial_and_batch_bundle)

            tv_device_serial_number = serial_batch_bundle.entries[0].serial_no #item.tv_device_serial_number 

    plan.update({"entitlements":entitlements})
    body = {
            "action": "SUBSCRIPTION_ACTIVATION",
            "phone_number": doc.contact_phone,
            "country_code": doc.custom_country_code,
            "start_timestamp": doc.custom_start_timestamp_for_the_plan,
            "end_timestamp": doc.custom_start_timestamp_for_the_plan,
            "subscription_id": doc.name,
            "subscription_type": doc.custom_subscription_type,
            "tv_device_serial_number": tv_device_serial_number,
        } 
    body.update({"plan": plan})

    print("body json= ",json.dumps(body))

    # Make the POST request
    try:
        response = requests.post('https://sensara.co/api/v4/subscriber/erpnext_subscription',headers=headers,data=json.dumps(body))
    except HTTPError as http_err:
        frappe.throw(_("HTTP Error {0}".format(http_err)))
    print("\n\n\nResponse >>> ",response)