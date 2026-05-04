from flask import Flask, request, jsonify, send_from_directory
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

def read_db():
    with open(os.path.join(BASE_DIR, 'data.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def write_db(data):
    with open(os.path.join(BASE_DIR, 'data.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def read_logs():
    with open(os.path.join(BASE_DIR, 'logs.json'), 'r', encoding='utf-8') as f:
        return json.load(f)

def write_logs(logs):
    with open(os.path.join(BASE_DIR, 'logs.json'), 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def add_log(action, user_name, target_name, details=""):
    logs = read_logs()
    logs.insert(0, {
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "action": action,
        "user": user_name,
        "target": target_name,
        "details": details
    })
    write_logs(logs)

@app.route('/')
def index():
    return send_from_directory('html', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    if filename.endswith('.html'):
        return send_from_directory('html', filename)
    elif filename.endswith('.css'):
        return send_from_directory('css', filename)
    elif filename.endswith('.js'):
        return send_from_directory('js', filename)
    return send_from_directory('.', filename)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data.get('login', '').strip().lower()
    password = data.get('password', '')
    
    db = read_db()
    for emp in db['employees']:
        if emp['password'] == password and (emp['login'].lower() == login or emp['email'].lower() == login):
            add_log("Вход в систему", emp['full_name'], "-")
            return jsonify({'success': True, 'user': emp})
    
    return jsonify({'success': False})

@app.route('/api/get_employees', methods=['POST'])
def get_employees():
    db = read_db()
    return jsonify({'success': True, 'employees': db['employees']})

@app.route('/api/get_profile', methods=['POST'])
def get_profile():
    data = request.get_json()
    uid = data.get('user_id')
    db = read_db()
    for emp in db['employees']:
        if emp['id'] == uid:
            return jsonify({'success': True, 'user': emp})
    return jsonify({'success': False})

@app.route('/api/get_employee', methods=['POST'])
def get_employee():
    data = request.get_json()
    uid = data.get('user_id')
    db = read_db()
    for emp in db['employees']:
        if emp['id'] == uid:
            return jsonify({'success': True, 'user': emp})
    return jsonify({'success': False})

@app.route('/api/get_logs', methods=['POST'])
def get_logs():
    logs = read_logs()
    return jsonify({'success': True, 'logs': logs})

@app.route('/api/add_employee', methods=['POST'])
def add_employee():
    data = request.get_json()
    db = read_db()
    
    login = data.get('login', '').strip()
    if not login:
        n = 1
        while any(e['login'] == f'employee{n}' for e in db['employees']):
            n += 1
        login = f'employee{n}'
    elif any(e['login'] == login for e in db['employees']):
        return jsonify({'success': False, 'message': 'Такой логин уже существует'})
    
    emp = {
        'id': db['next_id'],
        'full_name': data.get('full_name', ''),
        'hire_date': data.get('hire_date', ''),
        'position': data.get('position', ''),
        'department': data.get('department', ''),
        'phone': data.get('phone', ''),
        'email': data.get('email', ''),
        'login': login,
        'password': data.get('password', ''),
        'role': data.get('role', 'employee'),
        'extra_info': data.get('extra_info', {})
    }
    db['employees'].append(emp)
    db['next_id'] += 1
    write_db(db)
    
    current_user = data.get('current_user', data.get('full_name', 'Система'))
    add_log("Добавление сотрудника", current_user, emp['full_name'], f"Логин: {login}")
    
    return jsonify({'success': True, 'employee': emp})

@app.route('/api/update_employee', methods=['POST'])
def update_employee():
    data = request.get_json()
    db = read_db()
    
    emp_id = data.get('id')
    current_user_role = data.get('current_user_role')
    current_user_name = data.get('current_user_name', 'Неизвестно')
    
    for emp in db['employees']:
        if emp['id'] == emp_id:
            if current_user_role == 'hr' and emp['role'] in ['admin', 'junior_admin']:
                return jsonify({'success': False, 'message': 'Кадровик не может редактировать администраторов'})
            if current_user_role == 'junior_admin' and emp['role'] == 'admin':
                return jsonify({'success': False, 'message': 'Нельзя редактировать старшего администратора'})
            
            emp['full_name'] = data.get('full_name', emp['full_name'])
            emp['hire_date'] = data.get('hire_date', emp['hire_date'])
            emp['position'] = data.get('position', emp['position'])
            emp['department'] = data.get('department', emp['department'])
            emp['phone'] = data.get('phone', emp['phone'])
            emp['email'] = data.get('email', emp['email'])
            emp['password'] = data.get('password', emp['password'])
            if data.get('login'):
                new_login = data['login'].strip()
                if new_login != emp['login'] and any(e['login'] == new_login for e in db['employees']):
                    return jsonify({'success': False, 'message': 'Логин занят'})
                emp['login'] = new_login
            
            write_db(db)
            add_log("Редактирование", current_user_name, emp['full_name'])
            return jsonify({'success': True, 'employee': emp})
    
    return jsonify({'success': False, 'message': 'Сотрудник не найден'})

@app.route('/api/update_extra_info', methods=['POST'])
def update_extra_info():
    data = request.get_json()
    db = read_db()
    
    emp_id = data.get('id')
    current_user_name = data.get('current_user_name', 'Неизвестно')
    
    for emp in db['employees']:
        if emp['id'] == emp_id:
            emp['extra_info'] = data.get('extra_info', {})
            write_db(db)
            add_log("Редактирование доп. информации", current_user_name, emp['full_name'])
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Сотрудник не найден'})

@app.route('/api/delete_employee', methods=['POST'])
def delete_employee():
    data = request.get_json()
    db = read_db()
    
    emp_id = data.get('id')
    current_user_role = data.get('current_user_role')
    current_user_name = data.get('current_user_name', 'Неизвестно')
    
    target = next((e for e in db['employees'] if e['id'] == emp_id), None)
    if not target:
        return jsonify({'success': False, 'message': 'Сотрудник не найден'})
    if current_user_role == 'hr':
        return jsonify({'success': False, 'message': 'Кадровик не может удалять'})
    if target['role'] == 'admin':
        return jsonify({'success': False, 'message': 'Нельзя удалить старшего администратора'})
    
    db['employees'] = [e for e in db['employees'] if e['id'] != emp_id]
    write_db(db)
    add_log("Удаление", current_user_name, target['full_name'])
    return jsonify({'success': True})