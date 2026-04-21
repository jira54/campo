# Generated migration for ManagerAuth model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vendors', '0013_vendor_resort_manager_pin_vendor_resort_otp_and_more'),
        ('resort_portal', '0012_resort_settings'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(help_text='Manager email for verification', max_length=254)),
                ('phone', models.CharField(blank=True, help_text='Manager phone for verification', max_length=20)),
                ('password_hash', models.CharField(help_text='Hashed manager password', max_length=255)),
                ('is_verified', models.BooleanField(default=False, help_text='Email/phone verification status')),
                ('verification_code', models.CharField(blank=True, help_text='Email/phone verification code', max_length=6)),
                ('verification_expires', models.DateTimeField(blank=True, help_text='Verification code expiry', null=True)),
                ('failed_attempts', models.PositiveIntegerField(default=0, help_text='Failed login attempts')),
                ('locked_until', models.DateTimeField(blank=True, help_text='Account lockout expiry', null=True)),
                ('last_login', models.DateTimeField(blank=True, help_text='Last successful login', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('vendor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='manager_auth', to='vendors.vendor')),
            ],
            options={
                'verbose_name': 'Manager Authentication',
                'verbose_name_plural': 'Manager Authentication',
            },
        ),
    ]
