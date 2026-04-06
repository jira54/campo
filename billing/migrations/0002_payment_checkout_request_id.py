# Generated manually — adds checkout_request_id to billing.Payment

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='checkout_request_id',
            field=models.CharField(
                blank=True,
                default='',
                max_length=100,
                help_text='Safaricom CheckoutRequestID — used to match callbacks',
            ),
        ),
    ]
