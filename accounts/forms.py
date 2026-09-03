import re

from django import forms

EMAIL_RE = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")


class StudentRegisterForm(forms.Form):
    name = forms.CharField(max_length=150)
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=1)
    university = forms.CharField(max_length=150)
    career = forms.CharField(max_length=150)
    semester = forms.CharField(max_length=10)
    skills = forms.CharField(max_length=500, required=False)
    certifications = forms.CharField(max_length=500, required=False)
    resume_filename = forms.CharField(max_length=255, required=False)

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

    def clean_semester(self):
        semester = str(self.cleaned_data["semester"]).strip()
        if not semester.isdigit() or not (1 <= int(semester) <= 20):
            raise forms.ValidationError("Semester must be a number between 1 and 20")
        return semester


class CompanyRegisterForm(forms.Form):
    company_name = forms.CharField(max_length=150)
    email = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput, min_length=1)

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


class StudentProfileForm(forms.Form):
    name = forms.CharField(max_length=150)
    university = forms.CharField(max_length=150)
    career = forms.CharField(max_length=150)
    semester = forms.CharField(max_length=10)
    skills = forms.CharField(max_length=500, required=False)
    certifications = forms.CharField(max_length=500, required=False)
    resume_filename = forms.CharField(max_length=255, required=False)

    def clean_semester(self):
        semester = str(self.cleaned_data["semester"]).strip()
        if not semester.isdigit() or not (1 <= int(semester) <= 20):
            raise forms.ValidationError("Semester must be a number between 1 and 20")
        return semester


class CompanyProfileForm(forms.Form):
    company_name = forms.CharField(max_length=150, label="Company Name")
