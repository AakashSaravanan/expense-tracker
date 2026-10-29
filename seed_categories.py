from app import app
from config.database import db
from models.category import Category


categories = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Health",
    "Education",
    "Other"
]


with app.app_context():
    for category_name in categories:
        existing_category = Category.query.filter_by(
            category_name=category_name
        ).first()

        if not existing_category:
            category = Category(category_name=category_name)
            db.session.add(category)

    db.session.commit()

    print("Categories seeded successfully!")
