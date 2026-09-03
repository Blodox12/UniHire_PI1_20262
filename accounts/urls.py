from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/student/", views.register_student, name="register_student"),
    path("register/company/", views.register_company, name="register_company"),
    path("profile/", views.profile_view, name="profile"),
]
