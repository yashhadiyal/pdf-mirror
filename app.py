from flask import Flask, render_template, request, send_from_directory, redirect, url_for
from flask_socketio import SocketIO, emit
import os
from werkzeug.utils import secure_filename

# Create Flask app
app = Flask(__name__, static_folder='static', template_folder='templates')

# Config
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024  # 20MB upload limit

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Create uploads folder if missing
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

PDF_FILE = os.path.join(app.config['UPLOAD_FOLDER'], "current.pdf")

# Main route
@app.route("/")
def index():
    role = request.args.get("role", "public")  # ?role=admin or ?role=public
    return render_template("index.html", role=role)

# Upload route
@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get('pdf')
    if file and file.filename.endswith(".pdf"):
        filename = secure_filename("current.pdf")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect(url_for('index', role="admin"))

# Serve the current PDF file
@app.route("/pdf")
def serve_pdf():
    return send_from_directory(app.config['UPLOAD_FOLDER'], "current.pdf")

# SocketIO Events

@socketio.on('scroll')
def handle_scroll(data):
    emit('scroll', data, broadcast=True, include_self=False)

@socketio.on('highlight')
def handle_highlight(data):
    emit('highlight', data, broadcast=True, include_self=False)

@socketio.on('remove-highlight')
def handle_remove_highlight(data):
    emit('remove-highlight', data, broadcast=True, include_self=False)

# Run the app
if __name__ == "__main__":
    socketio.run(app, debug=True)
