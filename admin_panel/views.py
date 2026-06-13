from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.core.paginator import Paginator
from accounts.decorators import admin_required
from accounts.forms import StudentCreationForm, StudentEditForm, TeacherCreationForm, TeacherEditForm, FaceEnrollmentForm
from accounts.models import CustomUser, StudentProfile, TeacherProfile
from academics.models import Department, Course, Subject
from academics.forms import DepartmentForm, CourseForm, SubjectForm
import os
import uuid
from attendance.face_utils import encode_face_from_multiple, save_encoding
from django.conf import settings

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

@admin_required
def academics_overview(request):
    departments = Department.objects.select_related('head_of_dept').order_by('name')
    courses = Course.objects.select_related('department').order_by('department__name', 'name')

    dept_search = request.GET.get('dept_search', '').strip()
    course_search = request.GET.get('course_search', '').strip()

    if dept_search:
        departments = departments.filter(name__icontains=dept_search)
    if course_search:
        courses = courses.filter(name__icontains=course_search)

    return render(request, 'admin_panel/academics_overview.html', {
        'departments': departments,
        'courses': courses,
        'dept_search': dept_search,
        'course_search': course_search,
    })


@admin_required
def department_add(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{form.cleaned_data["name"]}" created successfully.')
            return redirect('admin_panel:academics_overview')
    else:
        form = DepartmentForm()
    return render(request, 'admin_panel/department_form.html', {
        'form': form,
        'form_title': 'Add Department',
        'submit_label': 'Create Department',
    })


@admin_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{department.name}" updated successfully.')
            return redirect('admin_panel:academics_overview')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'admin_panel/department_form.html', {
        'form': form,
        'form_title': f'Edit Department — {department.name}',
        'submit_label': 'Save Changes',
        'department': department,
    })


@admin_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        name = department.name
        course_count = department.course_set.count()
        if course_count > 0:
            messages.error(request, f'Cannot delete "{name}". It has {course_count} course(s) assigned. Remove or reassign them first.')
            return redirect('admin_panel:academics_overview')
        department.delete()
        messages.success(request, f'Department "{name}" deleted successfully.')
        return redirect('admin_panel:academics_overview')
    return render(request, 'admin_panel/confirm_delete.html', {
        'object_name': department.name,
        'object_type': 'Department',
        'cancel_url': 'admin_panel:academics_overview',
    })


@admin_required
def course_add(request):
    if request.method == 'POST':
        form = CourseForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{form.cleaned_data["name"]}" created successfully.')
            return redirect('admin_panel:academics_overview')
    else:
        form = CourseForm()
    return render(request, 'admin_panel/course_form.html', {
        'form': form,
        'form_title': 'Add Course',
        'submit_label': 'Create Course',
    })


