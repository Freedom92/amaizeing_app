from flask import Flask, request, render_template, redirect, url_for, session, send_from_directory
from flask_socketio import SocketIO, emit
#from tensorflow.keras.models import load_model
#from tensorflow.keras.preprocessing.image import img_to_array, load_img
import numpy as np
import os
import requests
import json
import datetime  

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key'
socketio = SocketIO(app)

classes = [
    'Anthracnose Stalk Rot', 'Common Smut Corn', 'Corn leaf spot', 'Corn rust', 
    'Crazy Top', 'Curvularia leaf spot', 'Diplodia Ear Rot', 'Eyespot', 
    'Fall Army Worm', 'Fusarium Ear Rot', 'Gibberella Ear Rot', "Goss's Bacterial Wilt",
    'Gray Leaf Spot', 'Healthy', 'Maize Common Rust', 'Maize Lethal Necrosis', 
    'Maize Streak Virus', 'Northern Leaf Blight', 'Northern Leaf Spot', 
    'Phaeosphaeria Leaf Spot', 'Southern Rusts', 'Stewarts Wilt'
]

# Load the pre-trained model
#model = load_model('stack_ensemble_using_svm.h5')

# Supported languages
LANGUAGES = ['en', 'es', 'fr']

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load translations based on the selected language
def load_translations(language):
    with open(f'translations/{language}.json') as f:
        return json.load(f)

# Route to set the language in the session
@app.route('/change_language', methods=['POST'])
def change_language():
    selected_language = request.form['language']
    if selected_language in LANGUAGES:
        session['language'] = selected_language
    return redirect(url_for('index'))

# Function to prepare an image for prediction
#def prepare_image(image_path):
 #   img = load_img(image_path, target_size=(224, 224))
 #   img = img_to_array(img)
 #   img = np.expand_dims(img, axis=0)
 #   img = img / 255.0  # Normalize to [0, 1]
 #   return img
@app.route('/cultivation', methods=['GET'])
@app.route('/cultivation')
def cultivation():
    return render_template('maize_cultivation.html')

# Get disease info for the predicted class
def get_disease_info(disease_name):
    treatments = {
        'Northern Leaf Blight': {
            'symptoms': 'Gray-green lesions on leaves that merge to form larger areas of dead tissue.',
            'triggers': 'Cool, moist conditions, often in late summer or fall.',
            'agrochemicals': 'Fungicides, such as strobilurins or triazoles.',
            'biological_remedy': 'Use resistant hybrids and practice crop rotation.'
        },
        'Gibberella Ear Rot': {
            'symptoms': 'Red or pink mold starting at the ear tip and progressing down.',
            'triggers': 'Wet and cool conditions during the silking period.',
            'agrochemicals': 'Fungicides are generally not effective once the disease has set in.',
            'biological_remedy': 'Use resistant hybrids and practice field sanitation.'
        },
        'Maize Streak Virus': {
            'symptoms': 'Yellow to white streaks along the leaf veins, stunted growth, and poor ear development.',
            'triggers': 'Warm, humid conditions during the rainy season.',
            'agrochemicals': 'Insecticides to control the leafhopper vector.',
            'biological_remedy': 'Plant resistant varieties and control leafhopper populations.'
        },
        'Crazy Top': {
            'symptoms': 'Twisted tassels and proliferation of leaves at the tassel.',
            'triggers': 'Waterlogged soils early in the season.',
            'agrochemicals': 'Not applicable for this disease.',
            'biological_remedy': 'Improve field drainage and use resistant hybrids.'
        },
        # Add entries for all other diseases predicted by your model.
    }

    # Use `.get()` to return a default empty dictionary if the disease name is not found.
    return treatments.get(disease_name, {
        'symptoms': 'Information not available.',
        'triggers': 'Information not available.',
        'agrochemicals': 'Information not available.',
        'biological_remedy': 'Information not available.'
    })

