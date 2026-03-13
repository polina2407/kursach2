from django.db import models
from datetime import date


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Room(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    number = models.IntegerField()
    capacity = models.IntegerField(default=4)

    def free_places(self):
        return self.capacity - self.patient_set.count()

    def is_full(self):
        return self.free_places() <= 0

    def __str__(self):
        return f"Палата {self.number} ({self.department.name})"


class Patient(models.Model):
    # 👉 ФИО
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    middle_name = models.CharField(max_length=100, blank=True, verbose_name="Отчество")


    birth_date = models.DateField(verbose_name="Дата рождения")
    gender = models.CharField(
        max_length=1,
        choices=[('M', 'Мужской'), ('F', 'Женский')],
        verbose_name="Пол"
    )
    allergy = models.TextField(blank=True, verbose_name="Аллергия")
    age_category = models.CharField(max_length=20, blank=True, verbose_name="Возрастная категория")


    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Отделение")
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Палата")

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_age(self):
        from datetime import date
        today = date.today()
        age = today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
        )
        return age

    def save(self, *args, **kwargs):

        if self.birth_date:
            age = self.get_age()

            if age < 13:
                self.age_category = "child"
            elif age < 18:
                self.age_category = "teen"
            else:
                self.age_category = "adult"

        super().save(*args, **kwargs)

    def get_age_category_display_ru(self):
        categories = {
            'child': 'Ребёнок',
            'teen': 'Подросток',
            'adult': 'Взрослый'
        }
        return categories.get(self.age_category, self.age_category)


class DischargeHistory(models.Model):
    patient_name = models.CharField(max_length=200)
    department = models.CharField(max_length=100)
    room_number = models.IntegerField()
    date_admitted = models.DateField()
    date_discharged = models.DateField(auto_now_add=True)
    disease = models.TextField()

    def __str__(self):
        return f"Выписка: {self.patient_name}"