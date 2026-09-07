
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Donor(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5)
    location = models.CharField(max_length=100)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    last_donation_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    
class Hospital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    # 🔥 ADD THIS
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.name
    

class BloodRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fulfilled', 'Fulfilled'),
    ]

    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    blood_group = models.CharField(max_length=5)
    location = models.CharField(max_length=100)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # 🔥 NEW FIELD
    fulfilled_by = models.ForeignKey(
        Donor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
