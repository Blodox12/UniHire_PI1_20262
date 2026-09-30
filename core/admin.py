from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
	list_display = ("name", "role", "rating", "created_at")
	list_filter = ("rating",)
from django.contrib import admin

# Marketing/static pages (home, about) have no models of their own.
# Domain models live in their respective apps:
#   - accounts.Student / accounts.Company
#   - jobs.Job / jobs.Application
