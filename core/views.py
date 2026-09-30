from django.shortcuts import render

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
