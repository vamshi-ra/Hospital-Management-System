"""HospitalManagementSystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from hospitalmanagement import views
from django.contrib.auth.views import LoginView,LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home_view,name='hospitalmanagement/index.html'),

    path('logout', LogoutView.as_view(template_name='hospitalmanagement/index.html'),name='logout'),
    # This was configured in settings.py file
    path('afterlogin/', views.afterlogin_view,name='afterlogin'),
    #Doctor URL's
    path('register/doctor/', views.register_doctor, name='register_doctor'),
    path('doctorlogin/', LoginView.as_view(template_name='hospitalmanagement/doctor_login.html')),
    path('doctor-dashboard/', views.doctor_dashboard_view, name='doctor-dashboard'),
    path('doctor-patient/', views.patient_view, name='doctor-patient'),
    path('doctor-view-patient', views.doctor_patient_views, name='doctor-view-patient'),
    path('doctor-view-appointment', views.doctor_view_appointment_view, name='doctor-view-appointment'),
    path('doctor_edit_appointment/<int:appointment_id>', views.doctor_edit_appointment, name='doctor_edit_appointment'),
    

    #Patient URL's
    path('register/patient/', views.register_patient, name='register_patient'),
    path('patientlogin/', LoginView.as_view(template_name='hospitalmanagement/patient_login.html')),
    path('patient-dashboard/',views.patient_dashboard_view, name='patient-dashboard'),
    path('patient-appointment/', views.patient_appointment_view, name='patient-appointment'),
    path('patient-profile-update/', views.patient_profile_update, name='patient-profile-update'),

    #Appointment URL's
    path('appointment/book/', views.book_appointment, name='book_appointment'),
    path('appointment/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('appointment/reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('appointment/view/<int:appointment_id>/', views.appointment_view, name='appointment_view'),

    path('appointment/view/patient/', views.patient_appointment_view, name='patient_appointment_view'),
    path('appointment/view/doctor/', views.doctor_appointment_view, name='doctor_appointment_view'),




]
