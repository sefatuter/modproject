from flask import Flask, render_template, Response, jsonify, request, redirect, url_for
import os
import time
import json
import sqlite3
import subprocess
from database import init_db, add_rule, get_all_rules, delete_rule, update_rule
from markupsafe import Markup

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Allow up to 16MB
RULE_FILE_PATH = "/etc/nginx/modsec/custom_rules.conf"
# RULE_FILE_PATH = "/home/sefaubuntu/modproject/test.txt"
# Initialize the database
init_db()

@app.route('/')
def index():
    return render_template('index.html')
    
    
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
        # current_user = subprocess.check_output(['whoami']).decode().strip()
        # current_permissions = subprocess.check_output(['ls', '-l', RULE_FILE_PATH]).decode().strip()
        # print(f"Current user: {current_user}")
        # print(f"File permissions: {current_permissions}")
        rendered_rules = render_template('modsec_rules_template.j2', rules=rules)
        with open(RULE_FILE_PATH, 'w') as file:
            file.write(rendered_rules)    

        # Test nginx configuration before restart
        try:
            subprocess.run(['sudo', 'nginx', '-t'], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            # If nginx test fails, delete the last added rule
            if request.method == 'POST' and new_rule:
                delete_rule(new_rule_id)
            show_alert = True
            error_message = f"NGINX configuration test failed. Rule was removed."
            return render_template('modsettings.html', rules=get_all_rules(), show_alert=show_alert, error_message=error_message)

        # If test passes, restart nginx
        subprocess.run(['sudo', 'systemctl', 'restart', 'nginx'], check=True)

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


# @app.route('/rules', methods=['GET'])
# def get_rules():
#     rules = read_rules()
#     return jsonify({"rules": rules})


# @app.route('/rules', methods=['POST'])
# def add_new_rule():
#     print(request.json)
#     new_rule = request.json.get('rule')
#     add_rule(new_rule)
#     return jsonify({"success": True, "message": "Rule added successfully!"})


# @app.route('/rules/<int:rule_id>', methods=['PUT'])
# def update_existing_rule(rule_id):
#     updated_rule = request.json.get('rule')
#     update_rule(rule_id, updated_rule)
#     return jsonify({"success": True, "message": "Rule updated successfully!"})


# @app.route('/rules/<int:rule_id>', methods=['DELETE'])
# def delete_existing_rule(rule_id):
#     delete_rule(rule_id)
#     return jsonify({"success": True, "message": "Rule deleted successfully!"})


# #--- Functions ---

# def read_rules():
#     result = os.popen("sudo /usr/local/bin/manage_rules.sh read").read()
#     return result.splitlines()



# def add_rule(new_rule):
#     os.system(f"sudo /usr/local/bin/manage_rules.sh write '{new_rule}'")

    
    
# def update_rule(rule_id, updated_rule):
#     os.system(f"sudo /usr/local/bin/manage_rules.sh update {rule_id+1} '{updated_rule}'")

# def delete_rule(rule_id):
#     os.system(f"sudo /usr/local/bin/manage_rules.sh delete {rule_id+1}")
