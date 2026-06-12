from django import forms
from academics.models import Subject
from django.utils import timezone


class AttendanceSelectionForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.none(),
        empty_label="Select Subject",
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    date = forms.DateField(
        initial=timezone.now().date,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )

    def __init__(self, teacher, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].queryset = Subject.objects.filter(
            teacher=teacher
        ).select_related('course')