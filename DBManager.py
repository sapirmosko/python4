import os
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class DBManager:
    def __init__(self, app):
        app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
        username = os.getenv('USER_NAME')
        password = os.getenv('PASSWORD')
        database = os.getenv('DATABASE')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{username}:{password}@localhost:5432/{database}"
        db.init_app(app)

    def create_all(self):
        db.create_all()

    def execute(self, query, params=None):
        result = self.db.engine.execute(query, params)
        return result

    def add_and_commit(self, object):
        db.session.add(object)
        db.session.commit()

    def close(self):
        db.session.close()
