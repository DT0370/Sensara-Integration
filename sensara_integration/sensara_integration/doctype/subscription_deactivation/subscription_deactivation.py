# Copyright (c) 2024, dteam0370@gmail.com and contributors
# For license information, please see license.txt

# import frappe
# from __future__ import unicode_literals
from frappe.model.document import Document
import frappe
from frappe import _
import requests
import json
from requests.exceptions import HTTPError, RequestException
import datetime


class SubscriptionDeactivation(Document):
    def on_submit(self):
        sensara_settings = frappe.get_doc('Sensara Integration Settings')

        headers = {
            'content-type': 'application/json',
            sensara_settings.api_key: sensara_settings.api_secret
        }

        # Safely handle preview_subscription_id
        preview_subscription_id = getattr(self, "preview_subscription_id", None)

        body = {
            "action": self.action,
            "phone_number": self.phone_number,
            "country_code": "+91",
            "subscription_id": self.subscription_id if self.subscription_id else preview_subscription_id,
        }

        # Create a webhook log
        webhook_log = frappe.new_doc("Sensara Integration Request Log")
        webhook_log.request_for = self.action
        webhook_log.reference_document = self.name
        webhook_log.headers = json.dumps(headers)
        webhook_log.data = json.dumps(body)
        webhook_log.user = self.modified_by
        webhook_log.url = sensara_settings.base_url

        try:
            # Make the POST request
            response = requests.post(sensara_settings.base_url, headers=headers, data=json.dumps(body))

            # Set response and message
            webhook_log.response = response.text
            try:
                webhook_log.message = str(response.json())
            except ValueError:
                webhook_log.message = "Unable to parse response as JSON"

        except HTTPError as http_err:
            webhook_log.error = f"HTTP Error: {http_err}"
            frappe.log_error(message=str(http_err), title="HTTP Error in Subscription Deactivation")
        except RequestException as req_err:
            webhook_log.error = f"Request Error: {req_err}"
            frappe.log_error(message=str(req_err), title="Request Error in Subscription Deactivation")
        except Exception as ex:
            webhook_log.error = f"Unexpected Error: {ex}"
            frappe.log_error(message=str(ex), title="Unexpected Error in Subscription Deactivation")
        finally:
            # Ensure the webhook log is saved
            webhook_log.insert(ignore_permissions=True)
            frappe.db.commit()

