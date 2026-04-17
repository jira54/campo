from django.core.management.base import BaseCommand
from resort_portal.models import Facility, RestaurantTable, BarSeat, DayPass, Department
from vendors.models import Property
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds initial operational data for the modular resort dashboard'

    def handle(self, *args, **options):
        vendors = User.objects.filter(business_type='resort')
        if not vendors.exists():
            self.stdout.write(self.style.WARNING('No resort vendors found.'))
            return

        for vendor in vendors:
            properties = Property.objects.filter(vendor=vendor)
            for prop in properties:
                self.stdout.write(f'Seeding data for {prop.name} ({vendor.email})...')

                # 1. Departments
                depts = ['Room Service', 'Housekeeping', 'Restaurant', 'Pool Bar', 'Laundry']
                for dname in depts:
                    Department.objects.get_or_create(vendor=vendor, resort_property=prop, name=dname)

                # 2. Facilities
                facilities = [
                    'Main Pool',
                    'Ocean Gym',
                    'Sunrise Spa',
                    'Beach Lounge',
                ]
                for name in facilities:
                    Facility.objects.get_or_create(
                        vendor=vendor, resort_property=prop, name=name,
                        defaults={'status': 'Open'}
                    )

                # 3. Restaurant Tables
                for i in range(1, 11):
                    RestaurantTable.objects.get_or_create(
                        vendor=vendor, resort_property=prop, table_number=i,
                        defaults={'capacity': 4, 'table_type': 'Standard'}
                    )

                # 4. Bar Seats
                for i in range(1, 13):
                    BarSeat.objects.get_or_create(
                        vendor=vendor, resort_property=prop, seat_number=i
                    )

                # 5. Day Passes
                passes = [
                    ('Pool Pass', 1500, 'Access to main pool and towels.'),
                    ('Full Day Access', 3500, 'Pool, Gym, and Lunch Buffet.'),
                    ('Gym Only', 800, 'Entry to ocean gym.'),
                ]
                for name, price, desc in passes:
                    DayPass.objects.get_or_create(
                        vendor=vendor, resort_property=prop, name=name,
                        defaults={'price': price, 'includes_services': desc}
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded resort data.'))
