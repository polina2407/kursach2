from django.db import models
from datetime import date
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название отделения")

    class Meta:
        verbose_name = "Отделение"
        verbose_name_plural = "Отделения"

    def __str__(self):
        return self.name


class Room(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, verbose_name="Отделение")
    number = models.IntegerField(verbose_name="Номер палаты")
    capacity = models.IntegerField(default=4, verbose_name="Вместимость")

    class Meta:
        verbose_name = "Палата"
        verbose_name_plural = "Палаты"
        unique_together = ['department', 'number']
        ordering = ['department', 'number']

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
    admitted_by = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Врач, принявший пациента")
    admission_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата поступления")

    class Meta:
        verbose_name = "Пациент"
        verbose_name_plural = "Пациенты"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_age(self):
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


class Doctor(models.Model):
    """Модель врача с уникальным кодом доступа"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Учетная запись", related_name='doctor_profile')
    code = models.CharField(max_length=10, unique=True, verbose_name="Код доступа")
    specialty = models.CharField(max_length=100, blank=True, verbose_name="Специальность")
    departments = models.ManyToManyField(Department, blank=True, verbose_name="Отделения")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Врач"
        verbose_name_plural = "Врачи"
        ordering = ['user__last_name', 'user__first_name']

    def __str__(self):
        return f"Др. {self.user.get_full_name() or self.user.username} ({self.code})"

    @classmethod
    def authenticate_by_code(cls, code):
        """Аутентификация врача по коду"""
        try:
            doctor = cls.objects.get(code=code, is_active=True)
            return doctor
        except cls.DoesNotExist:
            return None


class DischargeHistory(models.Model):
    patient_name = models.CharField(max_length=200, verbose_name="ФИО пациента")
    department = models.CharField(max_length=100, verbose_name="Отделение")
    room_number = models.IntegerField(verbose_name="Номер палаты")
    date_admitted = models.DateField(verbose_name="Дата поступления")
    date_discharged = models.DateField(auto_now_add=True, verbose_name="Дата выписки")
    disease = models.TextField(verbose_name="Диагноз/Причина выписки")
    discharged_by = models.ForeignKey('Doctor', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Выписавший врач")

    class Meta:
        verbose_name = "История выписки"
        verbose_name_plural = "Истории выписок"
        ordering = ['-date_discharged']

    def __str__(self):
        return f"Выписка: {self.patient_name}"