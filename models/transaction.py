from config.database import db


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id = db.Column(db.Integer, primary_key=True)

    amount = db.Column(db.Numeric(10, 2), nullable=False)

    date = db.Column(db.Date, nullable=False)

    type = db.Column(db.String(20), nullable=False)

    description = db.Column(db.String(255))

    receipt_url = db.Column(db.String(500))

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.category_id"),
        nullable=False
    )

    category = db.relationship("Category")
