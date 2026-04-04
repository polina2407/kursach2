# hospital/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Department, Room, Patient, Doctor, DischargeHistory


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    verbose_name = "Отделение"
    verbose_name_plural = "Отделения"


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['number', 'department', 'capacity', 'free_places']
    list_filter = ['department']
    search_fields = ['number', 'department__name']
    verbose_name = "Палата"
    verbose_name_plural = "Палаты"


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'department', 'room', 'age_category', 'gender', 'admission_date']
    list_filter = ['department', 'gender', 'age_category']
    search_fields = ['last_name', 'first_name', 'middle_name']
    verbose_name = "Пациент"
    verbose_name_plural = "Пациенты"


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'specialty', 'is_active', 'created_at']
    list_filter = ['is_active', 'departments']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'code']
    filter_horizontal = ['departments']
    verbose_name = "Врач"
    verbose_name_plural = "Врачи"


@admin.register(DischargeHistory)
class DischargeHistoryAdmin(admin.ModelAdmin):
    list_display = ['patient_name', 'department', 'date_admitted', 'date_discharged', 'discharged_by']
    list_filter = ['department', 'date_discharged']
    search_fields = ['patient_name', 'department']
    verbose_name = "История выписки"
    verbose_name_plural = "Истории выписок"