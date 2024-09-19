# Copyright (c) 2024, dteam0370@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
import re
import requests, json
from requests.exceptions import HTTPError 


class DorplaySubscription(Document):
	def on_submit(self):
		body, webhook_log = self.create_dorplay_subscription_payload()
		post_subscription_payload(body, webhook_log)

	def create_dorplay_subscription_payload(self):
		sensara_settings = frappe.get_doc('Sensara Integration Settings')
		headers = {
			'content-type':'application/json',
			sensara_settings.api_key: sensara_settings.api_secret
		}

		plan = {}
		entitlements = []
		tv_device_serial_number = ""

		product_bundle_list = frappe.get_all("Product Bundle",["new_item_code"],pluck="new_item_code")
		plan_name = frappe.get_value("Item",self.plan,['item_name'])
		plan.update({"plan_id":self.plan, "id":plan_name})
		pdt_bundle = frappe.get_doc("Product Bundle",self.plan)
		for item in pdt_bundle.items:
			item_name = frappe.get_value("Item",item.item_code,['item_name'])
			entitlements.append({
				"id": plan_name,
				"entitlement_id": item.item_code,
				"entitlement_type": "ott",
				"entitlement_title": item_name
			})

		plan.update({"entitlements":entitlements})

		if isinstance(self.start_timestamp_for_the_plan, datetime.datetime):
			start_timestamp = self.start_timestamp_for_the_plan.isoformat()
			end_timestamp = self.start_timestamp_for_the_plan.isoformat()
		if isinstance(self.start_timestamp_for_the_plan, str):
			start_timestamp = datetime.datetime.strptime(self.start_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
			end_timestamp = datetime.datetime.strptime(self.end_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()

		body = {
			"action": "SUBSCRIPTION_ACTIVATION",
			"phone_number": self.phone_number,
			"country_code": self.country_code,
			"customer_id": self.customer,
			"start_timestamp": start_timestamp, 
			"end_timestamp": end_timestamp,
			"subscription_id": self.subscription_id,
			"subscription_type": "Non-TV",
			"tv_device_serial_number": None,
			"tv_model": None,
			"activation_status": None
			} 
		body.update({"plan": plan})

		# Make the POST request
		webhook_log = frappe.new_doc("Sensara Integration Request Log")
		webhook_log.request_for = "Dorplay Subscription Activation"
		webhook_log.reference_document = self.name
		webhook_log.headers = str(headers)
		webhook_log.data = str(json.dumps(body))
		webhook_log.user = self.modified_by
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

	webhook_log.insert(ignore_permissions=True)