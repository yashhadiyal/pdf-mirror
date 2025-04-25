from flask import Flask, render_template, request, send_from_directory, redirect
from flask_socketio import SocketIO, emit
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
socketio = SocketIO(app, cors_allowed_origins="*")

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

PDF_FILE = os.path.join(app.config['UPLOAD_FOLDER'], "current.pdf")

@app.route("/")
def index():
    role = request.args.get("role", "public")
    return render_template("index.html", role=role)

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files['pdf']
    if file:
        filename = secure_filename("current.pdf")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    return redirect("/?role=admin")

@app.route("/pdf")
def serve_pdf():
    return send_from_directory(app.config['UPLOAD_FOLDER'], "current.pdf")

@socketio.on('scroll')
def sync_scroll(data):
    emit('scroll', data, broadcast=True, include_self=False)

@socketio.on('highlight')
def sync_highlight(data):
    emit('highlight', data, broadcast=True, include_self=False)

if __name__ == "__main__":
    socketio.run(app, debug=True)
