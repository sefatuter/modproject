from flask import Flask, render_template, Response, jsonify, request, redirect, url_for
import os
import time
import json
import sqlite3
import subprocess
from database import init_db, add_rule, get_all_rules, delete_rule, update_rule
from markupsafe import Markup
from rules import get_rule_files, RULE_DESCRIPTIONS

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
    temp_file_path = f"{file_path}.temp"

    description = RULE_DESCRIPTIONS.get(filename, "Unknown Rule")

    if request.method == 'POST':
        # TEMP FILE
        subprocess.run(['sudo', 'cp', file_path, temp_file_path], check=True, capture_output=True)
        # Save changes
        new_content = request.form.get('file_content')

        # Write mew content
        with open(file_path, 'w') as file:
            file.write(new_content)
        
        # with open(file_path, 'r') as file:
        #     content = file.read()
        
        
        
        # Validate configuration
        try:
            check_nginx()
            restart_nginx()
            subprocess.run(['sudo', 'rm', '-rf', f'{RULES_DIRECTORY}{filename}.temp'], check=True, capture_output=True)
            return render_template('edit_rule.html',filename=filename, content=content, description=description, show_alert=True, message=f"Rule added to {filename}, changes saved.", icon="success")
        except subprocess.CalledProcessError as e:
            subprocess.run(['sudo', 'mv', f'{RULES_DIRECTORY}{filename}.temp', f'{RULES_DIRECTORY}{filename}'], check=True, capture_output=True)
            return render_template('edit_rule.html', filename=filename, content=content, description=description, show_alert=True, message=f"Rule cannot be added {filename}, changes are not saved.", icon="error")

    else:
        # Read file content
        if os.path.exists(file_path):
            # with open(file_path, 'r') as file:
            #     content = file.read()
            content = parse_modsecurity_file(file_path)
            return render_template('edit_rule.html', filename=filename, content=content, description=description, show_alert=False)
        else:
            return "File not found", 404

#--- Config ---
def restart_nginx():
    subprocess.run(['sudo', 'systemctl', 'restart', 'nginx'], check=True)

def check_nginx():
    subprocess.run(['sudo', 'nginx', '-t'], check=True, capture_output=True)

def parse_modsecurity_file(file_path):
    """
    Parses a ModSecurity rules file and extracts only SecRule and SecAction blocks.
    Ignores comments and captures multiline blocks neatly.
    """
    rules = []
    current_rule = []
    in_rule_block = False  # Flag to detect multiline rules

    with open(file_path, 'r') as file:
        for line in file:
            stripped_line = line.strip()

            # Skip comments and empty lines
            if not stripped_line or stripped_line.startswith("#"):
                continue

            # Detect the start of a SecRule or SecAction block
            if stripped_line.startswith("SecRule") or stripped_line.startswith("SecAction"):
                if in_rule_block:
                    # Save the previous rule if we're in a block
                    rules.append("\n".join(current_rule))
                    current_rule = []
                in_rule_block = True

            # Collect lines that belong to the current rule block
            if in_rule_block:
                current_rule.append(line.rstrip("\\").strip())  # Handle multiline continuation
                # Detect the end of a rule block (no trailing '\')
                if not stripped_line.endswith("\\"):
                    rules.append("\n".join(current_rule))
                    current_rule = []
                    in_rule_block = False

    # Ensure the last rule is added
    if current_rule:
        rules.append("\n".join(current_rule))

    return rules



if __name__ == '__main__':
    app.run(debug=True)