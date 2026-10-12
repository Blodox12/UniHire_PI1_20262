from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def login_required(role=None):
    """Session-based login guard (replaces the JWT + localStorage flow used by
    the previous React SPA)."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.session.get("user_id"):
                messages.error(request, "Please log in to continue.")
                return redirect("accounts:login")
            if role and request.session.get("role") != role:
                messages.error(request, "You do not have access to that page.")
                return redirect(
                    "jobs:company_dashboard"
                    if request.session.get("role") == "company"
                    else "jobs:student_dashboard"
                )
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def approved_company_required(view_func):
    """Only lets companies approved by an administrator through. Pending or
    rejected companies are sent back to their dashboard with a notice."""

    @login_required(role="company")
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from .utils import current_company

        company = current_company(request)
        if not company or not company.is_approved:
            if company and company.verification_status == company.STATUS_REJECTED:
                messages.error(request, "Your company account was rejected. You cannot perform this action.")
            else:
                messages.error(request, "Your company account is under review. You will be able to do this once an administrator approves it.")
            return redirect("jobs:company_dashboard")
        return view_func(request, *args, **kwargs)

    return wrapper
