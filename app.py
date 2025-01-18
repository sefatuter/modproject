from flask import Flask, render_template, Response
import time

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    
    
@app.route('/modsettings')
def panel():
    return render_template('modsettings.html')

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