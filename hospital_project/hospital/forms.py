from django import forms
from .models import Patient, Doctor
from django.contrib.auth.models import User


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'last_name', 'first_name', 'middle_name',
            'birth_date', 'gender', 'department', 'allergy'
        ]
        labels = {
            'last_name': 'Фамилия',
            'first_name': 'Имя',
            'middle_name': 'Отчество',
            'birth_date': 'Дата рождения',
            'gender': 'Пол',
            'department': 'Отделение',
            'allergy': 'Аллергия/Особенности',
        }
        widgets = {
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию',
                'required': True
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя',
                'required': True
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True,
                'max': '9999-12-31'
            }),
            'gender': forms.RadioSelect(),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'allergy': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Укажите аллергию или напишите "нет"'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['gender'].choices = [
            ('M', 'Мужской'),
            ('F', 'Женский')
        ]

        self.fields['gender'].initial = 'M'
        
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name', '').strip()
        if not last_name:
            raise forms.ValidationError("Фамилия обязательна для заполнения")
        if len(last_name) < 2:
            raise forms.ValidationError("Фамилия должна быть не менее 2 символов")
        if not last_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Фамилия должна содержать только буквы и пробелы")
        return last_name
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', '').strip()
        if not first_name:
            raise forms.ValidationError("Имя обязательно для заполнения")
        if len(first_name) < 2:
            raise forms.ValidationError("Имя должно быть не менее 2 символов")
        if not first_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Имя должно содержать только буквы и пробелы")
        return first_name
    
    def clean_middle_name(self):
        middle_name = self.cleaned_data.get('middle_name', '').strip()
        if middle_name and not middle_name.replace(' ', '').isalpha():
            raise forms.ValidationError("Отчество должно содержать только буквы и пробелы")
        return middle_name
    
    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if not birth_date:
            raise forms.ValidationError("Дата рождения обязательна")
        
        from datetime import date
        today = date.today()
        
        # Проверка: дата не может быть в будущем
        if birth_date > today:
            raise forms.ValidationError("Дата рождения не может быть в будущем")
        
        # Вычисляем возраст
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        
        # Проверка: минимальный возраст 0 лет (новорожденный)
        if age < 0:
            raise forms.ValidationError("Некорректная дата рождения")
        
        # Проверка: максимальный возраст 120 лет
        if age > 120:
            raise forms.ValidationError("Проверьте корректность даты рождения (возраст не может превышать 120 лет)")
        
        # Дополнительная проверка: дата не раньше 1900 года
        if birth_date.year < 1900:
            raise forms.ValidationError("Дата рождения должна быть не ранее 1900 года")
        
        return birth_date
    
    def clean_allergy(self):
        allergy = self.cleaned_data.get('allergy', '').strip()
        return allergy


class DoctorCodeForm(forms.Form):
    """Форма для ввода кода врача"""
    code = forms.CharField(
        max_length=10,
        label="Код доступа врача",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш код доступа',
            'autocomplete': 'off'
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code:
            raise forms.ValidationError("Введите код доступа")
        
        doctor = Doctor.authenticate_by_code(code)
        if not doctor:
            raise forms.ValidationError("Неверный код доступа или врач не активен")
        
        return code


class DoctorLoginForm(forms.Form):
    """Форма входа для врача по коду"""
    code = forms.CharField(
        max_length=10,
        label="Код доступа",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите ваш код доступа',
            'autocomplete': 'current-password',
            'autofocus': True
        })
    )
    
    def clean_code(self):
        code = self.cleaned_data.get('code', '').strip()
        if not code:
            raise forms.ValidationError("Введите код доступа")
        
        doctor = Doctor.authenticate_by_code(code)
        if not doctor:
            raise forms.ValidationError("Неверный код доступа. Проверьте правильность ввода.")
        
        return code