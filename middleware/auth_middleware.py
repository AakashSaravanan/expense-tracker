from functools import wraps

from flask import session, redirect, url_for


def login_required(route_function):

    @wraps(route_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("auth_routes.login"))

        return route_function(*args, **kwargs)

    return wrapper
