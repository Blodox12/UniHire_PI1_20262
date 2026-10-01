from django import forms

from .models import Job

MAX_RESUME_SIZE = 5 * 1024 * 1024  # 5 MB


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "required_skills", "location", "job_type"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ResumeForm(forms.Form):
    resume = forms.FileField(label="Resume (PDF)")

    def clean_resume(self):
        upload = self.cleaned_data["resume"]
        if not upload.name.lower().endswith(".pdf"):
            raise forms.ValidationError("The resume must be a PDF file.")
        if upload.size > MAX_RESUME_SIZE:
            raise forms.ValidationError("The PDF is too large (maximum 5 MB).")
        if upload.read(5) != b"%PDF-":
            raise forms.ValidationError("This file is not a valid PDF.")
        upload.seek(0)
        return upload
