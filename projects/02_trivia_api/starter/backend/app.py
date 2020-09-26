import os

from .models import setup_db, Question, Category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


QUESTIONS_PER_PAGE = 10

# Define a function for test_flaskr
def create_app():

    app = Flask(__name__)
    setup_db(app)
    
    # Define rest api pulling all categories
    @app.route('/api/categories', methods = ['GET'])
    def get_all_categories():

        try: 

            categories = Category.query.all()
            data = {category.id : category.type for category in categories}
            return jsonify({
                "success": True,
                "categories": data
            })
        except:
            return jsonify({
                "success": False
            })

    @app.route("/api")
    def get_all_questions():
        pass

    return app


# create_app()
