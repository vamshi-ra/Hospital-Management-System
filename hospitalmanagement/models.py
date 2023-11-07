from django.db import models
from django.contrib.auth.models import User


departments=[('Cardiologist','cardiologist'),
('Dermatologists','dermatologists'),
('Emergency Medicine Specialists','emergency medicine specialists'),
('Allergists/Immunologists','allergists/immunologists'),
('Anesthesiologists','anesthesiologists'),
('ENT Specialist', 'ent'),
('Neurologist', 'neurologist')
]

# Create your models here.
class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    specialization = models.CharField(max_length=50,choices=departments)
    status = models.BooleanField(default=False)
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return "{} ({})".format(self.user.first_name,self.specialization)
    

#Patient class Model
class Patient(models.Model):
    class Gender(models.TextChoices):
        male = "MALE"
        female = "FEMALE"
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20,null=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, default="MALE")
    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    @property
    def get_id(self):
        return self.user.id
    def __str__(self):
        return self.user.first_name

#Appointment class Model
class Appointment(models.Model):
    STATUS_CHOICE = [('Booked', 'BOOKED'),('Closed', 'CLOSED'),('Cancelled', 'CANCELLED')]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField(default=None)
    time = models.TimeField(default=None)
    symptoms = models.TextField(default=None)
    status = models.CharField(max_length=255, choices=STATUS_CHOICE, default="BOOKED")
    medications = models.TextField()




