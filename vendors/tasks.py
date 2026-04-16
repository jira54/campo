from celery import shared_task
import time

@shared_task
def send_welcome_email_async(vendor_id):
    """
    Simulates sending a welcome email asynchronously.
    """
    from vendors.models import Vendor
    try:
        vendor = Vendor.objects.get(id=vendor_id)
        print(f"Starting async email task for {vendor.email}...")
        time.sleep(5)  # Simulate network latency
        print(f"Welcome email sent to {vendor.email} successfully.")
        return True
    except Vendor.DoesNotExist:
        return False

@shared_task
def generate_monthly_report_async(vendor_id):
    """
    Simulates a long-running report generation.
    """
    print(f"Generating monthly report for Vendor ID: {vendor_id}")
    time.sleep(10)
    print("Report generated.")
    return "Report Path: /media/reports/monthly_sample.pdf"
