from __future__ import unicode_literals
import frappe
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 
import frappe
import datetime

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
            plan.update({"plan_id":item.item_code   , "id":item.item_name})
        else:
            serial_batch_bundle = frappe.get_doc("Serial and Batch Bundle",item.serial_and_batch_bundle)

            tv_device_serial_number = serial_batch_bundle.entries[0].serial_no #item.tv_device_serial_number 
    print("\n\n\n>>>>>>>>",type(doc.custom_start_timestamp_for_the_plan.isoformat()))
    # start_timestamp_for_the_plan = doc.custom_start_timestamp_for_the_plan.strftime("%Y-%m-%d %H:%M:%S") 
    # end_timestamp_for_the_plan = doc.custom_end_timestamp_for_the_plan.strftime("%Y-%m-%d %H:%M:%S") 

    plan.update({"entitlements":entitlements})
    body = {
            "action": "SUBSCRIPTION_ACTIVATION",
            "phone_number": doc.contact_phone,
            "country_code": doc.custom_country_code,
            "start_timestamp": doc.custom_start_timestamp_for_the_plan.isoformat(), 
            "end_timestamp": doc.custom_end_timestamp_for_the_plan.isoformat(),
            "subscription_id": doc.name,
            "subscription_type": doc.custom_subscription_type,
            "tv_device_serial_number": tv_device_serial_number,
        } 
    body.update({"plan": plan})

    print("body json= ",json.dumps(body))

    # Make the POST request
    webhook_log = frappe.new_doc("Sensara Integration Request Log")
    webhook_log.request_for = "Subscription Activation"
    webhook_log.reference_document = doc.name
    webhook_log.headers = str(headers)
    webhook_log.data = str(json.dumps(body))
    webhook_log.user = doc.modified_by
    webhook_log.url = 'https://sensara.co/api/v4/subscriber/erpnext_subscription'
    try:
        response = requests.post('https://sensara.co/api/v4/subscriber/erpnext_subscription',headers=headers,data=json.dumps(body))
        webhook_log.response = response
    except HTTPError as http_err:
        webhook_log.error = http_err
        frappe.throw(_("HTTP Error {0}".format(http_err)))
    print("\n\n\nResponse >>> ",type(response ))

    # create a webhook log
    # webhook_log = frappe.new_doc("Webhook Request Log")
    # webhook_log.webhook = "Subscription Activation"
    # webhook_log.reference_document = doc.name
    # webhook_log.headers = headers
    # webhook_log.data = json.dumps(body)
    # webhook_log.user = doc.modified_by
    # webhook_log.url = 'https://sensara.co/api/v4/subscriber/erpnext_subscription'
    # webhook_log.response = response
    webhook_log.insert()