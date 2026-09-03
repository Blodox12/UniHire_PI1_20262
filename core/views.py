from django.shortcuts import render

# ---------------------------------------------------------------------------
# Public marketing pages
# ---------------------------------------------------------------------------


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")
