
from datetime import datetime
from decimal import Decimal, InvalidOperation
from functools import wraps
from sqlalchemy import func, case, extract

from flask import (
    Blueprint, request, render_template,
    redirect, url_for, session, flash
)

from config.database import db
from models.transaction import Transaction
from models.category import Category


transaction_routes = Blueprint("transaction_routes", __name__)


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth_routes.login"))
        return route_function(*args, **kwargs)
    return wrapper


@transaction_routes.route("/transactions/add", methods=["GET", "POST"])
@login_required
def add_transaction():
    categories = Category.query.order_by(Category.category_name).all()

    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount", ""))
            category_id = int(request.form.get("category_id", ""))
            transaction_date = datetime.strptime(
                request.form.get("date", ""), "%Y-%m-%d"
            ).date()
        except (InvalidOperation, ValueError, TypeError):
            flash("Enter a valid amount, date, and category.", "danger")
            return render_template(
                "add_transaction.html", categories=categories
            )

        transaction_type = request.form.get("type", "")
        description = request.form.get("description", "").strip()

        if not amount.is_finite() or amount <= 0 or amount > Decimal("99999999.99"):
            flash("Enter a valid positive amount.", "danger")
            return render_template(
                "add_transaction.html", categories=categories
            )

        if transaction_type not in ("income", "expense"):
            flash("Select a valid transaction type.", "danger")
            return render_template(
                "add_transaction.html", categories=categories
            )

        category = db.session.get(Category, category_id)

        if category is None:
            flash("Select a valid category.", "danger")
            return render_template(
                "add_transaction.html", categories=categories
            )

        # Receipt upload will be connected to AWS S3 later.
        transaction = Transaction(
            amount=amount,
            date=transaction_date,
            type=transaction_type,
            description=description or None,
            user_id=session["user_id"],
            category_id=category_id
        )

        db.session.add(transaction)
        db.session.commit()

        flash("Transaction added successfully.", "success")
        return redirect(url_for("transaction_routes.list_transactions"))

    return render_template("add_transaction.html", categories=categories)


@transaction_routes.route(
    "/transactions/<int:transaction_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_transaction(transaction_id):
    transaction = Transaction.query.filter_by(
        transaction_id=transaction_id,
        user_id=session["user_id"]
    ).first_or_404()

    categories = Category.query.order_by(
        Category.category_name
    ).all()

    if request.method == "POST":
        try:
            amount = Decimal(request.form.get("amount", ""))
            category_id = int(request.form.get("category_id", ""))
            transaction_date = datetime.strptime(
                request.form.get("date", ""), "%Y-%m-%d"
            ).date()
        except (InvalidOperation, ValueError, TypeError):
            flash("Enter a valid amount, date, and category.", "danger")
            return render_template(
                "add_transaction.html",
                categories=categories,
                transaction=transaction
            )

        transaction_type = request.form.get("type", "")
        category = db.session.get(Category, category_id)

        if (
            not amount.is_finite()
            or amount <= 0
            or amount > Decimal("99999999.99")
            or transaction_type not in ("income", "expense")
            or category is None
        ):
            flash("Please check the transaction details.", "danger")
            return render_template(
                "add_transaction.html",
                categories=categories,
                transaction=transaction
            )

        transaction.amount = amount
        transaction.date = transaction_date
        transaction.type = transaction_type
        transaction.category_id = category_id
        transaction.description = (
            request.form.get("description", "").strip() or None
        )

        db.session.commit()
        flash("Transaction updated successfully.", "success")
        return redirect(url_for("transaction_routes.list_transactions"))

    return render_template(
        "add_transaction.html",
        categories=categories,
        transaction=transaction
    )


@transaction_routes.route("/transactions")
@login_required
def list_transactions():
    query = Transaction.query.filter_by(user_id=session["user_id"])

    # Read filters from the URL.
    transaction_type = request.args.get("type", "")
    category_id = request.args.get("category_id", "")
    search = request.args.get("search", "").strip()
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")

    if transaction_type in ("income", "expense"):
        query = query.filter_by(type=transaction_type)

    if category_id.isdigit():
        query = query.filter_by(category_id=int(category_id))

    if search:
        query = query.filter(
            Transaction.description.ilike(f"%{search}%")
        )

    try:
        if start_date:
            query = query.filter(
                Transaction.date >= datetime.strptime(
                    start_date, "%Y-%m-%d"
                ).date()
            )

        if end_date:
            query = query.filter(
                Transaction.date <= datetime.strptime(
                    end_date, "%Y-%m-%d"
                ).date()
            )
    except ValueError:
        flash("Invalid date filter.", "danger")
        return redirect(url_for("transaction_routes.list_transactions"))

    transactions = query.order_by(
        Transaction.date.desc(),
        Transaction.transaction_id.desc()
    ).all()

    categories = {
        category.category_id: category.category_name
        for category in Category.query.all()
    }

    return render_template(
        "transactions.html",
        transactions=transactions,
        categories=categories,
        category_list=Category.query.order_by(
            Category.category_name
        ).all(),
        selected_type=transaction_type,
        selected_category=category_id,
        search=search,
        start_date=start_date,
        end_date=end_date
    )


@transaction_routes.route(
    "/transactions/<int:transaction_id>/delete", methods=["POST"]
)
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.filter_by(
        transaction_id=transaction_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(transaction)
    db.session.commit()

    flash("Transaction deleted successfully.", "success")
    return redirect(url_for("transaction_routes.list_transactions"))


@transaction_routes.route("/reports")
@login_required
def reports():
    user_id = session["user_id"]

    # Calculate total income and expenses.
    totals = db.session.query(
        func.coalesce(
            func.sum(case(
                (Transaction.type == "income", Transaction.amount),
                else_=0
            )), 0
        ).label("income"),
        func.coalesce(
            func.sum(case(
                (Transaction.type == "expense", Transaction.amount),
                else_=0
            )), 0
        ).label("expenses")
    ).filter(Transaction.user_id == user_id).first()

    total_income = float(totals.income)
    total_expenses = float(totals.expenses)
    balance = total_income - total_expenses

    # Monthly totals for the current year.
    current_year = datetime.now().year

    monthly_rows = db.session.query(
        extract("month", Transaction.date).label("month"),
        func.sum(case(
            (Transaction.type == "income", Transaction.amount),
            else_=0
        )).label("income"),
        func.sum(case(
            (Transaction.type == "expense", Transaction.amount),
            else_=0
        )).label("expenses")
    ).filter(
        Transaction.user_id == user_id,
        extract("year", Transaction.date) == current_year
    ).group_by(
        extract("month", Transaction.date)
    ).all()

    monthly_income = [0] * 12
    monthly_expenses = [0] * 12

    for row in monthly_rows:
        month_index = int(row.month) - 1
        monthly_income[month_index] = float(row.income or 0)
        monthly_expenses[month_index] = float(row.expenses or 0)

    # Expenses grouped by category.
    category_rows = db.session.query(
        Category.category_name,
        func.sum(Transaction.amount).label("total")
    ).join(
        Transaction,
        Category.category_id == Transaction.category_id
    ).filter(
        Transaction.user_id == user_id,
        Transaction.type == "expense"
    ).group_by(Category.category_name).all()

    category_labels = [row.category_name for row in category_rows]
    category_amounts = [float(row.total) for row in category_rows]

    return render_template(
        "reports.html",
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        category_labels=category_labels,
        category_amounts=category_amounts,
        current_year=current_year
    )
