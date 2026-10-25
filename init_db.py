from app import app
from config.database import db

with app.app_context():
    db.create_all()
    print("Tables created.")
