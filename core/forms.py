from django import forms

from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["name", "role", "rating", "content"]
        widgets = {
            "rating": forms.Select(choices=[(number, f"{number}/5") for number in range(1, 6)]),
            "content": forms.Textarea(attrs={"rows": 4}),
        }