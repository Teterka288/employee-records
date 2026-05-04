import http.server
import socketserver
import json
import os
from datetime import datetime

def create_app(port=8000):
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    HTML_DIR = os.path.join(BASE_DIR, 'html')
    CSS_DIR = os.path.join(BASE_DIR, 'css')
    JS_DIR = os.path.join(BASE_DIR, 'js')
    
    def add_log(db, action, user_name, target_name, details=""):
        log_entry = {
            "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "action": action,
            "user": user_name,
            "target": target_name,
            "details": details
        }
        with open('logs.json', 'r', encoding='utf-8') as f:
            logs = json.load(f)
        logs.insert(0, log_entry)
        with open('logs.json', 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        
        def do_GET(self):
            if self.path == '/' or self.path == '':
                self.path = '/html/index.html'
                return super().do_GET()
            
            if not self.path.startswith('/html/') and not self.path.startswith('/css/') and not self.path.startswith('/js/') and not self.path.startswith('/api/'):
                if self.path.endswith('.html'):
                    self.path = '/html' + self.path
                elif self.path.endswith('.css'):
                    self.path = '/css' + self.path
                elif self.path.endswith('.js'):
                    self.path = '/js' + self.path
            
            if self.path.endswith('.html'):
                file_path = os.path.join(HTML_DIR, os.path.basename(self.path))
                if os.path.exists(file_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                    return
            
            if self.path.endswith('.css'):
                file_path = os.path.join(CSS_DIR, os.path.basename(self.path))
                if os.path.exists(file_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/css; charset=utf-8')
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                    return
            
            if self.path.endswith('.js'):
                file_path = os.path.join(JS_DIR, os.path.basename(self.path))
                if os.path.exists(file_path):
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/javascript; charset=utf-8')
                    self.end_headers()
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                    return
            
            super().do_GET()
        
        def do_POST(self):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length).decode('utf-8') if length > 0 else '{}'
            
            if self.path == '/api/login':
                data = json.loads(body)
                login = data.get('login', '').strip().lower()
                password = data.get('password', '')
                
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                for emp in db['employees']:
                    if emp['password'] == password and (emp['login'].lower() == login or emp['email'].lower() == login):
                        add_log(db, "Вход в систему", emp['full_name'], "-")
                        self.send_json({'success': True, 'user': emp})
                        return
                
                self.send_json({'success': False})
            
            elif self.path == '/api/get_employees':
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                self.send_json({'success': True, 'employees': db['employees']})
            
            elif self.path == '/api/get_profile':
                data = json.loads(body)
                uid = data.get('user_id')
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                for emp in db['employees']:
                    if emp['id'] == uid:
                        self.send_json({'success': True, 'user': emp})
                        return
                self.send_json({'success': False})
            
            elif self.path == '/api/get_employee':
                data = json.loads(body)
                uid = data.get('user_id')
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                for emp in db['employees']:
                    if emp['id'] == uid:
                        self.send_json({'success': True, 'user': emp})
                        return
                self.send_json({'success': False, 'message': 'Пользователь не найден'})
            
            elif self.path == '/api/get_logs':
                with open('logs.json', 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                self.send_json({'success': True, 'logs': logs})
            
            elif self.path == '/api/add_employee':
                data = json.loads(body)
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                login = data.get('login', '').strip()
                if not login:
                    n = 1
                    while any(e['login'] == f'employee{n}' for e in db['employees']):
                        n += 1
                    login = f'employee{n}'
                else:
                    if any(e['login'] == login for e in db['employees']):
                        self.send_json({'success': False, 'message': 'Такой логин уже существует'})
                        return
                
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
                
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
                
                current_user = data.get('current_user', data.get('full_name', 'Система'))
                add_log(db, "Добавление сотрудника", current_user, emp['full_name'], f"Логин: {login}")
                
                self.send_json({'success': True, 'employee': emp})
            
            elif self.path == '/api/update_employee':
                data = json.loads(body)
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                emp_id = data.get('id')
                current_user_role = data.get('current_user_role')
                current_user_name = data.get('current_user_name', 'Неизвестно')
                
                for emp in db['employees']:
                    if emp['id'] == emp_id:
                        if current_user_role == 'hr' and (emp['role'] == 'admin' or emp['role'] == 'junior_admin'):
                            self.send_json({'success': False, 'message': 'Кадровик не может редактировать администраторов'})
                            return
                        
                        if current_user_role == 'junior_admin' and emp['role'] == 'admin':
                            self.send_json({'success': False, 'message': 'Нельзя редактировать старшего администратора'})
                            return
                        
                        old_values = f"ФИО: {emp['full_name']}, Должность: {emp['position']}"
                        
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
                                self.send_json({'success': False, 'message': 'Логин занят'})
                                return
                            emp['login'] = new_login
                        
                        with open('data.json', 'w', encoding='utf-8') as f:
                            json.dump(db, f, ensure_ascii=False, indent=2)
                        
                        add_log(db, "Редактирование", current_user_name, emp['full_name'], old_values)
                        
                        self.send_json({'success': True, 'employee': emp})
                        return
                
                self.send_json({'success': False, 'message': 'Сотрудник не найден'})
            
            elif self.path == '/api/update_extra_info':
                data = json.loads(body)
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                emp_id = data.get('id')
                current_user_role = data.get('current_user_role')
                current_user_id = data.get('current_user_id')
                current_user_name = data.get('current_user_name', 'Неизвестно')
                
                for emp in db['employees']:
                    if emp['id'] == emp_id:
                        can_edit = False
                        if current_user_role == 'admin':
                            can_edit = True
                        elif current_user_role == 'junior_admin' and emp['role'] != 'admin':
                            can_edit = True
                        elif current_user_role == 'hr' and emp['role'] != 'admin' and emp['role'] != 'junior_admin':
                            can_edit = True
                        elif current_user_id == emp_id:
                            can_edit = True
                        
                        if not can_edit:
                            self.send_json({'success': False, 'message': 'Нет прав на редактирование'})
                            return
                        
                        emp['extra_info'] = data.get('extra_info', {})
                        
                        with open('data.json', 'w', encoding='utf-8') as f:
                            json.dump(db, f, ensure_ascii=False, indent=2)
                        
                        add_log(db, "Редактирование доп. информации", current_user_name, emp['full_name'])
                        
                        self.send_json({'success': True})
                        return
                
                self.send_json({'success': False, 'message': 'Сотрудник не найден'})
            
            elif self.path == '/api/delete_employee':
                data = json.loads(body)
                emp_id = data.get('id')
                current_user_role = data.get('current_user_role')
                current_user_name = data.get('current_user_name', 'Неизвестно')
                
                with open('data.json', 'r', encoding='utf-8') as f:
                    db = json.load(f)
                
                target = next((e for e in db['employees'] if e['id'] == emp_id), None)
                if not target:
                    self.send_json({'success': False, 'message': 'Сотрудник не найден'})
                    return
                
                if current_user_role == 'hr':
                    self.send_json({'success': False, 'message': 'Кадровик не может удалять сотрудников'})
                    return
                
                if target['role'] == 'admin':
                    self.send_json({'success': False, 'message': 'Нельзя удалить старшего администратора'})
                    return
                
                if current_user_role == 'junior_admin' and target['role'] == 'junior_admin':
                    self.send_json({'success': False, 'message': 'Нельзя удалить другого администратора'})
                    return
                
                target_name = target['full_name']
                target_login = target['login']
                
                db['employees'] = [e for e in db['employees'] if e['id'] != emp_id]
                
                with open('data.json', 'w', encoding='utf-8') as f:
                    json.dump(db, f, ensure_ascii=False, indent=2)
                
                add_log(db, "Удаление", current_user_name, target_name, f"Логин: {target_login}")
                
                self.send_json({'success': True})
        
        def send_json(self, data):
            text = json.dumps(data, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(text)
    
    return socketserver.TCPServer(("", port), Handler)