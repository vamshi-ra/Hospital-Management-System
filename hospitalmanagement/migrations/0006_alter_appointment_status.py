# Generated by Django 4.0.1 on 2023-10-31 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospitalmanagement', '0005_alter_appointment_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='status',
            field=models.CharField(choices=[('Booked', 'BOOKED'), ('Closed', 'CLOSED'), ('Cancelled', 'CANCELLED')], default='BOOKED', max_length=255),
        ),
    ]
