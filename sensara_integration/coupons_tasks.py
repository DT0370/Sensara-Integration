import frappe
from sensara_integration.coupon_custom_script import update_dates

def scheduled_update_dates():
    """
    Wrapper function to call update_dates for scheduled execution.
    """
    print("in scheduled_update_dates----------------------7")
    update_dates()
