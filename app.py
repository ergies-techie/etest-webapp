import os
import sqlite3
from flask import Flask, g, request, jsonify, session, redirect, render_template_string, make_response, url_for, render_template, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash
import random
from functools import wraps

BASE_DIR = os.path.dirname(__file__)
QUESTIONS_DB = os.path.join(BASE_DIR, 'db', 'questions.db')
USERS_DB = os.path.join(BASE_DIR,'db', 'users.db')

app = Flask(__name__)
app.secret_key = 'THIS_IS_MY_KEY_WHICH_IS_A_GREAT_SECRET@ERGIES'  # IMPORTANT: replace in production
app.config['JSON_SORT_KEYS'] = False

# -------------------- Users DB helpers --------------------

def get_users_db():
    db = getattr(g, '_users_db', None)
    if db is None:
        db = g._users_db = sqlite3.connect(USERS_DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_users_db(exception):
    db = getattr(g, '_users_db', None)
    if db is not None:
        db.close()

# -------------------- Auth helpers --------------------

def getUserByUserName(username):
    db = get_users_db()
    cur = db.cursor()
    cur.execute('SELECT id, username, password_hash, is_admin, active FROM users WHERE username = ?', (username,))
    return cur.fetchone()

def getUserByUserID(id):
    db = get_users_db()
    cur = db.cursor()
    cur.execute('SELECT id, username, password_hash, is_admin, active FROM users WHERE id = ?', (id,))
    return cur.fetchone()

def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if not session.get('user_id'):
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapped

def admin_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        user = getUserByUserID(session.get('user_id'))
        if not user['is_admin']:
            return abort(404)
        return f(*args, **kwargs)
    return wrapped

# -------------------- Questions DB helper --------------------

def get_questions_db():
    db = getattr(g, '_questions_db', None)
    if db is None:
        db = g._questions_db = sqlite3.connect(QUESTIONS_DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_questions_db(exception):
    db = getattr(g, '_questions_db', None)
    if db is not None:
        db.close()

# -------------------- LOGIN --------------------

@app.route("/login")
def login_page():
    return render_template("login.html")

#TODO This is deprecated, everything save admin panel uses /api/logout
@app.route("/logout")
def logoutOld():
    session.clear()
    return redirect("/")


# -------------------- Frontend (requires login) --------------------

@app.route("/", methods = ["GET"])
@login_required
def index():
    return redirect('/dashboard')

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

#TODO this needs implementing
@app.route("/adminPanel")
@login_required
@admin_required
def adminPanel():
    pass

@app.route("/mockTest")
@login_required
def serveQuestions():
    session['testType'] = 'mockTest'
    return render_template("mTest.html")

@app.route("/allQuestions")
@login_required
def serveAllQuestions():
    session['testType'] = 'allQuestions'
    return render_template("questions.html")

# -------------------- API --------------------

@app.route('/api/getThisQuestion', methods=["POST"])
@login_required
def getThisQuestion():
    data = request.get_json()
    qid = data.get('qid')
    if not qid:
        qid = "1"
    db = get_questions_db()
    cur = db.cursor()
    cur.execute('SELECT id, text FROM questions WHERE id = ?', (qid,))
    row = cur.fetchone()
    if not row:
        return jsonify({'error': 'no questions in database'}), 404
    qText = row['text']
    cur.execute('SELECT id, text, is_correct FROM answers WHERE question_id = ?', (qid,))
    answers = [dict(r) for r in cur.fetchall()]
    rightAnswer = ""
    for i in answers:
        if i['is_correct']:
            rightAnswer = i['id']
    random.shuffle(answers)
    response = make_response(jsonify({
        'question_id': qid,
        'question': qText,
        'answers': answers,
        'rightAnswer': rightAnswer
    }))
    session["questionNo"] = qid
    return response

@app.route('/api/selectedA', methods=["POST"])#TODO REFACTOR to save selected answer only. Rest is implemented in js
@login_required
def selectedA():
    data = request.get_json()
    aid = data["aID"]
    db = get_questions_db()
    cur = db.cursor()    
    cur.execute('SELECT id, question_id, is_correct FROM answers WHERE id = ?', (aid,))
    answer = [dict(r) for r in cur.fetchall()]
    questionID = answer[0]['question_id']
    questionIsCorrect = answer[0]['is_correct']
    #TODO uncomment when everything else working ---- save selected qid and aid
    # udb = get_users_db()
    # ucur = udb.cursor()
    # ucur.execute('INSERT INTO myAnswers (user_id, question_id, answer_id, is_correct) VALUES (?,?,?,?)',
    #               (session.get("user_id"), questionID, aid, questionIsCorrect))
    if questionIsCorrect:
        rightAnswer = answer
    if not questionIsCorrect:
        cur.execute('SELECT id, is_correct FROM answers WHERE question_id = ? AND is_correct = 1', (questionID,))
        rightAnswer = [dict(r) for r in cur.fetchall()]
        
    return jsonify({
        "checked": answer[0],
        "correct" : rightAnswer[0]
                })

@app.route("/api/saveThisRun", methods = ["POST"])
@login_required
def evaluateTest():
    data = request.get_json()
    print(data)
    return jsonify({
        "checked": 0,
        "correct" : 0
                })

@app.route('/api/getTenQuestionsIDs', methods = ["GET"])
@login_required
def getTenQuestionsIDs():
    db = get_questions_db()
    cur = db.cursor()
    cur.execute("SELECT id FROM questions ORDER BY RANDOM() LIMIT 10")
    questions = [dict(q) for q in cur.fetchall()]
    current = session.get('questionNo')
    print(current)
    if not current:
        current = 0
    for i in questions:
        if i["id"] == int(current):
            i["active"] = True
        i["notAnswered"] = True
    return jsonify(questions)



@app.route('/api/getAllQuestionIDs')
@login_required
def getAllQIDs():
    db = get_questions_db()
    cur = db.cursor()
    cur.execute('SELECT id FROM questions')
    rows = cur.fetchall()
    qids = [dict(r) for r in rows]
    current = session.get('questionNo')
    for i in qids:
        if i["id"] == int(current):
            i["active"] = True
        i["notAnswered"] = True
    return jsonify(qids)

@app.route('/api/logout')
@login_required
def logout():
    session.clear()
    return jsonify({"success" : True, "redirect": "/"})

@app.route('/api/getMyOptions')
@login_required
def getMyOptions():
    admin = {"id":0, "text":"admin panel", "href":"/adminPanelOld"}
    response = [{"id": 1, "text": "Test", "href":"/mockTest"},
                {"id":2, "text":"Všechny otázky", "href":"/allQuestions"}]
    userID = session.get('user_id')
    
    if userID != -1:
        user = getUserByUserID(userID)
        if user['is_admin']:
            response.insert(0, admin)   
    #TODO make DB entry, what is available to user and implement automatic listing in here
    return jsonify(response)

@app.post("/api/login")
def api_login():
    data = request.get_json()

    username = data.get("username")
    password = data.get("password")
    if username == "guest" and password == "guest":
        session['user_id'] = -1
        session['username'] = "guest"
        return jsonify({"success": True, "message": "Login successful!", "redirect": "/dashboard"})
    #Validate input TODO make sure no DB special chars are accepted
    if not username or not password:
        return jsonify({"success": False, "error": "Missing fields"}), 400
    user = getUserByUserName(username)
    
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({"success": False, "error": "Invalid username or password"}), 401    
    elif not user['active']:
        return jsonify({"success": False, "error": "User is not active"}), 401    
    elif user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        return jsonify({"success": True, "message": "Login successful!", "redirect": "/dashboard"})
    return jsonify({"success": False, "error": "Unknown"}), 401

@app.post("/api/register")
def api_register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    
    if not username or not password:
        return jsonify({"success": False, "error": "Missing fields"}), 400
    user = getUserByUserName(username)
    if user or username == "guest":
        return jsonify({"success": False, "error": "Username already exists"}), 400    
    
    #TODO create user here

    return jsonify({"success": False, "error": "Unknown"}), 401

@app.route("/api/getUserName")
@login_required
def getUserName():
    return jsonify({"userName" : session.get('username')})

@app.route('/api/me')
@login_required
def api_me():
    return jsonify({'username': session.get('username', 'unknown'), 'is_admin': session.get('is_admin', False)})




#TODO clear this to js ------------- ADMIN --------------------------
@app.route('/questions')
@admin_required
def list_questions():
    cur = get_db('questions').cursor()
    cur.execute('SELECT * FROM questions ORDER BY id')
    qs = cur.fetchall()
    rows = []
    for q in qs:
        cur.execute('SELECT id, text, is_correct FROM answers WHERE question_id=?', (q['id'],))
        ans = cur.fetchall()
        rows.append((q, ans))

    body = render_template_string('''
    <h2>Questions</h2>
    <p><a href="/questions/add">Add question</a> | <a href="/">Back</a></p>
    <table>
      <tr><th>ID</th><th>Question</th><th>Answers</th><th>Actions</th></tr>
      {% for q, answers in rows %}
        <tr>
          <td>{{q.id}}</td>
          <td>{{q.text}}</td>
          <td>
            <ul>
              {% for a in answers %}
                <li>{{a.text}} {% if a.is_correct %}<strong>(correct)</strong>{% endif %}</li>
              {% endfor %}
            </ul>
          </td>
          <td>
            <a class="button" href="/questions/edit/{{q.id}}">Edit</a>
            <form method="POST" action="/questions/delete/{{q.id}}" class="inline" onsubmit="return confirm('Delete question?');">
              <button type="submit" class="danger">Delete</button>
            </form>
          </td>
        </tr>
      {% endfor %}
    </table>
    ''', rows=rows)

    return render_template_string(BASE_HTML, username=session.get('username'), body=body)

@app.route('/questions/add', methods=['GET','POST'])
@admin_required
def add_question():
    if request.method == 'POST':
        qtext = request.form.get('question')
        correct = request.form.get('correct')
        w1 = request.form.get('w1')
        w2 = request.form.get('w2')
        if not qtext or not correct or not w1 or not w2:
            flash('Missing fields')
            return redirect(url_for('add_question'))
        db = get_db('questions')
        cur = db.cursor()
        cur.execute('INSERT INTO questions (text) VALUES (?)', (qtext,))
        qid = cur.lastrowid
        cur.execute('INSERT INTO answers (question_id, text, is_correct) VALUES (?,?,1)', (qid, correct))
        cur.execute('INSERT INTO answers (question_id, text, is_correct) VALUES (?,?,0)', (qid, w1))
        cur.execute('INSERT INTO answers (question_id, text, is_correct) VALUES (?,?,0)', (qid, w2))
        db.commit()
        flash('Question added')
        return redirect(url_for('list_questions'))

    body = '''
    <h2>Add Question</h2>
    <form method="POST">
      <label>Question:<br><textarea name="question" required style="width:100%;height:80px"></textarea></label><br><br>
      <label>Correct answer:<br><input name="correct" required style="width:100%"></label><br><br>
      <label>Wrong answer 1:<br><input name="w1" required style="width:100%"></label><br><br>
      <label>Wrong answer 2:<br><input name="w2" required style="width:100%"></label><br><br>
      <button>Save</button> <a href="/questions">Cancel</a>
    </form>
    '''
    return render_template_string(BASE_HTML, username=session.get('username'), body=body)

@app.route('/questions/edit/<int:qid>', methods=['GET','POST'])
@admin_required
def edit_question(qid):
    db = get_db('questions')
    cur = db.cursor()
    cur.execute('SELECT * FROM questions WHERE id=?', (qid,))
    q = cur.fetchone()
    if not q:
        return 'Not found', 404

    if request.method == 'POST':
        new_qtext = request.form.get('question')
        # update question
        cur.execute('UPDATE questions SET text=? WHERE id=?', (new_qtext, qid))
        # update answers
        cur.execute('SELECT id FROM answers WHERE question_id=?', (qid,))
        aids = [r['id'] for r in cur.fetchall()]
        for aid in aids:
            text = request.form.get(f'a_{aid}')
            is_corr = 1 if request.form.get('correct') == str(aid) else 0
            cur.execute('UPDATE answers SET text=?, is_correct=? WHERE id=?', (text, is_corr, aid))
        db.commit()
        flash('Question updated')
        return redirect(url_for('list_questions'))

    # GET: render form with answers
    cur.execute('SELECT id, text, is_correct FROM answers WHERE question_id=?', (qid,))
    answers = cur.fetchall()
    body = render_template_string('''
    <h2>Edit Question #{{q.id}}</h2>
    <form method="POST">
      <label>Question:<br><textarea name="question" required style="width:100%;height:80px">{{q.text}}</textarea></label><br><br>

      <h3>Answers (select correct)</h3>
      {% for a in answers %}
        <div>
          <label>
            <input type="radio" name="correct" value="{{a.id}}" {% if a.is_correct %}checked{% endif %}> 
            <input type="text" name="a_{{a.id}}" value="{{a.text}}" style="width:80%">
          </label>
        </div>
        <br>
      {% endfor %}

      <button>Save</button> <a href="/questions">Cancel</a>
    </form>
    ''', q=q, answers=answers)
    return render_template_string(BASE_HTML, username=session.get('username'), body=body)

@app.route('/questions/delete/<int:qid>', methods=['POST'])
@admin_required
def delete_question(qid):
    db = get_db('questions')
    cur = db.cursor()
    cur.execute('DELETE FROM answers WHERE question_id=?', (qid,))
    cur.execute('DELETE FROM questions WHERE id=?', (qid,))
    db.commit()
    flash('Question deleted')
    return redirect(url_for('list_questions'))

# -------------------- Users Management --------------------
@app.route('/users')
@admin_required
def list_users():
    cur = get_db('users').cursor()
    cur.execute('SELECT id, username, is_admin, active FROM users ORDER BY username')
    rows = cur.fetchall()
    body = render_template_string('''
    <h2>Users</h2>
    <p><a href="/users/add">Add user</a> | <a href="/">Back</a></p>
    <table>
      <tr><th>Username</th><th>Admin</th><th>Active</th><th>Actions</th></tr>
      {% for u in rows %}
        <tr>
          <td>{{u.username}}</td>
          <td>{{'Yes' if u.is_admin else 'No'}}</td>
          <td>{{'Yes' if u.active else 'No'}}</td>
          <td>
            {% if not u.is_admin %}
              <form method="POST" action="/users/promote/{{u.id}}" class="inline"><button>Promote</button></form>
            {% else %}
              <form method="POST" action="/users/demote/{{u.id}}" class="inline"><button>Demote</button></form>
            {% endif %}
            <form method="POST" action="/users/toggle/{{u.id}}" class="inline"><button>{{'Disable' if u.active else 'Enable'}}</button></form>
            <form method="POST" action="/users/delete/{{u.id}}" class="inline" onsubmit="return confirm('Delete user?');"><button class="danger">Delete</button></form>
          </td>
        </tr>
      {% endfor %}
    </table>
    ''', rows=rows)
    return render_template_string(BASE_HTML, username=session.get('username'), body=body)

@app.route('/users/add', methods=['GET','POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        is_admin = 1 if request.form.get('is_admin') == '1' else 0
        if not username or not password:
            flash('Missing fields')
            return redirect(url_for('add_user'))
        db = get_db('users')
        cur = db.cursor()
        try:
            cur.execute('INSERT INTO users (username, password_hash, is_admin, active) VALUES (?,?,?,1)',
                        (username, generate_password_hash(password), is_admin))
            db.commit()
            flash('User added')
            return redirect(url_for('list_users'))
        except sqlite3.IntegrityError:
            flash('Username already exists')
            return redirect(url_for('add_user'))

    body = '''
    <h2>Add User</h2>
    <form method="POST">
      <label>Username: <input name="username" required></label><br><br>
      <label>Password: <input type="password" name="password" required></label><br><br>
      <label>Admin: <select name="is_admin"><option value="0">No</option><option value="1">Yes</option></select></label><br><br>
      <button>Save</button> <a href="/users">Cancel</a>
    </form>
    '''
    return render_template_string(BASE_HTML, username=session.get('username'), body=body)

@app.route('/users/promote/<int:uid>', methods=['POST'])
@admin_required
def promote_user(uid):
    db = get_db('users')
    cur = db.cursor()
    cur.execute('UPDATE users SET is_admin=1 WHERE id=?', (uid,))
    db.commit()
    flash('User promoted')
    return redirect(url_for('list_users'))

@app.route('/users/demote/<int:uid>', methods=['POST'])
@admin_required
def demote_user(uid):
    db = get_db('users')
    cur = db.cursor()
    cur.execute('UPDATE users SET is_admin=0 WHERE id=?', (uid,))
    db.commit()
    flash('User demoted')
    return redirect(url_for('list_users'))

@app.route('/users/toggle/<int:uid>', methods=['POST'])
@admin_required
def toggle_user(uid):
    db = get_db('users')
    cur = db.cursor()
    cur.execute('SELECT active FROM users WHERE id=?', (uid,))
    r = cur.fetchone()
    if not r:
        flash('User not found')
        return redirect(url_for('list_users'))
    new_state = 0 if r['active'] else 1
    cur.execute('UPDATE users SET active=? WHERE id=?', (new_state, uid))
    db.commit()
    flash('User state updated')
    return redirect(url_for('list_users'))

@app.route('/users/delete/<int:uid>', methods=['POST'])
@admin_required
def delete_user(uid):
    db = get_db('users')
    cur = db.cursor()
    cur.execute('DELETE FROM users WHERE id=?', (uid,))
    db.commit()
    flash('User deleted')
    return redirect(url_for('list_users'))

def get_db(path_key='users'):
    attr = '_users_db' if path_key == 'users' else '_q_db'
    path = USERS_DB if path_key == 'users' else QUESTIONS_DB
    db = getattr(g, attr, None)
    if db is None:
        db = sqlite3.connect(path)
        db.row_factory = sqlite3.Row
        setattr(g, attr, db)
    return db

@app.route('/adminPanelOld')
@admin_required
def home():
    body = """
    <p>
      <a href="/questions">Manage Questions</a> |
      <a href="/users">Manage Users</a>
    </p>
    """
    return render_template_string(BASE_HTML, username=session.get('username'), body=body)

BASE_HTML = """
<!doctype html>
<html>
<head>
<link rel="stylesheet" href="{{ url_for('static', filename='css/main.css')}}">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/dashboard.css')}}">   
  <meta charset="utf-8">
  <title>Admin</title>
  <style>
    body{font-family:system-ui,Segoe UI,Roboto,Arial;margin:2rem;background:#f7f7fb}
    .container{max-width:1100px;margin:0 auto;background:white;padding:1rem;border-radius:10px}
    table{width:100%;border-collapse:collapse}
    th,td{padding:8px;border-bottom:1px solid #e6e6ee;text-align:left}
    a.button{padding:6px 10px;border-radius:6px;border:1px solid #ccc;text-decoration:none;margin-right:6px}
    .danger{color:#c00}
    form.inline{display:inline}
    .top{display:flex;justify-content:space-between;align-items:center}
  </style>
</head>
<body>
<div class="userContainer">
        <div class="userCard">
            <button id="userName" class="user"></button>
            <button id="logout" class="user logout">Logout</button>
        </div>
    </div>
  <div class="container">
    <div class="top">
      <h1>Admin Panel</h1>
      
    
    </div>
    <hr>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <div style="color:green">{% for m in messages %}{{m}}<br>{% endfor %}</div>
      {% endif %}
    {% endwith %}
    {{ body|safe }}
  </div>
  <script src="{{ url_for('static', filename='js/userPanel.js') }}"></script>
</body>
</html>
"""

#TODO end of trash code
# -------------------- Run --------------------
if __name__ == '__main__':
    print('Starting public app on http://127.0.0.1:5000')
    app.run(port=5000, debug=True)
