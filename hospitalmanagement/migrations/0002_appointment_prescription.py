# Generated by Django 4.0.1 on 2023-10-23 17:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('hospitalmanagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time', models.DateTimeField()),
                ('status', models.CharField(choices=[('Booked', 'BOOKED'), ('Closed', 'CLOSED'), ('Cancelled', 'CANCELLED')], default='BOOKED', max_length=255)),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospitalmanagement.doctor')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hospitalmanagement.patient')),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medications', models.TextField()),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='hospitalmanagement.appointment')),
            ],
        ),
    ]
