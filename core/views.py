from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_GET

from .forms import TestimonialForm
from .models import Testimonial

# ---------------------------------------------------------------------------
# Public marketing pages
# ---------------------------------------------------------------------------


def home(request):
    if request.method == "POST":
        form = TestimonialForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, "core/home.html", {
                "form": TestimonialForm(),
                "testimonials": Testimonial.objects.all(),
                "testimonial_saved": True,
            })
    else:
        form = TestimonialForm()
    return render(request, "core/home.html", {
        "form": form,
        "testimonials": Testimonial.objects.all(),
    })


def about(request):
    return render(request, "core/about.html")


# ---------------------------------------------------------------------------
# Health check (NFR-03): lets an uptime monitor or the hosting platform detect
# when the site or its database is down and restart/alert automatically.
# ---------------------------------------------------------------------------


@never_cache
@require_GET
def health(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except DatabaseError:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse({"status": "ok", "database": "ok"})
