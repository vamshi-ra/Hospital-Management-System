from django.contrib import admin
from .models import Appointment, Doctor, Patient

# Register your models here.
class DoctorAdmin(admin.ModelAdmin):
    model = Doctor

admin.site.register(Doctor, DoctorAdmin)

#Patient registration
class PatientAdmin(admin.ModelAdmin):
    model=Patient

admin.site.register(Patient, PatientAdmin)

#Appointment registration
class AppointmentAdmin(admin.ModelAdmin):
    model=Appointment
admin.site.register(Appointment, AppointmentAdmin)
