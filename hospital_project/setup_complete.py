#!/usr/bin/env python
"""
Скрипт для полной настройки базы данных больницы:
- Создание суперпользователя (администратора)
- Создание 4 врачей с учетными записями и кодами доступа
- Создание 4 отделений по 10 палат в каждом
"""

import os
import sys
import django

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.contrib.auth.models import User
from hospital.models import Doctor, Department, Room

def setup_database():
    print("=== Начало настройки базы данных ===\n")

    # 1. Создаем суперпользователя (администратора)
    print("1. Создание администратора...")
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@hospital.com',
            first_name='Админ',
            last_name='Истратор'
        )
        print(f"   ✓ Администратор создан: admin / admin123")
    else:
        print("   ✓ Администратор уже существует")

    # 2. Создаем 4 врачей с учетными записями и кодами
    print("\n2. Создание врачей...")
    doctors_data = [
        {'username': 'doctor1', 'password': 'pass123', 'code': 'DOC001', 'first_name': 'Иван', 'last_name': 'Петров', 'specialty': 'Терапевт'},
        {'username': 'doctor2', 'password': 'pass123', 'code': 'DOC002', 'first_name': 'Мария', 'last_name': 'Сидорова', 'specialty': 'Хирург'},
        {'username': 'doctor3', 'password': 'pass123', 'code': 'DOC003', 'first_name': 'Алексей', 'last_name': 'Кузнецов', 'specialty': 'Невролог'},
        {'username': 'doctor4', 'password': 'pass123', 'code': 'DOC004', 'first_name': 'Елена', 'last_name': 'Попова', 'specialty': 'Кардиолог'},
    ]

    for doc_data in doctors_data:
        if not User.objects.filter(username=doc_data['username']).exists():
            user = User.objects.create_user(
                username=doc_data['username'],
                password=doc_data['password'],
                email=f"{doc_data['username']}@hospital.com",
                first_name=doc_data['first_name'],
                last_name=doc_data['last_name']
            )
            doctor = Doctor.objects.create(
                user=user,
                code=doc_data['code'],
                specialty=doc_data['specialty'],
                is_active=True
            )
            print(f"   ✓ Врач создан: {doc_data['username']} / {doc_data['password']} (код: {doc_data['code']})")
        else:
            print(f"   ✓ Врач {doc_data['username']} уже существует")

    # 3. Создаем 4 отделения
    print("\n3. Создание отделений...")
    departments_names = ['Хирургическое', 'Терапевтическое', 'Неврологическое', 'Кардиологическое']
    departments = []
    
    for dept_name in departments_names:
        dept, created = Department.objects.get_or_create(name=dept_name)
        departments.append(dept)
        if created:
            print(f"   ✓ Отделение создано: {dept_name}")
        else:
            print(f"   ✓ Отделение {dept_name} уже существует")

    # 4. Создаем по 10 палат в каждом отделении
    print("\n4. Создание палат (по 10 в каждом отделении)...")
    for dept in departments:
        for room_num in range(1, 11):
            room, created = Room.objects.get_or_create(
                department=dept,
                number=room_num,
                defaults={'capacity': 4}
            )
            if created and room_num == 1:
                print(f"   ✓ В отделении '{dept.name}' создано 10 палат (№{room_num}-10)")

    print("\n=== Настройка завершена! ===")
    print("\nДоступные учетные записи:")
    print("  Администратор: admin / admin123")
    print("  Врачи:")
    print("    - doctor1 / pass123 (код доступа: DOC001)")
    print("    - doctor2 / pass123 (код доступа: DOC002)")
    print("    - doctor3 / pass123 (код доступа: DOC003)")
    print("    - doctor4 / pass123 (код доступа: DOC004)")
    print("\nСтруктура больницы:")
    print("  - 4 отделения: Хирургическое, Терапевтическое, Неврологическое, Кардиологическое")
    print("  - В каждом отделении по 10 палат (вместимость 4 человека)")
    print("\nЗапустите сервер: python manage.py runserver")

if __name__ == '__main__':
    setup_database()
