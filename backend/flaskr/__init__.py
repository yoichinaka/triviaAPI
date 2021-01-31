import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random
from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. 
  Delete the sample route after completing the TODOs
  '''
  CORS(app)
  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', \
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE')
    return response
  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def retrive_categories():
    categories = Category.query.all()
    current_categories = [categories.format()["type"] for categories in categories]
    if len(categories) == 0:
      abort(404)

    return jsonify({'categories': current_categories})

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  def get_category_list():
    categories = {}
    for category in Category.query.all():
        categories[category.id] = category.type
    return categories

  @app.route('/questions')
  def retrieve_questions():
    questiongs = Question.query.order_by(Question.id).all()
    current_questions = paginate_questions(request, questiongs)
    len_questions = len(questiongs)
    if len(current_questions) == 0:
      abort(404)

    return jsonify({'questions': current_questions,
                    'total_questions': len_questions,
                    'categories': get_category_list(),
                    'current_category': None})
  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, 
  the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    question = Question.query.filter(Question.id == question_id).one_or_none()
    if question is None:
      abort(404)

    question.delete()

    return jsonify({})

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()    
    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_dificulity = body.get('difficulty', None)
    new_category = body.get('category', None)

    try:
      question = Question(question=new_question, 
                          answer=new_answer, difficulty=new_dificulity,
                          category=new_category)
      question.insert()

      return jsonify({})

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/questions/search', methods=['POST'])
  def search_questions():
    body = request.get_json()
    if body == None:
      abort(400)  
    search_term = body.get('searchTerm', None)

    try:
      questions = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()
      len_questions=len(questions)
      current_questions = paginate_questions(request, questions)

      return jsonify({'questions': current_questions,
                      'total_questions': len_questions,
                      'current_category': None})

    except:
      abort(400)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions')
  def retrieve_questions_by_category(category_id):
    questions = Question.query.order_by(Question.id).filter(Question.category==category_id).all()
    current_questions = paginate_questions(request, questions)
    len_quetions = len(questions)
    if len_quetions == 0:
      abort(404)

    return jsonify({'questions': current_questions,
                    'total_questions': len_quetions,
                    'current_category': category_id})

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def retrieve_quizzes():
    body = request.get_json()
    previous_questions = body.get('previous_questions', None)
    # quiz_category must be integer and start from one by frontend
    quiz_category = int(body.get('quiz_category', None).get('id', None))+1
    quiz_category_type = body.get('quiz_category', None).get('type' , None)

    #find questions inclueded in all categories or a selected category
    try: 
      if quiz_category_type == "click":   # this is for 'all' categories
        questions = Question.query.all()          
      else:                               # this is for a selected category
        questions = Question.query.\
          filter(Question.category==quiz_category).all()
      
      # make a list of question id in a selected catetory or all category
      ids = [q.id for q in questions] 
      # remove questions in previous questions from the list of questions above
      for i in previous_questions:
         ids.remove(i)
      selected_id = random.choice(ids)
      q = Question.query.get(selected_id).format()

      return jsonify({'question': q})

    except:
      abort(422)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(400)
  def not_found(error):
    return jsonify({"success": False,
                    "error": 400,
                    "message": "bad request"}),400
  
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({"success": False,
                    "error": 404,
                    "message": "resource not found"}),404
  
  @app.errorhandler(422)
  def not_found(error):
    return jsonify({"success": False,
                    "error": 422,
                    "message": "unprocessable"}),422

  return app

    