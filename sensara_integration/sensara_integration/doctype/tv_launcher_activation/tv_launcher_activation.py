# Copyright (c) 2024, dteam0370@gmail.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today


class TVLauncherActivation(Document):
	def on_submit(self):
		self.actual_installation_date = today()
