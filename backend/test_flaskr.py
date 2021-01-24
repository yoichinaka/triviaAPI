import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
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
    def test_get_categries(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
    
    def test_get_questions_fail(self):
        # this test must be fail. There is not category number 100.
        res = self.client().get('/categories/100/questions')

        self.assertEqual(res.status_code, 404)
    
    def test_delete_questions(self):
        res = self.client().delete('/questions/10')
        question = Question.query.filter(Question.id == 10).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(question, None)
    
# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()