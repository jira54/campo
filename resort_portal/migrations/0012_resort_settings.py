# Generated migration for ResortSettings model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0013_vendor_resort_manager_pin_vendor_resort_otp_and_more'),
        ('resort_portal', '0011_add_performance_indexes'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResortSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default_tax_rate', models.DecimalField(decimal_places=2, default=16.0, help_text='Default VAT rate for calculations', max_digits=5)),
                ('currency_code', models.CharField(default='KES', help_text='Currency code for display', max_length=3)),
                ('currency_symbol', models.CharField(default='KSh', help_text='Currency symbol for display', max_length=5)),
                ('default_department_names', models.JSONField(default=dict, help_text='Default department names for auto-creation')),
                ('auto_checkout_time', models.TimeField(default='10:00', help_text='Default check-out time')),
                ('auto_checkin_time', models.TimeField(default='14:00', help_text='Default check-in time')),
                ('housekeeping_alert_threshold', models.PositiveIntegerField(default=5, help_text='Alert when dirty rooms exceed this number')),
                ('dashboard_refresh_interval', models.PositiveIntegerField(default=300, help_text='Dashboard auto-refresh interval in seconds')),
                ('enable_vip_alerts', models.BooleanField(default=True, help_text='Show VIP arrival alerts')),
                ('enable_revenue_alerts', models.BooleanField(default=True, help_text='Show revenue milestone alerts')),
                ('pin_expiry_days', models.PositiveIntegerField(default=90, help_text='Days after which PIN should be changed')),
                ('max_login_attempts', models.PositiveIntegerField(default=3, help_text='Maximum failed login attempts before lockout')),
                ('enable_email_receipts', models.BooleanField(default=True, help_text='Send email receipts on check-out')),
                ('receipt_email_template', models.TextField(blank=True, help_text='Custom email template for receipts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('resort_property', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='vendors.property')),
                ('vendor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resort_settings', to='vendors.vendor')),
            ],
            options={
                'verbose_name': 'Resort Settings',
                'verbose_name_plural': 'Resort Settings',
            },
        ),
    ]