@app.route('/diseases', methods=['GET'])
@app.route('/diseases', methods=['GET'])
def diseases():
   
    disease_info = [
        {
            "name": "Northern Leaf Blight",
            "description": "Northern Leaf Blight is a fungal disease that causes lesions on maize leaves, reducing photosynthesis and yield.",
            "cause": "Caused by the fungus Exserohilum turcicum.",
            "season": "Most prevalent in cool, moist conditions, often in late summer and early fall.",
            "symptoms": "Long, gray-green lesions on leaves that can merge, causing large areas of dead tissue.",
            "combat": "Plant resistant hybrids, practice crop rotation, and use fungicides if necessary.",
            "image": "northern_leaf_blight1.jpg"
        },
        { 
                "name": " Maize Common Rust",
                "description": "Common Rust is a fungal disease that affects maize leaves, characterized by the formation of reddish-brown pustules, which can lead to reduced photosynthesis and lower crop yields.",
                "cause": "Caused by the fungus Puccinia sorghi.",
                "season": "Most prevalent in warm, humid conditions during the summer months.",
                "symptoms": "Elongated, dark brown to reddish-brown pustules appear on leaves, which can merge and cause significant leaf damage.",
                "combat": "Plant resistant hybrids, practice crop rotation, and apply fungicides as necessary.",
                "image": "common_rust.jpg"
        },

        {
            "name": "Gibberella Ear Rot",
            "description": "Gibberella Ear Rot is a common maize disease that affects the ears, leading to reduced grain quality and yield.",
            "cause": "Caused by the fungus Fusarium graminearum.",
            "season": "Typically occurs in wet and cool conditions, especially during the silking period.",
            "symptoms": "Red or pink mold on the ear, often starting at the tip and progressing downward.",
            "combat": "Use crop rotation, plant resistant hybrids, and manage field debris to reduce inoculum.",
            "image": "gibberella_ear_rot.jpg"
        },
        {
            "name": "Maize Streak Virus",
            "description": "Maize Streak Virus is a viral disease transmitted by leafhoppers that causes severe leaf striping and reduced yield.",
            "cause": "Caused by the Maize streak virus (MSV), transmitted by Cicadulina leafhoppers.",
            "season": "Most severe in warm, humid conditions, usually during the rainy season.",
            "symptoms": "Yellow to white streaks along the veins of the leaves, stunted growth, and poor ear development.",
            "combat": "Plant resistant varieties, control leafhopper populations, and avoid planting during high vector activity periods.",
            "image": "maize_streak_virus.jpeg"
        },
        {
            "name": "Crazy Top",
            "description": "Crazy Top is a disease that causes abnormal growth in maize, including twisted and proliferated tassels.",
            "cause": "Caused by the soilborne fungus Sclerophthora macrospora.",
            "season": "Common after heavy rains or flooding during the early growth stages of the crop.",
            "symptoms": "Distorted tassels, proliferation of leaves at the tassel, and abnormal growth of the ears.",
            "combat": "Improve field drainage, avoid planting in waterlogged conditions, and use resistant hybrids where available.",
            "image": "crazy_top.jpg"
        },
       {
            "name": "Anthracnose Stalk Rot",
            "description": "A fungal disease that affects maize stalks, leading to reduced yield.",
            "cause": "Caused by the fungus Colletotrichum graminicola.",
            "season": "Common in late summer and early fall, especially after wet weather.",
            "symptoms": "Stalk discoloration, weak stalks, and lodging.",
            "combat": "Use resistant varieties, crop rotation, and proper field sanitation.",
            "image": "anthracnose stalk rot_1.jpg"
        },
        {
            "name": "Common Smut Corn",
            "description": "A fungal disease that causes galls on various parts of the plant.",
            "cause": "Caused by the fungus Ustilago maydis.",
            "season": "Appears during warm and dry seasons, often after hail or other injuries to the plant.",
            "symptoms": "Large, grayish-white galls on ears, leaves, and stems.",
            "combat": "Plant resistant hybrids, avoid mechanical damage, and manage field debris.",
            "image": "common_smut_corn.jpg"
        },
       
    ]

    return render_template('diseases.html', diseases=disease_info)
  

# Index route
@app.route('/', methods=['GET'])
def index():
    language = session.get('language', 'en')
    translations = load_translations(language)   
    return render_template('index.html', translations=translations)

# Route to serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Prediction route
@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files or request.files['file'].filename == '':
        return redirect(url_for('index'))

    file = request.files['file']
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    img = prepare_image(file_path)

    # Make prediction
    predictions = model.predict(img)
    predicted_index = np.argmax(predictions)
    predicted_class = classes[predicted_index]
    confidence = round(predictions[0][predicted_index] * 100, 2)

    # Get detailed info about the disease
    disease_info = get_disease_info(predicted_class)

    language = session.get('language', 'en')
    translations = load_translations(language)

    # Render template with the uploaded image, prediction result, and confidence score
    return render_template('index.html', filename=file.filename, prediction=predicted_class, confidence=confidence, disease_info=disease_info, translations=translations)
# Weather route for displaying a detailed weather forecast for the next 5 days
@app.route('/weather')
def weather():
    # Starting date: 23 September 2024
    start_date = datetime.datetime(2024, 9, 23)
    
    # Dummy weather data for 5 days
    weather_data = [
        {'condition': 'Sunny', 'high': 21, 'low': 10, 'humidity': 64, 'wind_speed': 20, 'icon': 'Tuesday.png'},
        {'condition': 'Sunny', 'high': 25, 'low': 21, 'humidity': 65, 'wind_speed': 23, 'icon': 'Tuesday.png'},
        {'condition': 'Partly Cloudy Rain', 'high': 22, 'low': 17, 'humidity': 85, 'wind_speed': 12, 'icon': 'Monday.png'},
        {'condition': 'Thunderstorms', 'high': 23, 'low': 18, 'humidity': 90, 'wind_speed': 18, 'icon': 'Thursday.png'},
        {'condition': 'Overcast', 'high': 25, 'low': 19, 'humidity': 80, 'wind_speed': 14, 'icon': 'Friday.png'}
    ]

    # Add the day and date info
    for i, day in enumerate(weather_data):
        day_date = start_date + datetime.timedelta(days=i)
        day['day'] = day_date.strftime('%A')  # Monday, Tuesday, etc.
        day['date'] = day_date.strftime('%d %B %Y')  # e.g., 23 September 2024

    return render_template('weather.html', weather_data=weather_data)

# Real-time Chat route
@app.route('/chat')
def chat():
    language = session.get('language', 'en')
    translations = load_translations(language)
    return render_template('chat.html', translations=translations)

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)


