import random
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, abort, jsonify
from models import setup_db, Question, Category
import os
import sys


QUESTIONS_PER_PAGE = 10

# Define a function for test_flaskr


def create_app():

    app = Flask(__name__)
    setup_db(app)

    # Define rest api pulling all categories
    @app.route('/api/categories', methods=['GET'])
    def get_all_categories():

        try:

            categories = Category.query.all()
            data = {category.id: category.type for category in categories}
            return jsonify({
                "success": True,
                "categories": data,
                "number_of_categories": len(categories)
            })
        except:

            abort(500)

    @app.route('/api/questions', methods=['GET'])
    def get_all_questions():

        page = request.args.get("page", 1, type=int)

        questions = Question.query.all()
        total_questions = len(questions)
        min_index = (page - 1) * QUESTIONS_PER_PAGE
        max_index = page * QUESTIONS_PER_PAGE

        questions_view = questions[min_index: max_index]
        if len(questions_view) == 0:
            abort(404)

        questions_reformatted = [question.format()
                                 for question in questions_view]

        categories = Category.query.all()
        categories_reformatted = {
            category.id: category.type for category in categories}

        return jsonify({
            "success": True,
            "questions": questions_reformatted,
            "total_questions": total_questions,
            "categories": categories_reformatted,
            "current_category": None,
            "total_exhibited_questions": len(questions_view)
        })

    @app.route('/api/questions', methods=["POST"])
    def add_question():

        try:
            request_data = request.get_json()

            if "searchTerm" in request_data:
                searchTerm = request_data["searchTerm"].strip()

                questions = Question.query.filter(
                    Question.question.ilike(f'%{searchTerm}%')).all()

                if len(questions) > 0:

                    questions_rendered = [question.format()
                                          for question in questions]

                    return jsonify({
                        "success": True,
                        "questions": questions_rendered,
                        "total_questions": len(questions_rendered),
                        "currentCategory": questions_rendered[0]["category"]
                    })
                else:

                    return jsonify({
                        "success": False
                    })

            elif "question" in request_data:
                question = request_data["question"].strip()
                answer = request_data["answer"].strip()
                difficulty = int(request_data["difficulty"])
                category = int(request_data["category"])

                try:
                    new_question = Question(
                        question=question, answer=answer, category=category, difficulty=difficulty)

                    new_question.insert()

                    return jsonify({
                        "success": True,
                        "question": request_data["question"].strip(),
                        "answer": request_data["answer"].strip(),
                        "difficulty": difficulty,
                        "category": category,
                        "new_question_id": new_question.id

                    })
                except:
                    # Issue creating new question?  422 means understood the request but couldn't do it
                    abort(422)

        except:

            abort(500)

    @app.route("/api/categories/<int:id>/questions", methods=["GET"])
    def get_questions_by_category(id):

        questions = Question.query.filter(Question.category == id).all()

        if len(questions) == 0:
            # Requested a page that does not exist
            abort(404)

        category = Category.query.get(id)

        rendered_questions = [question.format() for question in questions]

        return jsonify({
            "success": True,
            "questions": rendered_questions,
            "total_questions": len(rendered_questions),
            "current_category": category.type
        })

    @app.route("/api/questions/<int:id>", methods=["DELETE"])
    def delete_question(id):

        try:

            question = Question.query.get(id)

            if not question:
                # Question id doesn't exist
                abort(404)

            question_name = question.question

            question.delete()

            return jsonify({
                "success": True,
                "Comment": f"Successfully delete question {question_name}",
                "deleted_id": id
            })

        except:

            # Understood the request and it was formatted properly, but was unable to process request
            abort(422)

    @app.route("/api/quizzes", methods=["POST"])
    def get_quizzes():

        try:
            data = request.get_json()
            previous_questions = data["previous_questions"]
            quiz_category = data["quiz_category"]

            if quiz_category["id"]:
                questions = Question.query.filter(
                    Question.category == int(quiz_category["id"])).all()
            else:
                questions = Question.query.all()

            questions = [question.format() for question in questions]

            unanswered_questions = []
            for question in questions:
                if question["id"] not in previous_questions:
                    unanswered_questions.append(question)

            question = random.choice(unanswered_questions)

            return jsonify({
                "success": True,
                "question": question,

            })

        except:

            abort(400)

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad Request"
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Not found"
        })

    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Unprocessable Entity"
        })

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        })

    return app


if __name__ == "__main__":
    app.run()
