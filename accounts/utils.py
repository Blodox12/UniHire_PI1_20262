from .models import Company, Student


def current_student(request):
    uid = request.session.get("user_id")
    if request.session.get("role") != "student" or not uid:
        return None
    return Student.objects.filter(id=uid).first()


def current_company(request):
    uid = request.session.get("user_id")
    if request.session.get("role") != "company" or not uid:
        return None
    return Company.objects.filter(id=uid).first()
