from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import transaction
from accounts.decorators import teacher_required
from accounts.models import CustomUser
from academics.models import Subject
from .models import Attendance
from .forms import AttendanceSelectionForm
from django.utils import timezone


@teacher_required
def mark_attendance(request):
    teacher = request.user

    if request.method == 'POST' and 'submit_attendance' in request.POST:
        subject_id = request.POST.get('subject_id')
        date = request.POST.get('date')
        subject = Subject.objects.filter(id=subject_id, teacher=teacher).first()

        if not subject:
            messages.error(request, 'Invalid subject selected.')
            return redirect('attendance:mark_attendance')

        students = CustomUser.objects.filter(
            role='student',
            student_profile__course=subject.course,
            student_profile__current_semester=subject.semester,
            is_active=True,
        ).select_related('student_profile')

        if not students.exists():
            messages.warning(request, 'No enrolled students found for this subject and semester.')
            return redirect('attendance:mark_attendance')

        try:
            with transaction.atomic():
                for student in students:
                    status_key = f'status_{student.id}'
                    status = request.POST.get(status_key, 'Absent')
                    if status not in ['Present', 'Absent', 'Late']:
                        status = 'Absent'

                    Attendance.objects.update_or_create(
                        student=student,
                        subject=subject,
                        date=date,
                        defaults={
                            'status': status,
                            'method': 'manual',
                            'marked_by': teacher,
                        },
                    )
            messages.success(request, f'Attendance saved successfully for {subject.name} on {date}.')
            return redirect('attendance:mark_attendance')

        except Exception as e:
            messages.error(request, f'Error saving attendance: {str(e)}')
            return redirect('attendance:mark_attendance')

    selection_form = AttendanceSelectionForm(teacher=teacher)
    subject = None
    students = []
    date = timezone.now().date()

    if request.method == 'POST' and 'load_students' in request.POST:
        selection_form = AttendanceSelectionForm(teacher=teacher, data=request.POST)
        if selection_form.is_valid():
            subject = selection_form.cleaned_data['subject']
            date = selection_form.cleaned_data['date']

            students = list(CustomUser.objects.filter(
                role='student',
                student_profile__course=subject.course,
                student_profile__current_semester=subject.semester,
                is_active=True,
            ).select_related('student_profile').order_by('student_profile__roll_no'))

            records = Attendance.objects.filter(
                subject=subject,
                date=date,
            )
            existing_records = {r.student_id: r.status for r in records}

            for student in students:
                student.attendance_status = existing_records.get(student.id, 'Present')

            if not students:
                messages.warning(request, 'No students enrolled in this subject for the current semester.')

    return render(request, 'attendance/mark_attendance.html', {
        'selection_form': selection_form,
        'subject': subject,
        'students': students,
        'date': date,
    })