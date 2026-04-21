# Generated migration for performance indexes

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resort_portal', '0010_alter_stayrecord_guest'),
    ]

    operations = [
        # ResortGuest indexes for frequently queried fields
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_resort_guest_name ON resort_portal_resortguest(name);",
            reverse_sql="DROP INDEX IF EXISTS idx_resort_guest_name;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_resort_guest_phone ON resort_portal_resortguest(phone);",
            reverse_sql="DROP INDEX IF EXISTS idx_resort_guest_phone;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_resort_guest_email ON resort_portal_resortguest(email);",
            reverse_sql="DROP INDEX IF EXISTS idx_resort_guest_email;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_resort_guest_vendor_property ON resort_portal_resortguest(vendor_id, resort_property_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_resort_guest_vendor_property;"
        ),
        
        # ServiceCharge indexes for dashboard performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_service_charge_logged_at ON resort_portal_servicecharge(logged_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_service_charge_logged_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_service_charge_vendor_property_date ON resort_portal_servicecharge(vendor_id, resort_property_id, logged_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_service_charge_vendor_property_date;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_service_charge_amount ON resort_portal_servicecharge(amount);",
            reverse_sql="DROP INDEX IF EXISTS idx_service_charge_amount;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_service_charge_is_paid ON resort_portal_servicecharge(is_paid);",
            reverse_sql="DROP INDEX IF EXISTS idx_service_charge_is_paid;"
        ),
        
        # StayRecord indexes for occupancy calculations
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_stay_record_status ON resort_portal_stayrecord(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_stay_record_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_stay_record_dates ON resort_portal_stayrecord(check_in_date, check_out_date);",
            reverse_sql="DROP INDEX IF EXISTS idx_stay_record_dates;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_stay_record_vendor_property ON resort_portal_stayrecord(vendor_id, resort_property_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_stay_record_vendor_property;"
        ),
        
        # Room indexes for housekeeping dashboard
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_room_status ON resort_portal_room(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_room_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_room_vendor_property ON resort_portal_room(vendor_id, resort_property_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_room_vendor_property;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_room_number ON resort_portal_room(room_number);",
            reverse_sql="DROP INDEX IF EXISTS idx_room_number;"
        ),
        
        # UserActivity indexes for activity feed
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_user_activity_created_at ON resort_portal_useractivity(created_at);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_activity_created_at;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_user_activity_vendor_property ON resort_portal_useractivity(vendor_id, resort_property_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_activity_vendor_property;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_user_activity_category ON resort_portal_useractivity(category);",
            reverse_sql="DROP INDEX IF EXISTS idx_user_activity_category;"
        ),
        
        # Department indexes for revenue breakdown
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_department_vendor_property ON resort_portal_department(vendor_id, resort_property_id);",
            reverse_sql="DROP INDEX IF EXISTS idx_department_vendor_property;"
        ),
        
        # RestaurantTable and BarSeat indexes for POS operations
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_restaurant_table_status ON resort_portal_restauranttable(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_restaurant_table_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS idx_bar_seat_status ON resort_portal_barseat(status);",
            reverse_sql="DROP INDEX IF EXISTS idx_bar_seat_status;"
        ),
    ]
