from flask import Blueprint, render_template, request, redirect, url_for, flash
from database import Database
from functools import wraps
import os
import sqlite3
import json

admin = Blueprint('admin', __name__)
db = Database()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        admin_password = request.cookies.get('admin_password')
        if admin_password != os.getenv('ADMIN_PASSWORD'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['password'] == os.getenv('ADMIN_PASSWORD'):
            response = redirect(url_for('admin.dashboard'))
            response.set_cookie('admin_password', request.form['password'])
            return response
        flash('كلمة المرور غير صحيحة')
    return render_template('admin/login.html')

@admin.route('/admin/dashboard')
@admin_required
def dashboard():
    templates = db.list_templates()
    return render_template('admin/dashboard.html', templates=templates)

@admin.route('/admin/templates/new', methods=['GET', 'POST'])
@admin_required
def new_template():
    if request.method == 'POST':
        template_name = request.form['name']
        template_type = request.form['type']
        template_data = {
            'type': template_type,
            'content': request.form['content']
        }
        if template_type == 'buttons':
            buttons = []
            for i in range(int(request.form['button_count'])):
                button = {
                    'type': request.form[f'button_type_{i}'],
                    'title': request.form[f'button_title_{i}'],
                    'payload': request.form[f'button_payload_{i}']
                }
                buttons.append(button)
            template_data['buttons'] = buttons
        
        db.save_template(template_name, template_data)
        flash('تم حفظ القالب بنجاح')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/new_template.html')

@admin.route('/admin/responses', methods=['GET', 'POST'])
@admin_required
def manage_responses():
    if request.method == 'POST':
        trigger = request.form['trigger']
        response_type = request.form['response_type']
        if response_type == 'text':
            response_data = {
                'type': 'text',
                'content': request.form['response_content']
            }
        elif response_type == 'media':
            response_data = {
                'type': 'media',
                'media_type': request.form.get('media_type'),
                'media_url': request.form.get('media_url')
            }
            # يمكن إضافة دعم رفع الملفات لاحقاً
        else:
            response_data = {'type': response_type}
        db.save_custom_response(trigger, response_data)
        flash('تم حفظ الرد بنجاح', 'success')
        return redirect(url_for('admin.manage_responses'))
    responses = []
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT trigger, response FROM responses')
        for row in cursor.fetchall():
            trigger = row[0]
            data = json.loads(row[1])
            resp = {'trigger': trigger, 'type': data.get('type'), 'content': data.get('content', '')}
            if data.get('type') == 'media':
                resp['media_type'] = data.get('media_type')
                resp['media_url'] = data.get('media_url')
            responses.append(resp)
    return render_template('admin/responses.html', responses=responses)

@admin.route('/admin/response/<trigger>/delete')
@admin_required
def delete_response(trigger):
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM responses WHERE trigger = ?', (trigger,))
        conn.commit()
    flash('تم حذف الرد بنجاح', 'success')
    return redirect(url_for('admin.manage_responses'))

@admin.route('/admin/response/<trigger>/edit', methods=['GET', 'POST'])
@admin_required
def edit_response(trigger):
    with sqlite3.connect(db.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT response FROM responses WHERE trigger = ?', (trigger,))
        row = cursor.fetchone()
        if not row:
            flash('الرد غير موجود', 'danger')
            return redirect(url_for('admin.manage_responses'))
        data = json.loads(row[0])
    if request.method == 'POST':
        response_type = request.form['response_type']
        if response_type == 'text':
            response_data = {
                'type': 'text',
                'content': request.form['response_content']
            }
        elif response_type == 'media':
            response_data = {
                'type': 'media',
                'media_type': request.form.get('media_type'),
                'media_url': request.form.get('media_url')
            }
        else:
            response_data = {'type': response_type}
        db.save_custom_response(trigger, response_data)
        flash('تم تحديث الرد بنجاح', 'success')
        return redirect(url_for('admin.manage_responses'))
    return render_template('admin/edit_response.html', trigger=trigger, data=data)

@admin.route('/admin/template/<name>')
@admin_required
def view_template(name):
    template = db.get_template(name)
    if not template:
        flash('القالب غير موجود', 'danger')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/view_template.html', template={'name': name, 'data': template})

@admin.route('/admin/template/<name>/edit', methods=['GET', 'POST'])
@admin_required
def edit_template(name):
    template = db.get_template(name)
    if not template:
        flash('القالب غير موجود', 'danger')
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        template_type = request.form['type']
        template_data = {
            'type': template_type,
            'content': request.form['content']
        }
        if template_type == 'buttons':
            buttons = []
            for i in range(int(request.form['button_count'])):
                button = {
                    'type': request.form.get(f'button_type_{i}'),
                    'title': request.form.get(f'button_title_{i}'),
                    'payload': request.form.get(f'button_payload_{i}')
                }
                buttons.append(button)
            template_data['buttons'] = buttons
        if template_type == 'media':
            template_data['media_type'] = request.form.get('media_type')
            template_data['media_url'] = request.form.get('media_url')
            # يمكن إضافة دعم رفع الملفات لاحقاً
        db.save_template(name, template_data)
        flash('تم تحديث القالب بنجاح', 'success')
        return redirect(url_for('admin.view_template', name=name))
    return render_template('admin/edit_template.html', template={'name': name, 'data': template})
