from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from accounts.decorators import admin_required
from accounts.forms import StudentCreationForm, StudentEditForm, TeacherCreationForm, TeacherEditForm
from accounts.models import CustomUser, StudentProfile, TeacherProfile
from academics.models import Department


@admin_required
def dashboard(request):
    return render(request, 'admin_panel/dashboard.html')


@admin_required
def students_list(request):
    query = request.GET.get('q', '').strip()
    students = StudentProfile.objects.select_related('user', 'course').all()
    if query:
        students = students.filter(
            roll_no__icontains=query
        ) | students.filter(
            user__first_name__icontains=query
        ) | students.filter(
            user__last_name__icontains=query
        ) | students.filter(
            user__username__icontains=query
        )
    students = students.order_by('roll_no')
    paginator = Paginator(students, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_panel/students_list.html', {
        'page_obj': page_obj,
        'query': query,
        'total': paginator.count,
    })


@admin_required
def student_add(request):
    if request.method == 'POST':
        form = StudentCreationForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    user = CustomUser(
                        username=cd['username'],
                        email=cd['email'],
                        first_name=cd['first_name'],
                        last_name=cd['last_name'],
                        phone=cd.get('phone', ''),
                        role='student',
                        is_active=True,
                    )
                    user.set_password(cd['password1'])
                    if cd.get('profile_pic'):
                        user.profile_pic = cd['profile_pic']
                    user.save()
                    StudentProfile.objects.create(
                        user=user,
                        roll_no=cd['roll_no'],
                        course=cd['course'],
                        current_semester=cd['current_semester'],
                        batch_year=cd['batch_year'],
                        address=cd.get('address', ''),
                        guardian_name=cd.get('guardian_name', ''),
                        guardian_phone=cd.get('guardian_phone', ''),
                    )
                messages.success(request, f"Student account for {user.get_full_name() or user.username} created successfully.")
                return redirect('admin_panel:students_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = StudentCreationForm()
    return render(request, 'admin_panel/student_add.html', {'form': form})


@admin_required
def student_edit(request, pk):
    sp = get_object_or_404(StudentProfile, pk=pk)
    user = sp.user
    if request.method == 'POST':
        form = StudentEditForm(request.POST, request.FILES, student_profile=sp)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    user.first_name = cd['first_name']
                    user.last_name = cd['last_name']
                    user.email = cd['email']
                    user.phone = cd.get('phone', '')
                    user.is_active = cd.get('is_active', False)
                    if cd.get('profile_pic'):
                        user.profile_pic = cd['profile_pic']
                    user.save()
                    sp.roll_no = cd['roll_no']
                    sp.course = cd['course']
                    sp.current_semester = cd['current_semester']
                    sp.batch_year = cd['batch_year']
                    sp.address = cd.get('address', '')
                    sp.guardian_name = cd.get('guardian_name', '')
                    sp.guardian_phone = cd.get('guardian_phone', '')
                    sp.save()
                messages.success(request, f"Student {user.get_full_name() or user.username} updated successfully.")
                return redirect('admin_panel:students_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = StudentEditForm(
            student_profile=sp,
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'is_active': user.is_active,
                'roll_no': sp.roll_no,
                'course': sp.course,
                'current_semester': sp.current_semester,
                'batch_year': sp.batch_year,
                'address': sp.address,
                'guardian_name': sp.guardian_name,
                'guardian_phone': sp.guardian_phone,
            }
        )
    return render(request, 'admin_panel/student_edit.html', {'form': form, 'sp': sp})


@admin_required
def student_deactivate(request, pk):
    sp = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        sp.user.is_active = False
        sp.user.save()
        messages.success(request, f"Student {sp.user.get_full_name() or sp.user.username} has been deactivated.")
    return redirect('admin_panel:students_list')


@admin_required
def student_activate(request, pk):
    sp = get_object_or_404(StudentProfile, pk=pk)
    if request.method == 'POST':
        sp.user.is_active = True
        sp.user.save()
        messages.success(request, f"Student {sp.user.get_full_name() or sp.user.username} has been activated.")
    return redirect('admin_panel:students_list')

