from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from .models import Department, Room, Patient, Doctor, DischargeHistory
from .forms import PatientForm, DoctorCodeForm, DoctorLoginForm
from datetime import date


def create_hospital_structure():
    """Создание начальной структуры больницы: 4 отделения по 10 палат"""
    if Department.objects.exists():
        return

    departments_data = [
        "Хирургическое", "Терапевтическое",
        "Неврологическое", "Кардиологическое"
    ]

    for dep_name in departments_data:
        department = Department.objects.create(name=dep_name)
        for i in range(1, 11):
            Room.objects.create(department=department, number=i, capacity=4)


def is_compatible(patient, room):
    """Проверка совместимости пациента с палатой
    - Нельзя размещать мужчин и женщин вместе
    - Нельзя размещать взрослых и детей вместе
    """
    if room.is_full():
        return False

    patients_in_room = room.patient_set.all()

    if not patients_in_room.exists():
        return True

    first_patient = patients_in_room.first()
    
    # Проверка по полу
    if first_patient.gender != patient.gender:
        return False

    # Проверка по возрастной категории
    for p in patients_in_room:
        # Взрослые (adult) не могут быть с детьми (child)
        if p.age_category == 'adult' and patient.age_category == 'child':
            return False
        if p.age_category == 'child' and patient.age_category == 'adult':
            return False

    return True


def find_optimal_room(patient):
    """Автоматический поиск подходящей палаты"""
    rooms = Room.objects.filter(department=patient.department).order_by('number')

    # Сначала ищем палату с пациентами той же категории
    for room in rooms:
        if is_compatible(patient, room):
            patients_in_room = room.patient_set.all()
            if patients_in_room.exists():
                same_category = any(p.age_category == patient.age_category for p in patients_in_room)
                if same_category:
                    return room

    # Если не нашли, ищем просто совместимую палату
    for room in rooms:
        if is_compatible(patient, room):
            return room

    return None


