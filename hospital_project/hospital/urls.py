from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('doctor_login/', views.doctor_login, name='doctor_login'),
    path('add_patient/', views.add_patient, name='add_patient'),
    path('select_room/<int:patient_id>/', views.select_room, name='select_room'),
    path('discharge_patient/<int:patient_id>/', views.discharge_patient, name='discharge_patient'),
    path('room_status/', views.room_status, name='room_status'),
    path('patient/<int:patient_id>/', views.patient_detail, name='patient_detail'),
]