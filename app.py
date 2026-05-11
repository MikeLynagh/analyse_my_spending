from flask import Flask, render_template
from werkzeug.utils import secure_filename

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('upload_form.html')

@app.route('/upload', methods=['POST'])
def upload_file():