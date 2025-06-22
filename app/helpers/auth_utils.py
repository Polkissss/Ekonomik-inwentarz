from identity.flask import Auth
from functools import wraps
from flask import session, redirect, url_for


def check_first_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        context = kwargs.get('context', {'user': {'name': 'Anonymous'}})

        if context['user']['name'] != "Anonymous" and "firstLogin" not in session:
            session["firstLogin"] = "Logged"
            return redirect(url_for("auth.Login"))

        return func(*args, **kwargs)

    return wrapper


class ModifiedAuth(Auth):

    def __init__(self, *args, login_toggle=True, **kwargs):
        super().__init__(*args, **kwargs)
        self.login_toggle = login_toggle

    def login_required(self, function=None, /, *, scopes: list[str] = None):
        # If login is disabled, return the original function unwrapped
        if not self.login_toggle:
            return function if function else lambda f: f

        # Otherwise use the parent's login_required decorator
        if function is None:
            return super().login_required(scopes=scopes)
        return super().login_required(function, scopes=scopes)


