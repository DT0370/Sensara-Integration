from __future__ import unicode_literals
import frappe
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 
import frappe
import datetime

def after_insert(doc,method=None):
    action = "SUBSCRIPTION_ACTIVATION"
    body, webhook_log = create_subscription_payload(doc,action)
    post_subscription_payload(body, webhook_log)

def on_submit(doc,method=None):
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
            if doc.docstatus == 1:
                serial_batch_bundle = frappe.get_doc("Serial and Batch Bundle",item.serial_and_batch_bundle)

                tv_device_serial_number = serial_batch_bundle.entries[0].serial_no #item.tv_device_serial_number 

    plan.update({"entitlements":entitlements})

    if isinstance(doc.custom_start_timestamp_for_the_plan, datetime.datetime):
        start_timestamp = doc.custom_start_timestamp_for_the_plan.isoformat()
        end_timestamp = doc.custom_end_timestamp_for_the_plan.isoformat()
    if isinstance(doc.custom_start_timestamp_for_the_plan, str):
        start_timestamp = datetime.datetime.strptime(doc.custom_start_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
        end_timestamp = datetime.datetime.strptime(doc.custom_end_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
    
    body = {
            "action": action,
            "phone_number": doc.contact_phone,
            "country_code": doc.custom_country_code,
            "customer_id": doc.customer,
            "start_timestamp": start_timestamp, 
            "end_timestamp": end_timestamp,
            "subscription_id": doc.name,
            "subscription_type": doc.custom_subscription_type,
            "tv_device_serial_number": tv_device_serial_number,
        } 
    body.update({"plan": plan})

    # Make the POST request
    webhook_log = frappe.new_doc("Sensara Integration Request Log")
    webhook_log.request_for = "Subscription Activation"
    webhook_log.reference_document = doc.name
    webhook_log.headers = str(headers)
    webhook_log.data = str(json.dumps(body))
    webhook_log.user = doc.modified_by
    webhook_log.url = sensara_settings.base_url

    return body,webhook_log

def post_subscription_payload(body, webhook_log):
    sensara_settings = frappe.get_doc('Sensara Integration Settings')
    headers = {
            'content-type':'application/json',
            sensara_settings.api_key: sensara_settings.api_secret
        }
    try:
        response = requests.post(sensara_settings.base_url,headers=headers,data=json.dumps(body))
        webhook_log.response = response
        webhook_log.message = str(response.json())

    except HTTPError as http_err:
        webhook_log.error = http_err
        frappe.throw(_("HTTP Error {0}".format(http_err)))

    webhook_log.insert()

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
        webhook_log.message = str(response.json())
    except HTTPError as http_err:
        webhook_log.error = http_err
        frappe.throw(_("HTTP Error {0}".format(http_err)))

    webhook_log.insert()