@admin_required
def teachers_list(request):
    query = request.GET.get('q', '').strip()
    dept_id = request.GET.get('dept', '')
    try:
        dept_id = int(dept_id)
    except (ValueError, TypeError):
        dept_id = ''
    departments = Department.objects.all()
    dept_choices = [
        {'obj': d, 'selected': d.pk == dept_id}
        for d in departments
    ]
    teachers = TeacherProfile.objects.select_related('user', 'department').all()
    if query:
        teachers = teachers.filter(
            employee_id__icontains=query
        ) | teachers.filter(
            user__first_name__icontains=query
        ) | teachers.filter(
            user__last_name__icontains=query
        ) | teachers.filter(
            user__username__icontains=query
        )
    if dept_id:
        teachers = teachers.filter(department_id=dept_id)
    teachers = teachers.order_by('employee_id')
    paginator = Paginator(teachers, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'admin_panel/teachers_list.html', {
        'page_obj': page_obj,
        'query': query,
        'dept_id': dept_id,
        'dept_choices': dept_choices,
        'total': paginator.count,
    })

@admin_required
def teacher_add(request):
    if request.method == 'POST':
        form = TeacherCreationForm(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    user = CustomUser(
                        username=cd['username'],
                        email=cd['email'],
                        first_name=cd['first_name'],
                        last_name=cd['last_name'],
                        phone=cd.get('phone', ''),
                        role='teacher',
                        is_active=True,
                    )
                    user.set_password(cd['password1'])
                    if cd.get('profile_pic'):
                        user.profile_pic = cd['profile_pic']
                    user.save()
                    TeacherProfile.objects.create(
                        user=user,
                        employee_id=cd['employee_id'],
                        department=cd['department'],
                        designation=cd.get('designation', ''),
                        joining_date=cd.get('joining_date'),
                        qualification=cd.get('qualification', ''),
                    )
                messages.success(request, f"Teacher account for {user.get_full_name() or user.username} created successfully.")
                return redirect('admin_panel:teachers_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = TeacherCreationForm()
    return render(request, 'admin_panel/teacher_add.html', {'form': form})


@admin_required
def teacher_edit(request, pk):
    tp = get_object_or_404(TeacherProfile, pk=pk)
    user = tp.user
    if request.method == 'POST':
        form = TeacherEditForm(request.POST, request.FILES, teacher_profile=tp)
        if form.is_valid():
            cd = form.cleaned_data
            try:
                with transaction.atomic():
                    user.first_name = cd['first_name']
                    user.last_name = cd['last_name']
                    user.email = cd['email']
                    user.phone = cd.get('phone', '')
                    user.is_active = cd.get('is_active', False)
                    if cd.get('profile_pic'):
                        user.profile_pic = cd['profile_pic']
                    user.save()
                    tp.employee_id = cd['employee_id']
                    tp.department = cd['department']
                    tp.designation = cd.get('designation', '')
                    tp.joining_date = cd.get('joining_date')
                    tp.qualification = cd.get('qualification', '')
                    tp.save()
                messages.success(request, f"Teacher {user.get_full_name() or user.username} updated successfully.")
                return redirect('admin_panel:teachers_list')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
    else:
        form = TeacherEditForm(
            teacher_profile=tp,
            initial={
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'phone': user.phone,
                'is_active': user.is_active,
                'employee_id': tp.employee_id,
                'department': tp.department,
                'designation': tp.designation,
                'joining_date': tp.joining_date,
                'qualification': tp.qualification,
            }
        )
    return render(request, 'admin_panel/teacher_edit.html', {'form': form, 'tp': tp})


@admin_required
def teacher_deactivate(request, pk):
    tp = get_object_or_404(TeacherProfile, pk=pk)
    if request.method == 'POST':
        tp.user.is_active = False
        tp.user.save()
        messages.success(request, f"Teacher {tp.user.get_full_name() or tp.user.username} has been deactivated.")
    return redirect('admin_panel:teachers_list')


@admin_required
def teacher_activate(request, pk):
    tp = get_object_or_404(TeacherProfile, pk=pk)
    if request.method == 'POST':
        tp.user.is_active = True
        tp.user.save()
        messages.success(request, f"Teacher {tp.user.get_full_name() or tp.user.username} has been activated.")
    return redirect('admin_panel:teachers_list')