from datetime import datetime
from django import forms
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework import serializers
from rest_framework import viewsets
from .models import Appointment, Doctor, Patient
from djongo import models
from django.apps import apps
from django.contrib.auth.decorators import login_required, user_passes_test


class AppointmentEditForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = "__all__"
        widgets = {
            "status": forms.MultipleChoiceField(choices=Appointment.STATUS_CHOICE)
        }


# Create your views here.
# ---------------Miscellaneous ----------
def is_doctor(user):
    return user.groups.filter(name="DOCTOR").exists()


def is_patient(user):
    return user.groups.filter(name="PATIENT").exists()


def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return render(request, "hospitalmanagement/index.html")


def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect("afterlogin")
    return redirect(request, "hospitalmanagement/adminclick.html")


def afterlogin_view(request):
    if is_doctor(request.user):
        return redirect("doctor-dashboard")
    elif is_patient(request.user):
        return redirect("patient-dashboard")


# --------------- Doctor API's------------------------------------


def register_doctor(request):
    if request.method == "POST":
        # Get the form data.
        first_name = request.POST["firstName"]
        last_name = request.POST["lastName"]
        email = request.POST["email"]
        password = request.POST["password"]
        specialization = request.POST["specialization"]
        address = request.POST["address"]
        mobile = request.POST["mobile"]

        # Create a new user object.
        user = User.objects.create_user(email, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Create a new doctor object.
        doctor = Doctor(
            user=user, specialization=specialization, address=address, mobile=mobile
        )
        doctor.save()

        my_doctor_group = Group.objects.get_or_create(name="DOCTOR")
        my_doctor_group[0].user_set.add(user)
        # Redirect the user to their profile page.
        return redirect("/doctorlogin/")

    else:
        # Render the registration form.
        return render(request, "hospitalmanagement/doctor_register.html")


@login_required(login_url="doctorlogin")
@user_passes_test(is_doctor)
def doctor_dashboard_view(request):
    Doctor = apps.get_model("hospitalmanagement", "Doctor")
    doctor = Doctor.objects.get(user_id=request.user.id)
    Patient = apps.get_model("hospitalmanagement", "Patient")
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    date = datetime.now().date()

    q = Q(status__icontains="BOOKED")
    q |= Q(status__icontains="CLOSED")
    appointment_count = Appointment.objects.filter(q, date=date, doctor=doctor).count()
    q = Q(status__icontains="CLOSED")
    patient_count = Appointment.objects.filter(q, doctor=doctor).count()

    q = Q(status__icontains="BOOKED")
    # for  table in doctor dashboard
    appointments = Appointment.objects.filter(q, doctor=doctor, date=date).order_by(
        "-id"
    )
    #  appointments=zip(appointments,patients)
    mydict = {
        "patientcount": appointment_count,
        "appointmentcount": appointment_count,
        "patientdischarged": patient_count,
        "appointments": appointments[0] if appointments else appointments,
        "doctor": doctor,
    }
    return render(request, "hospitalmanagement/doctor_dashboard.html", context=mydict)


@login_required(login_url="doctorlogin")
@user_passes_test(is_doctor)
def patient_view(request):
    Doctor = apps.get_model("hospitalmanagement", "Doctor")
    mydict = {
        "doctor": Doctor.objects.get(
            user_id=request.user.id
        ),  # for profile picture of doctor in sidebar
    }
    return render(request, "hospitalmanagement/doctor_patient.html", context=mydict)


@login_required(login_url="doctorlogin")
@user_passes_test(is_doctor)
def doctor_patient_views(request):
    Doctor = apps.get_model("hospitalmanagement", "Doctor")
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    doctor = Doctor.objects.get(
        user_id=request.user.id
    )  # for profile picture of doctor in sidebar
    appointments = Appointment.objects.filter(doctor=doctor)
    return render(
        request,
        "hospitalmanagement/doctor_view_patient.html",
        {"appointments": appointments, "doctor": doctor},
    )


@login_required(login_url="doctorlogin")
@user_passes_test(is_doctor)
def doctor_view_patient_view(request):
    patients = models.Patient.objects.all().filter(
        status=True, assignedDoctorId=request.user.id
    )
    doctor = models.Doctor.objects.get(
        user_id=request.user.id
    )  # for profile picture of doctor in sidebar
    return render(
        request,
        "hospital/doctor_view_patient.html",
        {"patients": patients, "doctor": doctor},
    )


@login_required(login_url="doctorlogin")
@user_passes_test(is_doctor)
def doctor_view_appointment_view(request):
    Doctor = apps.get_model("hospitalmanagement", "Doctor")
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    doctor = Doctor.objects.get(
        user_id=request.user.id
    )  # for profile picture of doctor in sidebar
    date = datetime.now().date()
    q = Q(status__icontains="BOOKED")
    q |= Q(status__icontains="CLOSED")
    appointments = Appointment.objects.filter(q, date=date, doctor=doctor).order_by(
        "-id"
    )
    return render(
        request,
        "hospitalmanagement/doctor_view_appointment.html",
        {"appointments": appointments, "doctor": doctor},
    )


@login_required(login_url="doctorlogin")
@user_passes_test(is_doctor)
def doctor_edit_appointment(request, appointment_id):
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == "POST":
        description = request.POST["description"]
        appointment.status = "Closed"
        appointment.medications = description
        appointment.save()
        date = datetime.now().date()
        q = Q(status__icontains="BOOKED")
        q |= Q(status__icontains="CLOSED")
        appointments = Appointment.objects.filter(
            q, date=date, doctor=appointment.doctor
        ).order_by("-id")
        return render(
            request,
            "hospitalmanagement/doctor_view_appointment.html",
            {"appointments": appointments, "doctor": appointment.doctor},
        )

    return render(
        request,
        "hospitalmanagement/doctor_edit_appointment.html",
        {"appointment": appointment},
    )


@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def doctor_profile_update(request):
    Doctor = apps.get_model("hospitalmanagement", "Doctor")
    doctor = Doctor.objects.get(user_id=request.user.id)
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        address = request.POST["address"]
        mobile = request.POST["mobile"]
        user = User.objects.get(id=request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.set_password(password)
        user.save()
        doctor.address = address
        doctor.mobile = mobile
        doctor.save()
        return render(
            request,
            "hospitalmanagement/doctor_profile_update.html",
            {"doctor": doctor}
        )

    return render(
        request, "hospitalmanagement/doctor_profile_update.html", {"doctor": doctor}
    )


# ---------------------------Patient API's ---------------------------------
def register_patient(request):
    if request.method == "POST":
        first_name = request.POST["firstName"]
        last_name = request.POST["lastName"]
        email = request.POST["email"]
        password = request.POST["password"]
        address = request.POST["address"]
        mobile = request.POST["mobile"]
        gender = request.POST["gender"]

        user = User.objects.create_user(email, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        patient = Patient(user=user, address=address, mobile=mobile, gender=gender)
        patient.save()

        my_doctor_group = Group.objects.get_or_create(name="PATIENT")
        my_doctor_group[0].user_set.add(user)

        return redirect("/patientlogin/")
    else:
        return render(request, "hospitalmanagement/patient_register.html")


@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def patient_dashboard_view(request):
    Patient = apps.get_model("hospitalmanagement", "Patient")
    patient = Patient.objects.get(user_id=request.user.id)

    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    q = Q(status__icontains="BOOKED")
    latest_appointments = Appointment.objects.filter(q, patient=patient).order_by(
        "-date", "-time"
    )

    if latest_appointments.exists():
        Doctor = apps.get_model("hospitalmanagement", "Doctor")
        doctor = Doctor.objects.get(id=latest_appointments[0].doctor.id)
        mydict = {
            "status": "success",
            "patient": patient,
            "doctorName": doctor.get_name,
            "doctorMobile": doctor.mobile,
            "symptoms": latest_appointments[0].symptoms,
            "doctorDepartment": doctor.specialization,
            "appointmentDate": latest_appointments[0].date,
            "appointmentTime": latest_appointments[0].time,
        }
        return render(
            request, "hospitalmanagement/patient_dashboard.html", context=mydict
        )
    else:
        return render(
            request, "hospitalmanagement/patient_dashboard.html", context=None
        )


@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def patient_profile_update(request):
    Patient = apps.get_model("hospitalmanagement", "Patient")
    patient = Patient.objects.get(user_id=request.user.id)
    if request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        address = request.POST["address"]
        mobile = request.POST["mobile"]
        gender = request.POST["gender"]
        user = User.objects.get(id=request.user.id)
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.set_password(password)
        user.save()
        patient.address = address
        patient.mobile = mobile
        patient.gender = gender
        patient.save()
        return render(
            request,
            "hospitalmanagement/patient_profile_update.html",
            {"patient": patient},
        )

    return render(
        request, "hospitalmanagement/patient_profile_update.html", {"patient": patient}
    )


# ------------------------Appointment API's-----------------
@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def book_appointment(request):
    if request.method == "POST":
        patient_date = request.POST["date"]
        patient_time = request.POST["time"]
        patient_specialization = request.POST["specialization"]
        patient_symptoms = request.POST["symptoms"]

        message = None
        mydict = {"status": None, "message": message}

        q = Q(specialization__icontains=patient_specialization)

        patient_date_object = datetime.strptime(patient_date, "%Y-%m-%d")
        patient_time_object = datetime.strptime(patient_time, "%I:%M %p").strftime(
            "%H:%M:%S.%f"
        )

        Doctor = apps.get_model("hospitalmanagement", "Doctor")
        Appointment = apps.get_model("hospitalmanagement", "Appointment")
        Patient = apps.get_model("hospitalmanagement", "Patient")

        patient = Patient.objects.get(user=request.user)
        # Get a list of doctors with the specified specialization
        doctors = Doctor.objects.filter(q)
        doctor_ids = []
        for doctor in doctors:
            doctor_ids.append(doctor.id)

        # Filter out doctors who have appointments at the requested date and time
        doctors_with_appointments = Appointment.objects.filter(
            doctor__in=doctor_ids, date=patient_date_object, time=patient_time_object
        ).values_list("doctor", flat=True)

        q = Q()
        for doctor_id in doctors_with_appointments:
            q |= Q(id__ne=doctor_id)
        available_doctors = doctors.filter(q)

        # Query the database to find a doctor with the desired specialization who is available for an appointment at the desired date and time.
        # doctors = Doctor.objects.filter(specialization=patient_specialization).filter(appointment__date=patient_date).filter(appointment__time=patient_time_object).order_by('appointment')

        # Check if there are any cancelled appointments for the doctor on the selected date and time.

        cancelled_appointments = Appointment.objects.filter(
            status="CANCELLED",
            doctor__in=available_doctors,
            date=patient_date,
            time=patient_time_object,
        )

        # cancelled_appointments = Appointment.objects.filter(status='CANCELLED', doctor__in=available_doctors, date=patient_date, time=patient_time_object)

        # If there are cancelled appointments, book the cancelled appointment with the patient.
        if cancelled_appointments.exists():
            cancelled_appointment = cancelled_appointments.first()
            cancelled_appointment.patient = patient
            cancelled_appointment.status = "BOOKED"
            cancelled_appointment.symptoms = patient_symptoms
            cancelled_appointment.save()
            mydict["status"] = "success"
            mydict["message"] = "The appointment has been booked successfully."

            return HttpResponseRedirect("patient-view-appointment")

        # If there are no cancelled appointments available, book the next available appointment with the patient.

        if available_doctors.exists():
            doctor = available_doctors.first()
            appointment = apps.get_model("hospitalmanagement", "Appointment")(
                patient=patient,
                doctor=doctor,
                date=patient_date,
                time=patient_time_object,
                status="BOOKED",
                symptoms=patient_symptoms,
            )
            appointment.save()
            mydict["status"] = "success"
            mydict["message"] = "The appointment has been booked successfully."

            return HttpResponseRedirect("/patient-dashboard/")
        else:
            return render(
                request,
                "hospitalmanagement/book_appointment.html",
                context={
                    "message": "No Appointments available on selected slot"
                },
            )

        # If the patient is booking an appointment for a specialization that is not available in the hospital, return an error message to the user.

    else:
        return render(request, "hospitalmanagement/book_appointment.html")


@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def patient_appointment_view(request):
    Patient = apps.get_model("hospitalmanagement", "Patient")
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    patient = Patient.objects.get(user_id=request.user.id)
    appointments = Appointment.objects.filter(patient=patient)
    return render(
        request,
        "hospitalmanagement/patient_view_appointment.html",
        {"appointments": appointments, "patient": patient},
    )


@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def cancel_appointment(request, appointment_id):
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    appointment = Appointment.objects.get(id=appointment_id)

    # Check if the user is authorized to cancel the appointment.
    if appointment.patient.user.id != request.user.id:
        return render(
            request,
            "hospitalmanagement/patient_view_appointment.html",
            {
                "status": "error",
                "message": "You are not authorized to cancel this appointment.",
            },
        )

    # Set the status of the appointment to cancelled.
    appointment.status = "Cancelled"
    appointment.patient = None

    # Save the appointment.
    appointment.save()
    return render(
        request,
        "hospitalmanagement/patient_view_appointment.html",
        {"status": "Cancelled", "message": "Cancelled your appointment successfully."},
    )


@login_required(login_url="/patientlogin/")
@user_passes_test(is_patient)
def reschedule_appointment(request, appointment_id):
    message = None
    mydict = {"status": None, "message": message}

    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    appointment = Appointment.objects.get(id=appointment_id)
    doctor = appointment.doctor

    if request.method == "POST":
        patient_date = request.POST["date"]
        patient_time = request.POST["time"]
        patient_specialization = request.POST["specialization"]
        patient_date_object = datetime.strptime(patient_date, "%Y-%m-%d")
        patient_time_object = datetime.strptime(patient_time, "%I:%M %p").strftime(
            "%H:%M:%S.%f"
        )
        existing_appointment = Appointment.objects.filter(
            date=patient_date_object, time=patient_time_object, doctor=doctor
        )
        if not existing_appointment.exists():
            appointment.date = patient_date_object
            appointment.time = patient_time_object
            appointment.save()
            mydict["status"] = "rescheduled"
            mydict["message"] = "The appointment has been rescheduled successfully."
            mydict["appointment"] = appointment
            mydict["date"] = patient_date_object
            return render(
                request,
                "hospitalmanagement/patient_reschedule_appointment.html",
                context=mydict,
            )
        else:
            mydict["status"] = "rescheduled-failed"
            mydict["message"] = "No slots available on the given date"
            return render(
                request,
                "hospitalmanagement/patient_reschedule_appointment.html",
                context=mydict,
            )

    return render(
        request,
        "hospitalmanagement/patient_reschedule_appointment.html",
        {
            "appointment": appointment,
        },
    )


@login_required(login_url="/doctorlogin/")
@user_passes_test(is_doctor)
def doctor_appointment_view(request):
    doctor = models.Doctor.objects.get(user_id=request.user.id)
    appointments = models.Appointment.objects.filter(doctor=doctor)
    patientId = []
    for appointment in appointments:
        patientId.append(appointment.patient)
    appointments = zip(appointments, patientId)
    return render(
        request,
        "hospitalmanagement/doctor_view_appointment.html",
        {"appointments": appointments, "doctor": doctor},
    )

def appointment_view(request, appointment_id):
    Appointment = apps.get_model("hospitalmanagement", "Appointment")
    appointment = Appointment.objects.get(id=appointment_id)
    template = 'hospitalmanagement/doctor_base.html' if(is_doctor) else 'hospitalmanagement/patient_base.html'
    return render(
        request,
        "hospitalmanagement/appointment_view.html",
        context={"appointment": appointment, "template": template},
    )
