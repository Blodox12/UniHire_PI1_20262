from django.db import models

# `core` only serves marketing/static pages (home, about) and the shared
# base template, so it has no models of its own.
#
class Testimonial(models.Model):
	name = models.CharField(max_length=150)
	role = models.CharField(max_length=150)
	content = models.TextField(max_length=500)
	rating = models.PositiveSmallIntegerField(default=5)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"{self.name} - {self.rating}/5"
