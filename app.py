import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from PIL import Image
from io import BytesIO
from stegano import lsb

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_PATH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/encode')
def encode_page():
    return render_template('encode.html')

@app.route('/decode')
def decode_page():
    return render_template('decode.html')

@app.route('/encode', methods=['POST'])
def encode():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('encode_page'))
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('encode_page'))
    if file and allowed_file(file.filename):
        image = Image.open(file.stream)
        message = request.form['message']
        if not message:
            flash('No message to encode')
            return redirect(url_for('encode_page'))
        try:
            encoded_image = lsb.hide(image, message)
            byte_io = BytesIO()
            encoded_image.save(byte_io, format='PNG')
            byte_io.seek(0)
            return send_file(byte_io, as_attachment=True, download_name='encoded_' + file.filename, mimetype='image/png')
        except Exception as e:
            flash('Error encoding image: ' + str(e))
            return redirect(url_for('encode_page'))

@app.route('/decode', methods=['POST'])
def decode():
    if 'image' not in request.files:
        flash('No file part')
        return redirect(url_for('decode_page'))
    file = request.files['image']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('decode_page'))
    if file and allowed_file(file.filename):
        image = Image.open(file.stream)
        try:
            decoded_message = lsb.reveal(image)
            if not decoded_message:
                flash('No hidden message found')
                return redirect(url_for('decode_page'))
            return render_template('decode.html', decoded_message=decoded_message)
        except Exception as e:
            flash('Error decoding image: ' + str(e))
            return redirect(url_for('decode_page'))

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    app.run(debug=True)
