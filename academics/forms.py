from django import forms
from .models import Department, Course
from accounts.models import CustomUser


class DepartmentForm(forms.ModelForm):
    head_of_dept = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(role='teacher', is_active=True).order_by('first_name', 'last_name'),
        required=False,
        empty_label='-- Select Head of Department --',
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    class Meta:
        model = Department
        fields = ['name', 'code', 'head_of_dept']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Computer Science'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CS'}),
        }

    def __init__(self, *args, **kwargs):
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get('code', '').upper().strip()
        qs = Department.objects.filter(code__iexact=code)
        if self.instance_pk:
            qs = qs.exclude(pk=self.instance_pk)
        if qs.exists():
            raise forms.ValidationError('A department with this code already exists.')
        return code

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        qs = Department.objects.filter(name__iexact=name)
        if self.instance_pk:
            qs = qs.exclude(pk=self.instance_pk)
        if qs.exists():
            raise forms.ValidationError('A department with this name already exists.')
        return name


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['name', 'code', 'department', 'duration_years', 'total_semesters']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bachelor of Computer Applications'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. BCA'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'duration_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 6}),
            'total_semesters': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 12}),
        }

    def __init__(self, *args, **kwargs):
        self.instance_pk = kwargs.get('instance').pk if kwargs.get('instance') else None
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.all().order_by('name')
        self.fields['department'].empty_label = '-- Select Department --'

    def clean_code(self):
        code = self.cleaned_data.get('code', '').upper().strip()
        qs = Course.objects.filter(code__iexact=code)
        if self.instance_pk:
            qs = qs.exclude(pk=self.instance_pk)
        if qs.exists():
            raise forms.ValidationError('A course with this code already exists.')
        return code

    def clean(self):
        cleaned = super().clean()
        duration = cleaned.get('duration_years')
        semesters = cleaned.get('total_semesters')
        if duration and semesters:
            if semesters != duration * 2:
                pass
        return cleaned