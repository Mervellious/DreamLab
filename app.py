from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import re
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash


def validate_password(password):
    if len(password) < 6:
        return "Password must be at least 6 characters"
    if not re.search(r'\d', password):
        return "Password must contain at least 1 number"
    if not re.search(r'[!@#$%^&*()\-_=+\[\]{}|;:,.<>?]', password):
        return "Password must contain at least 1 special character (e.g. @, !, #)"
    return None


app= Flask(__name__)
app.secret_key = 'dreamlab_secret_key'

def get_db():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='dream lab',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def home():
    return render_template ('index.html')


@app.route('/patient_signup', methods=['GET','POST'])
def patient_signup():
    msg = ''
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        name_pattern = r'^[A-Za-z]{2,20}$'
        licence_pattern = r'^[A-Z0-9]{6,10}$'

        if not name or not surname or not email or not password or not cpassword:
            msg = "Please fill in all fields"
        elif not re.fullmatch(name_pattern, name):
            msg = "Name must be 2-20 letters only"
        elif not re.fullmatch(name_pattern, surname):
            msg = "Surname must be 2-20 letters only"
        elif not re.fullmatch(email_pattern, email):
            msg = "Please enter a valid email address"
        elif password != cpassword:
            msg = "Passwords do not match"
        else:
            password_error = validate_password(password)
            if password_error:
                msg = password_error
            else:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing = cursor.fetchone()
                if existing:
                    msg = "An account with this email already exists"
                else:
                    hashed_password = generate_password_hash(password)
                    cursor.execute("INSERT INTO users (name, surname, email, password, role) VALUES (%s, %s, %s, %s, %s)",
                        (name, surname, email, hashed_password, 'patient'))
                    conn.commit()
                    conn.close()
                    session['user_id'] = cursor.lastrowid
                    session['user_name'] = name
                    session['user_role'] = 'patient'
                    return redirect(url_for('dashboard'))
                conn.close()

    return render_template('patient_signup.html', msg=msg)


@app.route('/clinician_signup', methods=['GET', 'POST'])
def clinician_signup():
    msg = ''
    if request.method == 'POST':
        username = request.form.get('username')
        usersurname = request.form.get('usersurname')
        licencenumber = request.form.get('licencenumber')
        workemail = request.form.get('workemail')
        create_password = request.form.get('create_password')
        confirm_password = request.form.get('confirm_password')

        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        name_pattern = r'^[A-Za-z]{2,20}$'
        licence_pattern = r'^[A-Z0-9]{6,10}$'

        if not username or not usersurname or not licencenumber or not workemail or not create_password or not confirm_password:
            msg = "Please fill in all fields"
        elif not re.fullmatch(name_pattern, username):
            msg = "Name must be 2-20 letters only"
        elif not re.fullmatch(name_pattern, usersurname):
            msg = "Surname must be 2-20 letters only"
        elif not re.fullmatch(licence_pattern, licencenumber):
            msg = "Licence number must be 6-10 uppercase letters or digits (e.g. ABC123)"
        elif not re.fullmatch(email_pattern, workemail):
            msg = "Please enter a valid work email address"
        elif create_password != confirm_password:
            msg = "Passwords do not match"
        else:
            password_error = validate_password(create_password)
            if password_error:
                msg = password_error
            else:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = %s", (workemail,))
                existing = cursor.fetchone()
                if existing:
                    msg = "An account with this email already exists"
                else:
                    hashed_password = generate_password_hash(create_password)
                    cursor.execute("INSERT INTO users (name, surname, email, password, role) VALUES (%s, %s, %s, %s, %s)",
                        (username, usersurname, workemail, hashed_password, 'clinician'))
                    conn.commit()
                    conn.close()
                    session['user_id'] = cursor.lastrowid
                    session['user_name'] = username
                    session['user_role'] = 'clinician'
                    return redirect(url_for('clinician_dashboard'))
                conn.close()

    return render_template('clinician_signup.html', msg=msg)

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg=''
    if request.method == 'POST':
        email=request.form.get('email')
        password =request.form.get('password')

        if not email or not password:
            msg="Please fill in all fields"
        elif not re.fullmatch(r'^[^@]+@[^@]+\.[^@]+$', email):
            msg="Please enter a valid email address (e.g. name@example.com)"
        else:
            password_error = validate_password(password)
            if password_error:
                msg = password_error
            else:
                conn = get_db()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                conn.close()
                if not user:
                    msg = "No account found with this email"
                elif not check_password_hash(user['password'], password):
                    msg = "Incorrect password"
                else:
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['user_role'] = user['role']
                    if user['role'] == 'clinician':
                        return redirect(url_for('clinician_dashboard'))
                    return redirect(url_for('dashboard'))
    return render_template('login.html', msg=msg)