@admin_required
def course_edit(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        form = CourseForm(request.POST, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, f'Course "{course.name}" updated successfully.')
            return redirect('admin_panel:academics_overview')
    else:
        form = CourseForm(instance=course)
    return render(request, 'admin_panel/course_form.html', {
        'form': form,
        'form_title': f'Edit Course — {course.name}',
        'submit_label': 'Save Changes',
        'course': course,
    })


@admin_required
def course_delete(request, pk):
    course = get_object_or_404(Course, pk=pk)
    if request.method == 'POST':
        name = course.name
        subject_count = course.subject_set.count()
        if subject_count > 0:
            messages.error(request, f'Cannot delete "{name}". It has {subject_count} subject(s) assigned. Remove them first.')
            return redirect('admin_panel:academics_overview')
        course.delete()
        messages.success(request, f'Course "{name}" deleted successfully.')
        return redirect('admin_panel:academics_overview')
    return render(request, 'admin_panel/confirm_delete.html', {
        'object_name': course.name,
        'object_type': 'Course',
        'cancel_url': 'admin_panel:academics_overview',
    })


@admin_required
def subjects_list(request):
    course_filter = request.GET.get('course_filter', '').strip()
    search = request.GET.get('search', '').strip()

    subjects = Subject.objects.select_related('course', 'course__department', 'teacher').order_by(
        'course__department__name', 'course__name', 'semester', 'name'
    )

    if course_filter:
        subjects = subjects.filter(course__id=course_filter)
    if search:
        subjects = subjects.filter(name__icontains=search) | subjects.filter(code__icontains=search)

    courses = Course.objects.select_related('department').order_by('department__name', 'name')

    course_filter_int = int(course_filter) if course_filter else None

    course_choices = []
    for course in courses:
        course_choices.append({
            'course': course,
            'is_selected': course.pk == course_filter_int,
        })

    grouped = {}
    for subject in subjects:
        key = subject.course.pk
        if key not in grouped:
            grouped[key] = {
                'course': subject.course,
                'subjects': [],
            }
        grouped[key]['subjects'].append(subject)

    grouped_list = list(grouped.values())

    return render(request, 'admin_panel/subjects_list.html', {
        'grouped_list': grouped_list,
        'course_choices': course_choices,
        'search': search,
        'course_filter': course_filter,
        'total_count': sum(len(g['subjects']) for g in grouped_list),
    })


@admin_required
def subject_add(request):
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save()
            messages.success(request, f'Subject "{subject.name}" created successfully.')
            return redirect('admin_panel:subjects_list')
    else:
        course_pk = request.GET.get('course')
        initial = {}
        if course_pk:
            try:
                initial['course'] = Course.objects.get(pk=course_pk)
            except Course.DoesNotExist:
                pass
        form = SubjectForm(initial=initial)
    return render(request, 'admin_panel/subject_form.html', {
        'form': form,
        'form_title': 'Add Subject',
        'submit_label': 'Create Subject',
    })


@admin_required
def subject_edit(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            messages.success(request, f'Subject "{subject.name}" updated successfully.')
            return redirect('admin_panel:subjects_list')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'admin_panel/subject_form.html', {
        'form': form,
        'form_title': f'Edit Subject — {subject.name}',
        'submit_label': 'Save Changes',
        'subject': subject,
    })


@admin_required
def subject_delete(request, pk):
    subject = get_object_or_404(Subject, pk=pk)
    if request.method == 'POST':
        name = subject.name
        subject.delete()
        messages.success(request, f'Subject "{name}" deleted successfully.')
        return redirect('admin_panel:subjects_list')
    return redirect('admin_panel:subjects_list')

@admin_required
def enroll_face_view(request, pk):
    student = get_object_or_404(CustomUser, pk=pk, role='student')
    profile = get_object_or_404(StudentProfile, user=student)
    already_enrolled = bool(profile.face_encoding)

    if request.method == 'POST':
        form = FaceEnrollmentForm(request.POST, request.FILES)
        if form.is_valid():
            image_fields = ['image1', 'image2', 'image3', 'image4', 'image5']
            saved_paths = []
            enroll_dir = os.path.join(settings.MEDIA_ROOT, 'face_images', str(student.pk))
            os.makedirs(enroll_dir, exist_ok=True)

            for field in image_fields:
                img = form.cleaned_data.get(field)
                if img:
                    ext = os.path.splitext(img.name)[1].lower()
                    filename = f"{uuid.uuid4().hex}{ext}"
                    path = os.path.join(enroll_dir, filename)
                    with open(path, 'wb+') as f:
                        for chunk in img.chunks():
                            f.write(chunk)
                    saved_paths.append(path)

            encoding = encode_face_from_multiple(saved_paths)

            if encoding is None:
                messages.error(request, 'No face detected in the uploaded photos. Please upload clear front-facing photos.')
            else:
                success = save_encoding(student.pk, encoding)
                if success:
                    messages.success(request, f'Face enrolled successfully for {student.get_full_name() or student.username}.')
                    return redirect('admin_panel:students_list')
                else:
                    messages.error(request, 'Failed to save encoding. Student profile not found.')
    else:
        form = FaceEnrollmentForm()

    return render(request, 'admin_panel/enroll_face.html', {
        'form': form,
        'student': student,
        'profile': profile,
        'already_enrolled': already_enrolled,
    })