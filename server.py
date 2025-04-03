from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import face_recognition
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import cv2
import io

# Initialize Flask app and Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Load the stored face encoding from an image
import os

# Ensure the file exists
stored_image_path = os.path.join(os.path.dirname(__file__), "stored_face.jpg")
if not os.path.exists(stored_image_path):
    raise FileNotFoundError(f"File 'stored_face.jpg' not found at {stored_image_path}")

stored_image = face_recognition.load_image_file(stored_image_path)
stored_face_encoding = face_recognition.face_encodings(stored_image)[0]

@app.route('/')
def index():
    return render_template('/index.html')

# Handle receiving the frame from the client
@socketio.on('send_frame')
def handle_frame(data):
    # Decode the base64 image data
    img_data = base64.b64decode(data.split(',')[1])
    
    # Convert image data to a format face_recognition can use
    img = Image.open(BytesIO(img_data))
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    # Use face_recognition to detect faces and compare
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    if face_encodings:
        # Compare with the stored face encoding
        match_results = face_recognition.compare_faces([stored_face_encoding], face_encodings[0])

        if match_results[0]:
            emit('face_recognition_result', 'Face matched!')
        else:
            emit('face_recognition_result', 'Face did not match.')
    else:
        emit('face_recognition_result', 'No face detected.')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=4999)