@app.route('/my_dreams')
def my_dreams():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dreams WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
    dreams = cursor.fetchall()
    conn.close()
    return render_template('my_dreams.html', dreams=dreams)

@app.route('/nightmares')
def nightmares():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nightmares WHERE user_id = %s ORDER BY date DESC", (session['user_id'],))
    nightmares = cursor.fetchall()
    conn.close()
    return render_template('nightmares.html', nightmares=nightmares)

@app.route('/nightmare/<int:nightmare_id>')
def nightmare_detail(nightmare_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM nightmares WHERE id = %s", (nightmare_id,))
    nightmare = cursor.fetchone()
    conn.close()
    if not nightmare:
        return redirect(url_for('nightmares'))
    return render_template('nightmare_detail.html', nightmare=nightmare)

@app.route('/nightmare/<int:nightmare_id>/update', methods=['POST'])
def update_nightmare(nightmare_id):
    description = request.form.get('description')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE nightmares SET description=%s WHERE id=%s", (description, nightmare_id))
    conn.commit()
    conn.close()
    return redirect(url_for('nightmare_detail', nightmare_id=nightmare_id))

@app.route('/create_account')
def create_account():
    return render_template('create_account.html')


@app.route('/dashboard')
def dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM dreams WHERE user_id = %s", (session['user_id'],))
    result = cursor.fetchone()
    dream_count = result['count'] if result else 0
    cursor.execute("SELECT sleep_qualitiy FROM dreams WHERE user_id = %s", (session['user_id'],))
    all_dreams = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) as count FROM reports WHERE patient_id = %s", (session['user_id'],))
    report_result = cursor.fetchone()
    report_count = report_result['count'] if report_result else 0
    conn.close()
    quality_map = {'Very Poor': 1, 'Poor': 2, 'Fair': 3, 'Good': 4, 'Very Good': 5}
    reverse_map = {1: 'Very Poor', 2: 'Poor', 3: 'Fair', 4: 'Good', 5: 'Very Good'}
    scores = [quality_map[d['sleep_qualitiy']] for d in all_dreams if d['sleep_qualitiy'] in quality_map]
    avg_sleep_quality = reverse_map[round(sum(scores) / len(scores))] if scores else '–'
    return render_template('dashboard.html', user_name=session['user_name'], dream_count=dream_count, avg_sleep_quality=avg_sleep_quality, report_count=report_count)


@app.route('/clinician-dashboard')
def clinician_dashboard():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template('clinician-dashboard.html', user_name=session['user_name'])


