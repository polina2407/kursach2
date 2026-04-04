import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from hospital.models import Department, Room

# Создаем 4 отделения по 10 палат
if not Department.objects.exists():
    departments_data = [
        "Хирургическое", "Терапевтическое",
        "Неврологическое", "Кардиологическое"
    ]

    for dep_name in departments_data:
        department = Department.objects.create(name=dep_name)
        print(f"✅ Создано отделение: {dep_name}")
        for i in range(1, 11):
            Room.objects.create(department=department, number=i, capacity=4)
        print(f"   → Добавлено 10 палат")
else:
    print("⚠️ Отделения уже существуют")

print("\n📋 Структура больницы создана!")
print(f"Всего отделений: {Department.objects.count()}")
print(f"Всего палат: {Room.objects.count()}")
