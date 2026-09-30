import re

from django import forms

from .models import Company
from .models import StudentDocument

EMAIL_RE = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")

EAFIT_CAREERS = [
    (career, career)
    for career in [
        "Administración de Negocios",
        "Contaduría Pública",
        "Derecho",
        "Economía",
        "Finanzas",
        "Geología",
        "Ingeniería Civil",
        "Ingeniería de Diseño de Producto",
        "Ingeniería de Procesos",
        "Ingeniería de Producción",
        "Ingeniería de Sistemas",
        "Ingeniería Física",
        "Ingeniería Matemática",
        "Ingeniería Mecánica",
        "Mercadeo",
        "Negocios Internacionales",
        "Psicología",
    ]
]

SEMESTER_CHOICES = [(str(number), str(number)) for number in range(1, 10)]


def validate_pdf(upload):
    if upload and not upload.name.lower().endswith(".pdf"):
        raise forms.ValidationError("The resume must be a PDF file.")
    return upload


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        single_clean = super().clean
        if not data:
            return []
        if not isinstance(data, list):
            data = [data]
        return [single_clean(item, initial) for item in data]


class StudentFieldsForm(forms.Form):
    career = forms.ChoiceField(choices=EAFIT_CAREERS)
    profile_photo = forms.ImageField(required=False)
    resume_filename = forms.FileField(required=False, validators=[validate_pdf])
    documents = MultipleFileField(required=False, label="Other documents")


class StudentRegisterForm(StudentFieldsForm):
    name = forms.CharField(max_length=150)
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=1)
    university = forms.CharField(max_length=150)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    skills = forms.CharField(max_length=500, required=False)
    certifications = forms.CharField(max_length=500, required=False)
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not EMAIL_RE.fullmatch(email):
            raise forms.ValidationError("Invalid email")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 6:
            raise forms.ValidationError("Password must contain at least 6 characters")
        return password

class CompanyRegisterForm(forms.Form):
    company_name = forms.CharField(max_length=150)
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=1)
    profile_photo = forms.ImageField(required=False)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not EMAIL_RE.fullmatch(email):
            raise forms.ValidationError("Invalid email")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 6:
            raise forms.ValidationError("Password must contain at least 6 characters")
        return password


class LoginForm(forms.Form):
    role = forms.ChoiceField(choices=[("student", "Student"), ("company", "Company")])
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class StudentProfileForm(StudentFieldsForm):
    name = forms.CharField(max_length=150)
    university = forms.CharField(max_length=150)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    skills = forms.CharField(max_length=500, required=False)
    certifications = forms.CharField(max_length=500, required=False)

class CompanyProfileForm(forms.Form):
    company_name = forms.CharField(max_length=150, label="Company Name")
    profile_photo = forms.ImageField(required=False)
