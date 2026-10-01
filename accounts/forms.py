import re

from django import forms

from .models import Company, CustomUser
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

USERNAME_RE = re.compile(r"[A-Za-z0-9._-]{3,30}")

SEMESTER_CHOICES = [(str(number), str(number)) for number in range(1, 10)]


def validate_pdf(upload):
    if upload and not upload.name.lower().endswith(".pdf"):
        raise forms.ValidationError("The resume must be a PDF file.")
    return upload


class UsernameFieldMixin:
    """Validates `username`: 3-30 chars (letters, digits, . _ -), unique ignoring case."""

    def __init__(self, *args, user_id=None, **kwargs):
        self.user_id = user_id
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            return ""
        if not USERNAME_RE.fullmatch(username):
            raise forms.ValidationError(
                "Username must have 3-30 characters: letters, numbers, dots, dashes or underscores."
            )
        taken = CustomUser.objects.filter(username__iexact=username)
        if self.user_id:
            taken = taken.exclude(id=self.user_id)
        if taken.exists():
            raise forms.ValidationError("That username is already taken.")
        return username


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


class StudentRegisterForm(UsernameFieldMixin, StudentFieldsForm):
    name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=30)
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

class CompanyRegisterForm(UsernameFieldMixin, forms.Form):
    company_name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=30)
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
    identifier = forms.CharField(max_length=150, label="Email or username")
    password = forms.CharField(widget=forms.PasswordInput)


class StudentProfileForm(UsernameFieldMixin, StudentFieldsForm):
    name = forms.CharField(max_length=150)
    username = forms.CharField(max_length=30, required=False)
    university = forms.CharField(max_length=150)
    semester = forms.ChoiceField(choices=SEMESTER_CHOICES)
    skills = forms.CharField(max_length=500, required=False)
    certifications = forms.CharField(max_length=500, required=False)

class CompanyProfileForm(UsernameFieldMixin, forms.Form):
    company_name = forms.CharField(max_length=150, label="Company Name")
    username = forms.CharField(max_length=30, required=False)
    profile_photo = forms.ImageField(required=False)
