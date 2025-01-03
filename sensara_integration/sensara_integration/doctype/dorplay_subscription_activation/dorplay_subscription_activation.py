# Copyright (c) 2024, dteam0370@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import datetime
import json
import requests
from requests.exceptions import HTTPError


class DorplaySubscriptionActivation(Document):
    def after_insert(self):
        body, webhook_log = self.create_dorplay_subscription_payload()
        post_subscription_payload(body, webhook_log)

    def create_dorplay_subscription_payload(self):
        # Fetch Sensara Integration Settings
        sensara_settings = frappe.get_doc('Sensara Integration Settings')
        headers = {
            'content-type': 'application/json',
            sensara_settings.dorplay_api_key: sensara_settings.dorplay_api_secret
        }

        # Initialize variables
        plan = {}
        entitlements = []

        # Get product bundle details
        product_bundle_list = frappe.get_all("Product Bundle", ["new_item_code"], pluck="new_item_code")
        plan_name = frappe.get_value("Item", self.plan, ['item_name'])
        plan.update({"plan_id": self.plan, "id": plan_name})

        # Add entitlements for the plan
        pdt_bundle = frappe.get_doc("Product Bundle", self.plan)
        for item in pdt_bundle.items:
            item_name = frappe.get_value("Item", item.item_code, ['item_name'])
            entitlements.append({
                "id": plan_name,
                "entitlement_id": item.item_code,
                "entitlement_type": "ott",
                "entitlement_title": item_name
            })

        plan.update({"entitlements": entitlements})

        # Convert timestamps
        if isinstance(self.start_timestamp_for_the_plan, datetime.datetime):
            start_timestamp = self.start_timestamp_for_the_plan.isoformat()
            end_timestamp = self.end_timestamp_for_the_plan.isoformat()
        elif isinstance(self.start_timestamp_for_the_plan, str):
            try:
                start_timestamp = datetime.datetime.strptime(self.start_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
                end_timestamp = datetime.datetime.strptime(self.end_timestamp_for_the_plan, "%Y-%m-%d %H:%M:%S").isoformat()
            except Exception:
                start_timestamp = datetime.datetime.strptime(self.start_timestamp_for_the_plan, "%Y-%m-%d").isoformat()
                end_timestamp = datetime.datetime.strptime(self.end_timestamp_for_the_plan, "%Y-%m-%d").isoformat()

        # Extract preview_subscription_id
        preview_subscription_id = getattr(self, "preview_subscription_id", None)
        preview_customer = getattr(self, "preview_customer", None)

        # Construct request body
        body = {
            "action": "SUBSCRIPTION_ACTIVATION",
            "phone_number": self.phone_number,
            "country_code": self.country_code,
            "customer_id": self.customer if self.customer else preview_customer,
            "start_timestamp": str(start_timestamp) + "Z",
            "end_timestamp": str(end_timestamp) + "Z",
            "subscription_id": self.subscription_id if self.subscription_id else preview_subscription_id,
            "subscription_type": "Non-TV",
            "tv_device_serial_number": None,
            "tv_model": None,
            "activation_status": None
        }
        body.update({"plan": plan})

        # Create webhook log
        webhook_log = frappe.new_doc("Sensara Integration Request Log")
        webhook_log.request_for = "Dorplay Subscription Activation"
        webhook_log.reference_document = self.name
        webhook_log.headers = str(headers)
        webhook_log.data = json.dumps(body)
        webhook_log.user = self.modified_by
        webhook_log.url = sensara_settings.dorplay_base_url

        return body, webhook_log


def post_subscription_payload(body, webhook_log):
    # Fetch Sensara Integration Settings
    sensara_settings = frappe.get_doc('Sensara Integration Settings')
    headers = {
        'content-type': 'application/json',
        sensara_settings.dorplay_api_key: sensara_settings.dorplay_api_secret
    }

    try:
        # Make the POST request
        response = requests.post(sensara_settings.dorplay_base_url, headers=headers, data=json.dumps(body))
        webhook_log.response = response.text

        # Add response message
        try:
            webhook_log.message = str(response.json())
        except Exception as e:
            print(e)

    except HTTPError as http_err:
        webhook_log.error = str(http_err)
        frappe.throw(_("HTTP Error {0}".format(http_err)))

    # Save webhook log
    webhook_log.insert(ignore_permissions=True)

