app_name = "sensara_integration"
app_title = "Sensara Integration"
app_publisher = "dteam0370@gmail.com"
app_description = "Integration"
app_email = " dteam0370@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sensara_integration/css/sensara_integration.css"
# app_include_js = "/assets/sensara_integration/js/sensara_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/sensara_integration/css/sensara_integration.css"
# web_include_js = "/assets/sensara_integration/js/sensara_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sensara_integration/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "sensara_integration/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sensara_integration.utils.jinja_methods",
# 	"filters": "sensara_integration.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sensara_integration.install.before_install"
# after_install = "sensara_integration.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sensara_integration.uninstall.before_uninstall"
# after_uninstall = "sensara_integration.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sensara_integration.utils.before_app_install"
# after_app_install = "sensara_integration.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sensara_integration.utils.before_app_uninstall"
# after_app_uninstall = "sensara_integration.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sensara_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doc_events = { 
    "Delivery Note": {
        "after_insert": "sensara_integration.sensara_integration.customization.delivery_note.delivery_note.after_insert",
        "on_submit": "sensara_integration.sensara_integration.customization.delivery_note.delivery_note.on_submit"
    },
    "Product Bundle": {
        "validate": "sensara_integration.sensara_integration.customization.product_bundle.product_bundle.validate"
    },
    #"Sales Invoice": {
        #"after_insert": "sensara_integration.sensara_integration.customization.delivery_note.sales_invoice_update.on_submit"
        #"on_submit": "sensara_integration.sensara_integration.customization.delivery_note.new_radix.radix_tv_locking"
    #},
    "Renewal Sales Invoice": {
        "on_submit": ["sensara_integration.sensara_integration.customization.delivery_note.renewal_sales_invoice.on_submit","sensara_integration.sensara_integration.customization.delivery_note.radix_new_renewal.radix_tv_locking"]
    },
    "Radix Locking":{"after_insert": "sensara_integration.sensara_integration.customization.delivery_note.radix_lock1.lock_device"}
}


scheduler_events = {
    "daily": [
        "sensara_integration.coupons_tasks.scheduled_update_dates"
    ]
}
# Scheduled Tasks
# ---------------

# scheduler_events = {"cron": {"30 17 * * *":["sensara_integration.sensara_integration.customization.delivery_note.radix_lock.radix_tv_locking"]}}

# 	"all": [
# 		"sensara_integration.tasks.all"
# 	],
# 	"daily": [
# 		"sensara_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"sensara_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sensara_integration.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sensara_integration.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sensara_integration.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sensara_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sensara_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sensara_integration.utils.before_request"]
# after_request = ["sensara_integration.utils.after_request"]

# Job Events
# ----------
# before_job = ["sensara_integration.utils.before_job"]
# after_job = ["sensara_integration.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sensara_integration.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

