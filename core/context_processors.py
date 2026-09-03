def session_user(request):
    return {
        "session_role": request.session.get("role"),
        "session_name": request.session.get("name"),
        "is_logged_in": bool(request.session.get("user_id")),
    }
