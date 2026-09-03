from django.contrib import admin

# Marketing/static pages (home, about) have no models of their own.
# Domain models live in their respective apps:
#   - accounts.Student / accounts.Company
#   - jobs.Job / jobs.Application
