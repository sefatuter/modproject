from flask import Flask, render_template, Response, jsonify, request, redirect, url_for
import os
import time
import json
import sqlite3
import subprocess
from database import init_db, add_rule, get_all_rules, delete_rule, update_rule
from markupsafe import Markup
from rules import get_rule_files

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Allow up to 16MB
RULE_FILE_PATH = "/etc/nginx/modsec/custom_rules.conf"
RULES_DIRECTORY = "/usr/local/modsecurity-crs/rules/"

# Initialize the database
init_db()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/modsettings', methods=['GET', 'POST'])
def panel():    
    show_alert = False
    error_message = ""
    new_rule_id = None
    # Add Rule
    if request.method == 'POST':
        new_rule = request.form.get('newRule')
        if new_rule:
            # Get the ID of the newly added rule
            new_rule_id = add_rule(new_rule)  # You'll need to modify add_rule to return the ID

    rules = get_all_rules()    
    # Write rules to the ModSecurity configuration file
    try:
        rendered_rules = render_template('modsec_rules_template.j2', rules=rules)
        with open(RULE_FILE_PATH, 'w') as file:
            file.write(rendered_rules)    

        # Test nginx configuration before restart
        try:
            check_nginx()
        except subprocess.CalledProcessError as e:
            # If nginx test fails, delete the last added rule
            if request.method == 'POST' and new_rule:
                delete_rule(new_rule_id)
            show_alert = True
            error_message = f"NGINX configuration test failed. Rule was removed."
            return render_template('modsettings.html', rules=get_all_rules(), show_alert=show_alert, error_message=error_message)

        # If test passes, restart nginx
        restart_nginx()

    except IOError as e:
        if new_rule_id:
            delete_rule(new_rule_id)
        show_alert = True
        error_message = f"Error writing to configuration file: {e}"
    except subprocess.CalledProcessError as e:
        if new_rule_id:
            delete_rule(new_rule_id)            
        show_alert = True
        error_message = f"Error restarting NGINX: {e.stderr.decode()}"

    return render_template('modsettings.html', rules=rules, show_alert=show_alert, error_message=error_message)


@app.route('/delete_rule/<int:rule_id>', methods=['POST'])
def delete_rule_view(rule_id):
    delete_rule(rule_id)
    return redirect(url_for('panel'))

@app.route('/edit_rule/<int:rule_id>', methods=['POST'])
def edit_rule_view(rule_id):
    updated_rule = request.form.get('updatedRule')
    if updated_rule:
        update_rule(rule_id, updated_rule)
    return redirect(url_for('panel'))

#--- Logs ---

@app.route('/stream_logs')
def stream_logs():
    log_file_path = '/var/log/modsec_audit.log'

    def generate():
        with open(log_file_path, 'r') as log_file:
            log_file.seek(0, 2)  # Move to the end of the file
            while True:
                line = log_file.readline()
                if line:
                    yield f"data: {line.strip()}\n\n"
                time.sleep(0.2)  # Prevent high CPU usage
            
    return Response(generate(), content_type='text/event-stream')


#--- Rules ---

@app.route('/rules')
def rules_ui():
    rule_files = get_rule_files()
    return render_template('rules.html', rule_files=rule_files)

@app.route('/edit_rule/<filename>', methods=['GET', 'POST'])
def edit_rule_ui(filename):
    file_path = os.path.join(RULES_DIRECTORY, filename)
    if request.method == 'POST':
        # Save changes
        new_content = request.form.get('file_content')
        with open(file_path, 'w') as file:
            file.write(new_content)
        
        # Validate configuration
        try:
            check_nginx()
            restart_nginx()
            return "Changes saved and applied successfully."
        except subprocess.CalledProcessError as e:
            return f"Error applying changes: {e.stderr.decode()}"
    else:
        # Read file content
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                content = file.read()
            return render_template('edit_rule.html', filename=filename, content=content)
        else:
            return "File not found", 404

#--- Config ---
def restart_nginx():
    subprocess.run(['sudo', 'systemctl', 'restart', 'nginx'], check=True)

def check_nginx():
    subprocess.run(['sudo', 'nginx', '-t'], check=True, capture_output=True)


if __name__ == '__main__':
    app.run(debug=True)