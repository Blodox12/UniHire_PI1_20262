from django.db import models

# `core` only serves marketing/static pages (home, about) and the shared
# base template, so it has no models of its own.
#
# Domain models live in their respective apps:
#   - accounts.Student / accounts.Company
#   - jobs.Job / jobs.Application
