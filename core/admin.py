from django.contrib import admin
from .models import Donor, Hospital, BloodRequest


# 👤 DONOR ADMIN
@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = ['user', 'blood_group', 'phone', 'location']
    search_fields = ['user__username', 'blood_group', 'location']
    list_filter = ['blood_group']


# 🏥 HOSPITAL ADMIN
@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'location']
    search_fields = ['name', 'location']


# 🩸 BLOOD REQUEST ADMIN
@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ['hospital', 'blood_group', 'location']
    search_fields = ['blood_group', 'location']









    