def index(request):
    create_hospital_structure()

    search_query = request.GET.get('search', '').strip()

    departments = Department.objects.all().prefetch_related('room_set', 'room_set__patient_set')

    total_rooms = Room.objects.count()
    total_capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0
    total_patients = Patient.objects.count()
    hospital_fill = int((total_patients / total_capacity) * 100) if total_capacity > 0 else 0

    found_patients = []

    for dep in departments:
        rooms_in_dep = Room.objects.filter(department=dep)
        dep.total_capacity = sum(r.capacity for r in rooms_in_dep)

        if search_query:
            dep_patients = Patient.objects.filter(
                room__department=dep
            ).filter(
                Q(last_name__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(middle_name__icontains=search_query) |
                Q(room__number__icontains=search_query)
            ).select_related('room')

            for patient in dep_patients:
                found_patients.append({
                    'patient': patient,
                    'department': dep,
                })
        else:
            dep_patients = Patient.objects.filter(room__department=dep).select_related('room')

        dep.patient_count = dep_patients.count()
        dep.fill_percent = int((dep.patient_count / dep.total_capacity) * 100) if dep.total_capacity > 0 else 0
        dep.patients = dep_patients

    context = {
        "departments": departments,
        "hospital_fill": hospital_fill,
        "total_patients": total_patients,
        "total_capacity": total_capacity,
        "search_query": search_query,
        "found_patients": found_patients,
    }
    return render(request, "index.html", context)


def doctor_login(request):
    """Вход врача по коду доступа"""
    if request.method == 'POST':
        form = DoctorLoginForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            doctor = Doctor.authenticate_by_code(code)
            
            if doctor:
                # Сохраняем ID врача в сессии
                request.session['doctor_id'] = doctor.id
                messages.success(request, f"✅ Добро пожаловать, {doctor.user.get_full_name() or doctor.user.username}!")
                return redirect('index')
    else:
        form = DoctorLoginForm()
    
    return render(request, 'doctor_login.html', {'form': form})


@login_required
def add_patient(request):
    """Добавление пациента с проверкой кода врача"""
    doctor = None
    
    # Проверяем, есть ли врач в сессии
    if request.session.get('doctor_id'):
        try:
            doctor = Doctor.objects.get(id=request.session['doctor_id'], is_active=True)
        except Doctor.DoesNotExist:
            del request.session['doctor_id']
    
    if request.method == "POST":
        # Если врач еще не аутентифицирован, проверяем код
        if not doctor:
            code_form = DoctorCodeForm(request.POST)
            if code_form.is_valid():
                doctor = Doctor.authenticate_by_code(code_form.cleaned_data['code'])
                if doctor:
                    request.session['doctor_id'] = doctor.id
                else:
                    messages.error(request, f"❌ Ошибка кода: Неверный код доступа")
                    return render(request, "add_patient.html", {"form": PatientForm(), "code_form": code_form})
            else:
                messages.error(request, f"❌ Ошибка кода: {code_form.errors.get('code', ['Неверный код'])[0]}")
                return render(request, "add_patient.html", {"form": PatientForm(), "code_form": code_form})
        
        # Если код верный, обрабатываем форму пациента
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.admitted_by = doctor
            patient.save()
            messages.success(request, f"✅ Пациент {patient.last_name} {patient.first_name} зарегистрирован")
            return redirect("select_room", patient_id=patient.id)
        else:
            messages.error(request, "❌ Исправьте ошибки в форме пациента")
    else:
        form = PatientForm()
        code_form = DoctorCodeForm()
        dep_id = request.GET.get('department')
        if dep_id:
            form.fields['department'].initial = dep_id

    return render(request, "add_patient.html", {"form": form, "code_form": code_form, "doctor": doctor})


@login_required
def select_room(request, patient_id):
    """Выбор палаты для пациента"""
    patient = get_object_or_404(Patient, id=patient_id)
    rooms = Room.objects.filter(department=patient.department).prefetch_related('patient_set')

    if request.method == "POST":
        mode = request.POST.get("mode")

        if mode == "auto":
            room = find_optimal_room(patient)
            if room:
                patient.room = room
                patient.save()
                messages.success(request, f"✅ Пациент автоматически размещён в палате {room.number}")
                return redirect("index")
            else:
                messages.error(request, "❌ В отделении нет свободных подходящих мест!")
                return redirect("index")

        if mode == "manual":
            room_id = request.POST.get("room_id")
            if room_id:
                try:
                    room = get_object_or_404(Room, id=room_id)
                    if room.is_full():
                        messages.error(request, f"❌ Палата {room.number} заполнена!")
                        return redirect("select_room", patient_id=patient.id)
                    elif not is_compatible(patient, room):
                        messages.error(request, f"❌ В палату {room.number} нельзя заселить (несовместимость)!")
                        return redirect("select_room", patient_id=patient.id)
                    else:
                        patient.room = room
                        patient.save()
                        messages.success(request, f"✅ Пациент размещён в палате {room.number}")
                        return redirect("index")
                except Exception as e:
                    messages.error(request, f"❌ Ошибка: {str(e)}")
                    return redirect("select_room", patient_id=patient.id)


    rooms_info = []
    for room in rooms:
        patients_in_room = room.patient_set.all()
        is_full = patients_in_room.count() >= room.capacity
        compatible = is_compatible(patient, room)

        rooms_info.append({
            'room': room,
            'full': is_full,
            'compatible': compatible,
            'patients': patients_in_room,
            'free_spots': room.capacity - patients_in_room.count()
        })

    context = {
        "patient": patient,
        "rooms_info": rooms_info
    }
    return render(request, "select_room.html", context)


@login_required
def discharge_patient(request, patient_id):
    """Выписка пациента с проверкой кода врача"""
    patient = get_object_or_404(Patient, id=patient_id)
    doctor = None

    # Проверяем, есть ли врач в сессии
    if request.session.get('doctor_id'):
        try:
            doctor = Doctor.objects.get(id=request.session['doctor_id'], is_active=True)
        except Doctor.DoesNotExist:
            del request.session['doctor_id']

    if request.method == "POST":
        # Если врач еще не аутентифицирован, проверяем код
        if not doctor:
            code_form = DoctorCodeForm(request.POST)
            if code_form.is_valid():
                doctor = Doctor.authenticate_by_code(code_form.cleaned_data['code'])
                if doctor:
                    request.session['doctor_id'] = doctor.id
                else:
                    messages.error(request, f"❌ Ошибка кода: Неверный код доступа")
                    return render(request, "discharge_patient.html", {"patient": patient, "code_form": code_form})
            else:
                messages.error(request, f"❌ Ошибка кода: {code_form.errors.get('code', ['Неверный код'])[0]}")
                return render(request, "discharge_patient.html", {"patient": patient, "code_form": code_form})

        disease = request.POST.get('diagnosis', 'Не указано')

        DischargeHistory.objects.create(
            patient_name=f"{patient.last_name} {patient.first_name}",
            department=patient.department.name,
            room_number=patient.room.number if patient.room else 0,
            date_admitted=patient.admission_date.date() if patient.admission_date else date.today(),
            disease=disease,
            discharged_by=doctor
        )

        patient.delete()
        messages.success(request, "✅ Пациент выписан")
        return redirect("index")
    else:
        code_form = DoctorCodeForm()

    return render(request, "discharge_patient.html", {"patient": patient, "code_form": code_form, "doctor": doctor})


def room_status(request):
    """Просмотр состояния палат"""
    dep_id = request.GET.get('department')

    if dep_id:
        departments = Department.objects.filter(id=dep_id).prefetch_related('room_set__patient_set')
    else:
        departments = Department.objects.all().prefetch_related('room_set__patient_set')

    total_rooms = Room.objects.count()
    total_capacity = Room.objects.aggregate(total=Sum('capacity'))['total'] or 0
    total_patients = Patient.objects.count()
    
    occupied_rooms = Room.objects.annotate(patient_count=Count('patient')).filter(patient_count__gt=0).count()
    full_rooms = Room.objects.annotate(
        patient_count=Count('patient')
    ).filter(
        patient_count__gte=4
    ).count()
    empty_rooms = Room.objects.annotate(patient_count=Count('patient')).filter(patient_count=0).count()
    partial_rooms = occupied_rooms - full_rooms

    departments_stats = []
    for dep in departments:
        rooms = Room.objects.filter(department=dep).prefetch_related('patient_set')
        dep_total_patients = Patient.objects.filter(room__department=dep).count()
        dep_total_capacity = sum(r.capacity for r in rooms)
        dep_fill_percent = int((dep_total_patients / dep_total_capacity) * 100) if dep_total_capacity > 0 else 0

        departments_stats.append({
            'department': dep,
            'rooms': rooms,
            'total_patients': dep_total_patients,
            'total_capacity': dep_total_capacity,
            'fill_percent': dep_fill_percent,
        })

    context = {
        'departments_stats': departments_stats,
        'total_rooms': total_rooms,
        'total_capacity': total_capacity,
        'total_patients': total_patients,
        'occupied_rooms': occupied_rooms,
        'full_rooms': full_rooms,
        'empty_rooms': empty_rooms,
        'partial_rooms': partial_rooms,
        'selected_department': dep_id,
    }
    return render(request, "room_status.html", context)


def patient_detail(request, patient_id):
    """Подробная информация о пациенте"""
    patient = get_object_or_404(Patient, id=patient_id)

    context = {
        'patient': patient,
    }
    return render(request, "patient_detail.html", context)