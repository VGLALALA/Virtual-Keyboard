import gradio as gr
import face_recognition
import numpy as np

from PIL import Image

known_image = face_recognition.load_image_file(r"C:\Users\sting\Downloads\phys\faces\Sting.jpg")
known_face_encoding = face_recognition.face_encodings(known_image)[0]

def verify_face_from_image(image):
    if image is None:
        return "No image received"
    
    if isinstance(image, np.ndarray):
        rgb_frame = image
    else:
        rgb_frame = np.array(image.convert("RGB"))

    face_encodings = face_recognition.face_encodings(rgb_frame)

    if not face_encodings:
        return "No face detected"
    
    match_results = face_recognition.compare_faces([known_face_encoding], face_encodings[0])
    
    if match_results[0]:
        return "Face recognized! Redirecting to test page..."
    else:
        return "Face not recognized"

iface = gr.Interface(
    fn=verify_face_from_image,
    inputs=gr.Image(sources="webcam", streaming=False),
    outputs="text",
    title="Face Recognition Verification",
    description="Use your webcam to verify if the face is recognized."
)

iface.launch()
