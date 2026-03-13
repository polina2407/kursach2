from django import forms
from .models import Patient


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
                'placeholder': 'Введите фамилию'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите отчество'
            }),
            'birth_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
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