import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User
from hospital.models import Doctor, Department

# Создаем суперпользователя (администратора)
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@hospital.com',
        'first_name': 'Админ',
        'last_name': 'Системы',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print(f"✅ Создан администратор: admin / admin123")

# Создаем 4 врачей
doctors_data = [
    {'username': 'doctor1', 'password': 'pass123', 'code': 'DOC001', 'first_name': 'Иван', 'last_name': 'Петров', 'specialty': 'Терапевт'},
    {'username': 'doctor2', 'password': 'pass123', 'code': 'DOC002', 'first_name': 'Мария', 'last_name': 'Сидорова', 'specialty': 'Хирург'},
    {'username': 'doctor3', 'password': 'pass123', 'code': 'DOC003', 'first_name': 'Алексей', 'last_name': 'Козлов', 'specialty': 'Невролог'},
    {'username': 'doctor4', 'password': 'pass123', 'code': 'DOC004', 'first_name': 'Елена', 'last_name': 'Новикова', 'specialty': 'Кардиолог'},
]

for doc_data in doctors_data:
    user, created = User.objects.get_or_create(
        username=doc_data['username'],
        defaults={
            'email': f"{doc_data['username']}@hospital.com",
            'first_name': doc_data['first_name'],
            'last_name': doc_data['last_name'],
            'is_staff': False,
            'is_superuser': False,
        }
    )
    if created:
        user.set_password(doc_data['password'])
        user.save()
    
    doctor, doctor_created = Doctor.objects.get_or_create(
        user=user,
        defaults={
            'code': doc_data['code'],
            'specialty': doc_data['specialty'],
            'is_active': True,
        }
    )
    
    if doctor_created:
        # Привязываем врача к соответствующему отделению
        departments = Department.objects.all()
        if departments.exists():
            dep_index = int(doc_data['username'][-1]) - 1
            if dep_index < len(departments):
                doctor.departments.add(departments[dep_index])
        
        print(f"✅ Создан врач: {doc_data['username']} / {doc_data['password']} (код: {doc_data['code']})")
    else:
        print(f"⚠️ Врач {doc_data['username']} уже существует")

print("\n📋 Учетные данные:")
print("Администратор: admin / admin123")
print("Врачи:")
print("  - doctor1 / pass123 (код: DOC001)")
print("  - doctor2 / pass123 (код: DOC002)")
print("  - doctor3 / pass123 (код: DOC003)")
print("  - doctor4 / pass123 (код: DOC004)")
