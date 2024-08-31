# Copyright (c) 2024, dteam0370@gmail.com and contributors
# For license information, please see license.txt

# import frappe
# from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
import re
import requests, json
from requests.exceptions import HTTPError 
import frappe
import datetime


class SubscriptionDeactivation(Document):
	
	def on_submit(self):
    	sensara_settings = frappe.get_doc('Sensara Integration Settings')

		headers = {
				'content-type':'application/json',
            	sensara_settings.api_key: sensara_settings.api_secret
				
			}
		body = {
			"action": self.action,
			"phone_number": self.phone_number,
			"country_code": "+91",
			"subscription_id": self.subscription_id
		}

		webhook_log = frappe.new_doc("Sensara Integration Request Log")
		webhook_log.request_for = self.action
		webhook_log.reference_document = self.name
		webhook_log.headers = str(headers)
		webhook_log.data = str(json.dumps(body))
		webhook_log.user = self.modified_by
		webhook_log.url = sensara_settings.base_url

		try:
			response = requests.post(sensara_settings.base_url,headers=headers,data=json.dumps(body))
			webhook_log.response = response
			webhook_log.message = str(response.json())

		except HTTPError as http_err:
			webhook_log.error = http_err
			# frappe.throw(_("HTTP Error {0}".format(http_err)))
		webhook_log.insert()
