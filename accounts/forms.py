from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, StudentProfile, TeacherProfile


class StudentCreationForm(forms.Form):
    # User fields
    first_name = forms.CharField(max_length=150, label='First Name')
    last_name = forms.CharField(max_length=150, label='Last Name')
    username = forms.CharField(max_length=150, label='Username')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=15, required=False, label='Phone')
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Password',
        validators=[validate_password],
    )
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    profile_pic = forms.ImageField(required=False, label='Profile Picture')

    # StudentProfile fields
    roll_no = forms.CharField(max_length=20, label='Roll Number')
    course = forms.ModelChoiceField(
        queryset=None,
        label='Course',
        empty_label='-- Select Course --',
    )
    current_semester = forms.IntegerField(min_value=1, max_value=12, initial=1, label='Current Semester')
    batch_year = forms.IntegerField(min_value=2000, max_value=2100, label='Batch Year')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Address')
    guardian_name = forms.CharField(max_length=100, required=False, label='Guardian Name')
    guardian_phone = forms.CharField(max_length=15, required=False, label='Guardian Phone')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from academics.models import Course
        self.fields['course'].queryset = Course.objects.select_related('department').all()
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['profile_pic'].widget.attrs['class'] = 'form-control'

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_roll_no(self):
        roll_no = self.cleaned_data['roll_no']
        if StudentProfile.objects.filter(roll_no=roll_no).exists():
            raise forms.ValidationError('This roll number is already assigned.')
        return roll_no

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data
    
class StudentEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='First Name')
    last_name = forms.CharField(max_length=150, label='Last Name')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=15, required=False, label='Phone')
    profile_pic = forms.ImageField(required=False, label='Profile Picture')
    is_active = forms.BooleanField(required=False, label='Active')

    roll_no = forms.CharField(max_length=20, label='Roll Number')
    course = forms.ModelChoiceField(
        queryset=None,
        label='Course',
        empty_label='-- Select Course --',
    )
    current_semester = forms.IntegerField(min_value=1, max_value=12, label='Current Semester')
    batch_year = forms.IntegerField(min_value=2000, max_value=2100, label='Batch Year')
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Address')
    guardian_name = forms.CharField(max_length=100, required=False, label='Guardian Name')
    guardian_phone = forms.CharField(max_length=15, required=False, label='Guardian Phone')

    def __init__(self, *args, **kwargs):
        self.student_profile = kwargs.pop('student_profile', None)
        super().__init__(*args, **kwargs)
        from academics.models import Course
        self.fields['course'].queryset = Course.objects.select_related('department').all()
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = CustomUser.objects.filter(email=email)
        if self.student_profile:
            qs = qs.exclude(pk=self.student_profile.user.pk)
        if qs.exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_roll_no(self):
        roll_no = self.cleaned_data['roll_no']
        qs = StudentProfile.objects.filter(roll_no=roll_no)
        if self.student_profile:
            qs = qs.exclude(pk=self.student_profile.pk)
        if qs.exists():
            raise forms.ValidationError('This roll number is already assigned.')
        return roll_no

class TeacherCreationForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='First Name')
    last_name = forms.CharField(max_length=150, label='Last Name')
    username = forms.CharField(max_length=150, label='Username')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=15, required=False, label='Phone')
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        label='Password',
        validators=[validate_password],
    )
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    profile_pic = forms.ImageField(required=False, label='Profile Picture')

    employee_id = forms.CharField(max_length=20, label='Employee ID')
    department = forms.ModelChoiceField(
        queryset=None,
        label='Department',
        empty_label='-- Select Department --',
    )
    designation = forms.CharField(max_length=100, required=False, label='Designation')
    joining_date = forms.DateField(
        required=False,
        label='Joining Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    qualification = forms.CharField(max_length=200, required=False, label='Qualification')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from academics.models import Department
        self.fields['department'].queryset = Department.objects.all()
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if TeacherProfile.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError('This employee ID is already assigned.')
        return employee_id

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data


class TeacherEditForm(forms.Form):
    first_name = forms.CharField(max_length=150, label='First Name')
    last_name = forms.CharField(max_length=150, label='Last Name')
    email = forms.EmailField(label='Email')
    phone = forms.CharField(max_length=15, required=False, label='Phone')
    profile_pic = forms.ImageField(required=False, label='Profile Picture')
    is_active = forms.BooleanField(required=False, label='Active')

    employee_id = forms.CharField(max_length=20, label='Employee ID')
    department = forms.ModelChoiceField(
        queryset=None,
        label='Department',
        empty_label='-- Select Department --',
    )
    designation = forms.CharField(max_length=100, required=False, label='Designation')
    joining_date = forms.DateField(
        required=False,
        label='Joining Date',
        widget=forms.DateInput(attrs={'type': 'date'}),
    )
    qualification = forms.CharField(max_length=200, required=False, label='Qualification')

    def __init__(self, *args, **kwargs):
        self.teacher_profile = kwargs.pop('teacher_profile', None)
        super().__init__(*args, **kwargs)
        from academics.models import Department
        self.fields['department'].queryset = Department.objects.all()
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')
        self.fields['is_active'].widget.attrs['class'] = 'form-check-input'

    def clean_email(self):
        email = self.cleaned_data['email']
        qs = CustomUser.objects.filter(email=email)
        if self.teacher_profile:
            qs = qs.exclude(pk=self.teacher_profile.user.pk)
        if qs.exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        qs = TeacherProfile.objects.filter(employee_id=employee_id)
        if self.teacher_profile:
            qs = qs.exclude(pk=self.teacher_profile.pk)
        if qs.exists():
            raise forms.ValidationError('This employee ID is already assigned.')
        return employee_id