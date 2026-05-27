app_name = "vbond"
app_title = "Vbond"
app_publisher = "GreyCube Technologies"
app_description = "Customization for vbond"
app_email = "admin@greycube.in"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "vbond",
# 		"logo": "/assets/vbond/logo.png",
# 		"title": "Vbond",
# 		"route": "/vbond",
# 		"has_permission": "vbond.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/vbond/css/vbond.css"
# app_include_js = "/assets/vbond/js/vbond.js"

# include js, css files in header of web template
# web_include_css = "/assets/vbond/css/vbond.css"
# web_include_js = "/assets/vbond/js/vbond.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "vbond/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
doctype_js = {
    "Delivery Note" : "public/js/delivery_note.js",
    "Sales Order"   : "public/js/sales_order.js",
    "Sales Invoice" : "public/js/sales_invoice.js",
    "Purchase Order" : "public/js/purchase_order.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "vbond/public/icons.svg"

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
jinja = {
	"methods": ["vbond.jinja.get_leaves_from_leave_ledger_in_salary_slip"],
}

# Installation
# ------------

# before_install = "vbond.install.before_install"
# after_install = "vbond.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "vbond.uninstall.before_uninstall"
# after_uninstall = "vbond.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "vbond.utils.before_app_install"
# after_app_install = "vbond.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "vbond.utils.before_app_uninstall"
# after_app_uninstall = "vbond.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "vbond.notifications.get_notification_config"

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

doc_events = {
	"Delivery Note": {
		"before_save" : "vbond.api.calculate_transport_data",
        "before_submit" : "vbond.api.calculate_basic_amount",
	},
    "Sales Order" : {
        "before_save" : "vbond.api.calculate_transport_data",
        "before_validate" : "vbond.api.fetch_discount_percentage_and_calculate_discount_amount",
	},
    "Sales Invoice" : {
        "before_save" : "vbond.api.calculate_transport_data",
        "before_validate" : "vbond.api.fetch_discount_percentage_and_calculate_discount_amount",
	},
    "Vehicle Log" : {
        "validate" : "vbond.api.calculate_trip_km"
    },
    "Stock Entry" : {
        "before_validate" : "vbond.api.generate_and_set_batch_no"
    },
    "Salary Slip" : {
        "after_insert" : "vbond.api.fetch_ot_weekly_off_public_holidays_in_salary_slip"
    },
    "Additional Salary": {
        "on_cancel": "vbond.api.cancel_overtime_on_cancel_of_additional_salary"
    },
    "Purchase Receipt" : {
        "before_validate" : "vbond.api.generate_and_set_batch_no_in_purchase_receipt"
    },
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"vbond.tasks.all"
# 	],
# 	"daily": [
# 		"vbond.tasks.daily"
# 	],
# 	"hourly": [
# 		"vbond.tasks.hourly"
# 	],
# 	"weekly": [
# 		"vbond.tasks.weekly"
# 	],
# 	"monthly": [
# 		"vbond.tasks.monthly"
# 	],
# }

# After Migrate Events
after_migrate = ['vbond.migrate.after_migrate']

# Testing
# -------

# before_tests = "vbond.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "vbond.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "vbond.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["vbond.utils.before_request"]
# after_request = ["vbond.utils.after_request"]

# Job Events
# ----------
# before_job = ["vbond.utils.before_job"]
# after_job = ["vbond.utils.after_job"]

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
# 	"vbond.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

required_apps = ["erpnext","hrms"]