@app.route('/dream_detail/<int:dream_id>')
def dream_detail(dream_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dreams WHERE id = %s", (dream_id,))
    dream = cursor.fetchone()
    conn.close()
    return render_template('dream_detail.html', dream=dream)


@app.route('/dream/<int:dream_id>/update', methods=['POST'])
def update_dream(dream_id):
    description = request.form.get('description')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE dreams SET description=%s WHERE id=%s", (description, dream_id))
    conn.commit()
    conn.close()
    return redirect(url_for('dream_detail', dream_id=dream_id))


@app.route('/dream/<int:dream_id>/delete', methods=['POST'])
def delete_dream(dream_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM dreams WHERE id = %s", (dream_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('my_dreams'))


@app.route('/dream/<int:dream_id>/update_tags', methods=['POST'])
def update_dream_tags(dream_id):
    data = request.json
    mood = data.get('mood', '')
    symbols = data.get('symbols', '')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE dreams SET mood=%s, symbols=%s WHERE id=%s", (mood, symbols, dream_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/sleep_overview')
def sleep_overview():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT date, sleep_qualitiy FROM dreams WHERE user_id = %s ORDER BY date ASC", (session['user_id'],))
    dreams = cursor.fetchall()
    conn.close()
    sleep_data = [{"date": str(d["date"]), "quality": d["sleep_qualitiy"]} for d in dreams]
    return render_template('sleep_overview.html', sleep_data=sleep_data)


@app.route('/mood_tracker')
def mood_tracker():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT mood FROM dreams WHERE user_id = %s", (session['user_id'],))
    dreams = cursor.fetchall()
    conn.close()
    mood_counts = {}
    for dream in dreams:
        if dream["mood"]:
            moods = [m.strip() for m in dream["mood"].split(",")]
            for mood in moods:
                mood_counts[mood] = mood_counts.get(mood, 0) + 1
    return render_template('mood_tracker.html', mood_counts=mood_counts)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/write_dream', methods=['GET', 'POST'])
def write_dream():
    if request.method == 'POST':
        dd = request.form.get('dd', '').zfill(2)
        mm = request.form.get('mm', '').zfill(2)
        yyyy = request.form.get('yyyy', '')
        date_str = f"{yyyy}-{mm}-{dd}"
        title = request.form.get('title', '')
        dream_type = request.form.get('dream_type', '')
        description = request.form.get('description', '')
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['date'] = date_str
        session['dream_draft']['title'] = title
        session['dream_draft']['dream_type'] = dream_type
        session['dream_draft']['description'] = description
        session.modified = True
        return redirect(url_for('q1'))
    return render_template('write_dream.html')


@app.route('/q1', methods=['GET', 'POST'])
def q1():
    if request.method == 'POST':
        standout = request.form.get('standout_moment', '')
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['standout_moment'] = standout
        session.modified = True
        return redirect(url_for('q2'))
    return render_template('q1.html')


@app.route('/q2', methods=['GET', 'POST'])
def q2():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['symbols'] = request.form.get('symbols', '')
        session.modified = True
        return redirect(url_for('q3'))
    return render_template('q2.html')


@app.route('/q3', methods=['GET', 'POST'])
def q3():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['people_appeared'] = request.form.get('people_appeared', '')
        session['dream_draft']['people_description'] = request.form.get('people_description', '')
        session.modified = True
        return redirect(url_for('q4'))
    return render_template('q3.html')


@app.route('/q4', methods=['GET', 'POST'])
def q4():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['dream_role'] = request.form.get('dream_role', '')
        session['dream_draft']['dream_role_description'] = request.form.get('dream_role_description', '')
        session.modified = True
        return redirect(url_for('q5'))
    return render_template('q4.html')


@app.route('/q5', methods=['GET', 'POST'])
def q5():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['wakeup_mood'] = request.form.get('emotions', '')
        session.modified = True
        return redirect(url_for('q6'))
    return render_template('q5.html')


@app.route('/q6', methods=['GET', 'POST'])
def q6():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['previous_day_mood'] = request.form.get('previous_day_mood', '')
        session.modified = True
        return redirect(url_for('q7'))
    return render_template('q6.html')


@app.route('/q7', methods=['GET', 'POST'])
def q7():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['recurring'] = request.form.get('recurring', '')
        session.modified = True
        return redirect(url_for('q8'))
    return render_template('q7.html')


@app.route('/q8', methods=['GET', 'POST'])
def q8():
    if request.method == 'POST':
        session['dream_draft'] = session.get('dream_draft', {})
        session['dream_draft']['sleep_qualitiy'] = request.form.get('sleep_qualitiy', '')
        session.modified = True

        draft = session.get('dream_draft', {})
        user_id = session.get('user_id')

        title = draft.get('title', '')
        description = draft.get('description', '')
        date = draft.get('date', None)
        mood = draft.get('wakeup_mood', '')
        symbols = draft.get('symbols', '')
        sleep_qualitiy = draft.get('sleep_qualitiy', '')
        standout_moment = draft.get('standout_moment', '')
        people_appeared = draft.get('people_appeared', '')
        people_description = draft.get('people_description', '')
        dream_role = draft.get('dream_role', '')
        dream_role_description = draft.get('dream_role_description', '')
        wakeup_mood = draft.get('wakeup_mood', '')
        previous_day_mood = draft.get('previous_day_mood', '')
        recurring = draft.get('recurring', '')
        dream_type = draft.get('dream_type', '')

        conn = get_db()
        cursor = conn.cursor()

        if dream_type == 'Nightmare':
            cursor.execute(
                "INSERT INTO nightmares (title, description, date, mood, symbols, sleep_qualitiy, user_id, standout_moment, people_appeared, people_description, dream_role, dream_role_description, wakeup_mood, previous_day_mood, recurring) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (title, description, date, mood, symbols, sleep_qualitiy, user_id, standout_moment, people_appeared, people_description, dream_role, dream_role_description, wakeup_mood, previous_day_mood, recurring)
            )
        else:
            cursor.execute(
                "INSERT INTO dreams (title, description, date, mood, symbols, sleep_qualitiy, user_id, standout_moment, people_appeared, people_description, dream_role, dream_role_description, wakeup_mood, previous_day_mood, recurring) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                (title, description, date, mood, symbols, sleep_qualitiy, user_id, standout_moment, people_appeared, people_description, dream_role, dream_role_description, wakeup_mood, previous_day_mood, recurring)
            )

        conn.commit()
        conn.close()
        session.pop('dream_draft', None)
        session.modified = True
        return redirect(url_for('submit_page'))
    return render_template('q8.html')


@app.route('/add_tag', methods=['POST'])
def add_tag():
    data = request.json
    tag_type = data.get('tag_type', 'mood')
    tag_name = data.get('tag_name', '')
    user_id = session.get('user_id')
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO user_tags (user_id, tag_type, tag_name) VALUES (%s, %s, %s)", (user_id, tag_type, tag_name))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


@app.route('/submit_page')
def submit_page():
    return render_template('submit_page.html')


@app.route('/forgot_dream')
def forgot_dream():
    return render_template('forgot_dream.html')


@app.route('/reports')
def reports():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE patient_id = %s ORDER BY created_at DESC", (session['user_id'],))
    reports = cursor.fetchall()
    conn.close()
    return render_template('reports.html', reports=reports, user_name=session['user_name'])


@app.route('/reports/<int:report_id>')
def report_detail(report_id):
    if 'user_name' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = %s AND patient_id = %s", (report_id, session['user_id']))
    report = cursor.fetchone()
    conn.close()
    return render_template('report_detail.html', report=report, user_name=session['user_name'])


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    msg=''
    if request.method=='POST':
        email = request.form.get('email')
        if not email:
            msg='Please enter your email address'
        elif not re.fullmatch(r'^[^@]+@[^@]+\.[^@]+$', email):
            msg='Please enter a valid email address'
        else:
            msg='Reset link sent to your email!'
    return render_template('forgot_password.html',msg=msg)


@app.route('/settings')
def settings():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')


@app.route('/settings-personal')
def settings_personal():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, surname FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('settings-personal.html',
                           user_name=user['name'] if user else '',
                           user_surname=user['surname'] if user else '')


@app.route('/settings/personal', methods=['POST'])
def settings_personal_save():
    if 'user_id' not in session:
        return ('', 401)
    name = request.form.get('name', '').strip()
    surname = request.form.get('surname', '').strip()
    if name and surname:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET name=%s, surname=%s WHERE id=%s",
                       (name, surname, session['user_id']))
        conn.commit()
        conn.close()
        session['user_name'] = name
        session.modified = True
    return ('', 204)


@app.route('/settings-security')
def settings_security():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    conn.close()
    return render_template('settings-security.html',
                           user_email=user['email'] if user else '')


@app.route('/settings/security/email', methods=['POST'])
def settings_security_email_save():
    if 'user_id' not in session:
        return ('', 401)
    email = request.form.get('email', '').strip()
    if email and '@' in email:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET email=%s WHERE id=%s", (email, session['user_id']))
        conn.commit()
        conn.close()
    return ('', 204)


@app.route('/settings-delete')
def settings_delete():
    if 'user_name' not in session:
        return redirect(url_for('login'))
    return render_template('settings-delete.html')


if __name__=='__main__':
    app.run(debug=True)