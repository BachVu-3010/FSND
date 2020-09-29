from models import setup_db, Question, Category
from app import create_app
import os
import sys
import unittest
import json
from flask_sqlalchemy import SQLAlchemy


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format(
            'postgres:password321@localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

#-------------------------------------------------------------------------------#
# Test get categories
#-------------------------------------------------------------------------------#

    def test_get_categories(self):

        response = self.client().get("api/categories")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["number_of_categories"], 6)

#-------------------------------------------------------------------------------#
# Test get all questions/ questions from categories
#-------------------------------------------------------------------------------#

    def test_get_questions(self):

        response = self.client().get("/api/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["categories"]["2"], "Art")
        self.assertEqual(data["total_questions"], 19)

    def test_get_questions_by_category(self):

        response = self.client().get("/api/categories/1/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["current_category"], "Science")
        self.assertEqual(data["total_questions"], 3)

    def test_get_questions_by_category_error(self):

        response = self.client().get("/api/categories/100/questions")
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['error'], 404)

#-------------------------------------------------------------------------------#
# Test delete question and create question
#-------------------------------------------------------------------------------#

    def test_delete_question(self):

        sample_quetion = {
            "question": "What is today?",
            "answer": "August 13th",
            "category": 4,
            "difficulty": 5
        }

        # Create a test question to delete

        test_question = Question(question=sample_quetion['question'], answer=sample_quetion['answer'],
                                 category=sample_quetion['category'], difficulty=sample_quetion['difficulty'])
        test_question.insert()
        testQuestion_id = test_question.id

        # Test added successfully
        questions = Question.query.all()
        # Original database has 19 questions
        self.assertEqual(len(questions), 20)

        # Delete it through route
        response = self.client().delete(f'/api/questions/{testQuestion_id}')
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], testQuestion_id)

    def test_create_question(self):

        sample_quetion = {
            "question": "What is today?",
            "answer": "August 13th",
            "category": 4,
            "difficulty": 5
        }

        # Create a test question to delete

        test_question = Question(question=sample_quetion['question'], answer=sample_quetion['answer'],
                                 category=sample_quetion['category'], difficulty=sample_quetion['difficulty'])

        response = self.client().post("/api/questions", json=sample_quetion)
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)

        testQuestion_id = data["new_question_id"]

        # Delete it through route
        response = self.client().delete(f'/api/questions/{testQuestion_id}')
        data = json.loads(response.data)

        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted_id'], testQuestion_id)

#-------------------------------------------------------------------------------#
# Test search function
#-------------------------------------------------------------------------------#

    def test_search_function(self):

        response = self.client().post(
            "/api/questions", json={"searchTerm": "What"})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_questions"], 8)

    def test_search_function_error(self):

        response = self.client().post(
            "/api/questions", json={"searchTerm": "@@"})

        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["success"], False)

    def test_page_doesnt_exist(self):
        # For non-existent page return error 404
        response = self.client().get('/api/questions?page=1000')
        data = json.loads(response.data)

        # Now using API-friendly custom error handlers
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['error'], 404)

    def test_pagination(self):
        """Tests the pagination by getting the first 10 questions and looking for known features"""
        res = self.client().get('/api/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(data["total_exhibited_questions"], 10)


#----------------------------------------------------------------------------#
# Tests for /quizzes POST
#----------------------------------------------------------------------------#

    def test_play_quiz_with_category(self):
        """Test /quizzes succesfully with given category """
        json_play_quizz = {
            'previous_questions': [1, 2, 5],
            'quiz_category': {
                'type': 'Science',
                'id': '1'
            }
        }
        res = self.client().post('api/quizzes', json=json_play_quizz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question']['question'])
        # Also check if returned question is NOT in previous question
        self.assertTrue(data['question']['id']
                        not in json_play_quizz['previous_questions'])

    def test_error_400_play_quiz(self):
        """Test /quizzes error without any JSON Body"""
        res = self.client().post('api/quizzes')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(
            data['message'], 'Bad Request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
