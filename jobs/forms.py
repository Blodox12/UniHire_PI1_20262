from django import forms

from .models import Job


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "required_skills", "location", "job_type"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }
