from flask import Blueprint, request, render_template, redirect, url_for, session
from config.database import db
from models.user import User
from functools import wraps

def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_routes.login"))

        return route_function(*args, **kwargs)

    return wrapper

auth_routes = Blueprint("auth_routes", __name__)


@auth_routes.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            return "Email already registered"

        user = User(
            name=name,
            email=email,
            password=""
        )

        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return "Registration successful"

    return render_template("register.html")


@auth_routes.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session["user_id"] = user.user_id
            session["user_name"] = user.name

            return redirect(url_for("home"))

        return "Invalid email or password"

    return render_template("login.html")


@auth_routes.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))

@auth_routes.route("/dashboard")
@login_required
def dashboard():
    from sqlalchemy import func
    from models.transaction import Transaction
    from models.category import Category

    user_id = session["user_id"]

    # Calculate income and expenses for the logged-in user
    total_income = db.session.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter_by(user_id=user_id, type="income").scalar()

    total_expense = db.session.query(
        func.coalesce(func.sum(Transaction.amount), 0)
    ).filter_by(user_id=user_id, type="expense").scalar()

    balance = total_income - total_expense

    # Get categories for the filter
    categories = Category.query.order_by(
        Category.category_name
    ).all()

    # Get transactions belonging to this user
    query = Transaction.query.filter_by(user_id=user_id)

    # Apply dashboard filters
    selected_type = request.args.get("type", "")
    selected_category = request.args.get("category_id", "")
    selected_date = request.args.get("date", "")

    if selected_type in ("income", "expense"):
        query = query.filter_by(type=selected_type)

    if selected_category.isdigit():
        query = query.filter_by(category_id=int(selected_category))

    if selected_date:
        try:
            from datetime import datetime
            selected_date_obj = datetime.strptime(
                selected_date, "%Y-%m-%d"
            ).date()
            query = query.filter(Transaction.date == selected_date_obj)
        except ValueError:
            selected_date = ""

    transactions = query.order_by(
        Transaction.date.desc(),
        Transaction.transaction_id.desc()
    ).all()

    # Calculate expenses grouped by category
    category_expenses = (
        db.session.query(
            Category.category_name,
            func.sum(Transaction.amount)
        )
        .join(
            Transaction,
            Category.category_id == Transaction.category_id
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.type == "expense"
        )
        .group_by(Category.category_name)
        .all()
    )

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name", "User"),
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        categories=categories,
        transactions=transactions,
        category_expenses=category_expenses,
        selected_type=selected_type,
        selected_category=selected_category,
        selected_date=selected_date
    )