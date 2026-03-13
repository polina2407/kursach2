# hospital/admin.py
from django.contrib import admin  # ← Обязательно добавить!
from .models import Department, Room, Patient, DischargeHistory

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'department', 'capacity']
    list_filter = ['department']

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'department', 'room', 'age_category', 'gender']
    list_filter = ['department', 'gender', 'age_category']
    search_fields = ['last_name', 'first_name']

@admin.register(DischargeHistory)
class DischargeHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'department', 'date_discharged']
    list_filter = ['department', 'date_discharged']