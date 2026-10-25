from flask import (
    Flask,
    render_template,
    session,
    request,
    redirect,
    url_for,
    send_from_directory
)
from config.database import db, init_db

import os
from werkzeug.utils import secure_filename
from models.user import User
from models.category import Category
from models.transaction import Transaction
from routes.auth_routes import auth_routes
from middleware.auth_middleware import login_required
from sqlalchemy import func, text
from dotenv import load_dotenv
from routes.transaction_routes import transaction_routes

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
load_dotenv()
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

init_db(app)

app.register_blueprint(auth_routes)
app.register_blueprint(transaction_routes)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/dashboard")
@login_required
def dashboard():

    # Get the current user's transactions
    query = Transaction.query.filter_by(
        user_id=session["user_id"]
    )

    # Filters
    transaction_type = request.args.get("type")
    category_id = request.args.get("category_id")
    date = request.args.get("date")

    if transaction_type:
        query = query.filter_by(type=transaction_type)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if date:
        query = query.filter_by(date=date)

    # Get filtered transactions
    transactions = query.order_by(
        Transaction.date.desc()
    ).all()

    # Get all categories for the filter dropdown
    categories = Category.query.all()

    # Total income
    total_income = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == session["user_id"],
        Transaction.type == "income"
    ).scalar() or 0

    # Total expenses
    total_expense = db.session.query(
        func.sum(Transaction.amount)
    ).filter(
        Transaction.user_id == session["user_id"],
        Transaction.type == "expense"
    ).scalar() or 0

    # Balance
    balance = total_income - total_expense

    # Expenses grouped by category
    category_expenses = db.session.query(
        Category.category_name,
        func.sum(Transaction.amount)
    ).join(
        Transaction,
        Category.category_id == Transaction.category_id
    ).filter(
        Transaction.user_id == session["user_id"],
        Transaction.type == "expense"
    ).group_by(
        Category.category_name
    ).all()

    return render_template(
        "dashboard.html",
        user_name=session.get("user_name"),
        transactions=transactions,
        categories=categories,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        category_expenses=category_expenses
    )

@app.route("/add-transaction", methods=["GET", "POST"])
@login_required
def add_transaction():

    if request.method == "POST":

        amount = request.form["amount"]
        date = request.form["date"]
        transaction_type = request.form["type"]
        description = request.form["description"]
        category_id = request.form["category_id"]

        receipt = request.files.get("receipt")

        receipt_filename = None

        if receipt and receipt.filename:

            receipt_filename = secure_filename(receipt.filename)

            receipt.save(
                os.path.join(
                    app.config["UPLOAD_FOLDER"],
                    receipt_filename
                )
        )

        transaction = Transaction(
            amount=amount,
            date=date,
            type=transaction_type,
            description=description,
            receipt_url=receipt_filename,
            user_id=session["user_id"],
            category_id=category_id
        )

        db.session.add(transaction)
        db.session.commit()

        return redirect(url_for("dashboard"))

    categories = Category.query.all()

    return render_template(
        "add_transaction.html",
        categories=categories
    )

@app.route("/edit-transaction/<int:transaction_id>", methods=["GET", "POST"])
@login_required
def edit_transaction(transaction_id):

    transaction = Transaction.query.filter_by(
        transaction_id=transaction_id,
        user_id=session["user_id"]
    ).first_or_404()

    if request.method == "POST":

        transaction.amount = request.form["amount"]
        transaction.date = request.form["date"]
        transaction.type = request.form["type"]
        transaction.description = request.form["description"]
        transaction.category_id = request.form["category_id"]

        db.session.commit()

        return redirect(url_for("dashboard"))

    categories = Category.query.all()

    return render_template(
        "edit_transaction.html",
        transaction=transaction,
        categories=categories
    )


@app.route("/delete-transaction/<int:transaction_id>", methods=["POST"])
@login_required
def delete_transaction(transaction_id):

    transaction = Transaction.query.filter_by(
        transaction_id=transaction_id,
        user_id=session["user_id"]
    ).first_or_404()

    db.session.delete(transaction)
    db.session.commit()

    return redirect(url_for("dashboard"))

@app.route("/uploads/<filename>")
@login_required
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )

@app.route("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
        return {"status": "ok"}, 200
    except Exception:
        return {"status": "db_unavailable"}, 503


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)