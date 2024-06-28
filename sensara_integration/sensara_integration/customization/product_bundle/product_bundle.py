from __future__ import unicode_literals
import frappe
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 
import frappe
import datetime
from datetime import datetime

def validate(doc,method=None):
    headers = {
			'content-type':'application/json',
            'x-sms-key': 'caf917de-21f2-4b41-7aa0-c9d5b0ec7095'
		}

    entitlements = []
    body = {
        "action": "PRODUCT_CATALOG_UPDATE",
    }
    from bs4 import BeautifulSoup as bs
    import re
    plan_title = ""
    try:
        soup = bs(doc.description)
        p_tag = soup.find('p')
        plan_title = p_tag.text
    except:
        plan_title = ""
    plans = {
            "plan_id": doc.new_item_code, 
            "plan_title": plan_title, 
            "plan_active_from": datetime.strptime(doc.custom_plan_active_from, "%Y-%m-%d").isoformat(), 
            "plan_active_till": datetime.strptime(doc.custom_plan_active_till, "%Y-%m-%d").isoformat(),
            "plan_type": doc.custom_type, 
        }

    pricings = []
    item_price = frappe.get_doc("Item Price",{"item_code":doc.new_item_code})
    pricings.append(
        {
            "pricing_id": item_price.name,
            "currency": item_price.currency,
            "currency_value": item_price.price_list_rate,
            "validity_type": item_price.custom_validity_type,
            "validity_value": item_price.custom_validity_value,
            "valid_from": item_price.valid_from.isoformat(),
            "valid_till": item_price.valid_upto.isoformat(),
        }
    )

    entitlements = []
    for item in doc.items:
        item_image_url = frappe.db.get_value("File",{
            "attached_to_doctype": "Item",
            "attached_to_name": item.item_code,
            "attached_to_field": "image"
        },['file_url'])
        entitlements.append(
            {
                "entitlement_id": item.item_code,
                "entitlement_title": item.description,
                "entitlement_type": "app",
                "entitlement_image": item_image_url
            }
        )

    plans.update({"pricings":pricings,"entitlements":entitlements})
    plans_list = [plans]


    body.update({"plans":plans_list})
    print("body json= ",json.dumps(body))

    # Make the POST request
    webhook_log = frappe.new_doc("Sensara Integration Request Log")
    webhook_log.request_for = "PRODUCT_CATALOG_UPDATE"
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
    print("\n\n\nResponse >>> ",response)

    webhook_log.insert()