import os
import sys

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

    @app.route('/api/questions', methods = ['GET'])    
    def get_all_questions():        

        page = request.args.get("page", 1, type = int)
        
        try:
            questions = Question.query.all()
            total_questions = len(questions)
            min_index = (page - 1) * QUESTIONS_PER_PAGE
            max_index = page * QUESTIONS_PER_PAGE 

            if max_index > total_questions:
                max_index = total_questions
            
     
            questions_view = questions[min_index : max_index]
            questions_reformatted = [question.format() for question in questions_view]

            categories = Category.query.all()
            categories_reformatted = {category.id: category.type for category in categories}

            return jsonify({
                "success": True,
                "questions": questions_reformatted,
                "total_questions": total_questions,
                "categories": categories_reformatted,
                "current_category": 1,
                "total_exhibited_questions": len(questions_view)
            })
        except:
            return jsonify({
                "success": False
    
            })

    @app.route("/api/questions", methods = ["POST"])
    def test_post():
        
        try:
            data = request.get_json()

            searchTerm = data["searchTerm"].strip()

            searched_questions = Question.query.filter(Question.question.ilike("%" + searchTerm + "%"))

            questions = [question.format() for question in searched_questions]

            return jsonify({
                "success": "OK",
                "questions": questions,
                "total_questions": len(questions),
                "current_category": None

            })
        except:
            return jsonify({
                "success": "Not OK"
            })

    @app.route("/api/categories/<int:id>/questions", methods = ["GET"])
    def return_questions_by_categories(id):

        try:

            # category = Category.query.get(id)

            # return jsonify({
            #     "id": category.id
            # })

            questions = Question.query.filter(Question.category == id).all()

            if len(questions == 0):
                return jsonify({
                    "success": False,
                    "length": len(questions)
                })

            rendered_questions = [question.format() for question in questions]

            return jsonify({
                "success": True,
                "questions": rendered_questions,
                "total_questions": len(rendered_questions),
                "current_category": category
            })
            
        except:

            return jsonify({
                "success": False
            })
        

    return app


# create_app()
