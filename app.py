from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ehr.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configure uploads folder inside the static folder so files can be served easily
upload_path = os.path.join(app.root_path, 'static', 'uploads')
if not os.path.exists(upload_path):
    os.makedirs(upload_path)
app.config['UPLOAD_FOLDER'] = upload_path

db = SQLAlchemy(app)

# Models


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Patient ID auto-assigned
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    blood_group = db.Column(db.String(10), nullable=False)
    consultations = db.relationship(
        'Consultation', backref='patient', lazy=True)


class Consultation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey(
        'patient.id'), nullable=False)
    note = db.Column(db.Text, nullable=True)
    audio_filename = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()

# Home page: list all patients


@app.route('/')
def index():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

# Create a new patient profile


@app.route('/patient/new', methods=['GET', 'POST'])
def new_patient():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        blood_group = request.form['blood_group']
        if not name or not address or not blood_group:
            # flash('Please fill in all required fields.')
            return redirect(url_for('new_patient'))
        patient = Patient(name=name, address=address, blood_group=blood_group)
        db.session.add(patient)
        db.session.commit()
        # flash('Patient added successfully.')
        return redirect(url_for('index'))
    return render_template('add_patient.html')

# View and edit an existing patient profile


@app.route('/patient/<int:patient_id>', methods=['GET', 'POST'])
def patient_detail(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.name = request.form['name']
        patient.address = request.form['address']
        patient.blood_group = request.form['blood_group']
        if not patient.name or not patient.address or not patient.blood_group:
            # flash('Please fill in all required fields.')
            return redirect(url_for('patient_detail', patient_id=patient_id))
        db.session.commit()
        # flash('Patient details updated.')
        return redirect(url_for('patient_detail', patient_id=patient_id))
    return render_template('patient_detail.html', patient=patient)

# Create a new consultation note for a patient


@app.route('/patient/<int:patient_id>/consultation/new', methods=['GET', 'POST'])
def new_consultation(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        note = request.form.get('note', '')
        audio_file = request.files.get('audio_file')
        audio_filename = None
        if audio_file and audio_file.filename != '':
            filename = generate_audio_name(
                patient_id, secure_filename(audio_file.filename))
            new_file_location = os.path.join(
                app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(new_file_location)
            audio_filename = filename
            ai_notes = process_audio_note(new_file_location)
            note += "\n\nAI Notes from the audio:\n" + ai_notes
        consultation = Consultation(
            patient_id=patient.id, note=note, audio_filename=audio_filename)
        db.session.add(consultation)
        db.session.commit()
        # flash('Consultation note added.')
        return redirect(url_for('patient_detail', patient_id=patient.id))
    return render_template('add_consultation.html', patient=patient)


def process_audio_note(audio_filename):
    from dotenv import load_dotenv
    from transformers import pipeline
    import os
    from google import genai

    load_dotenv("tokens.env")
    asr_pipeline = pipeline(
        "automatic-speech-recognition",
        model="openai/whisper-base"
    )
    text = asr_pipeline(audio_filename, return_timestamps=True)['text']

    prompt_template = """I will give you a transcription of an audio between a doctor and a patient. 
    Based on the transcript I want you to summarise the conversation in points. 
    Only return a maximum of 10 points and no other extra greeting or conclusion text.
    
    Make sure that you do not include the name of the patient or the doctor. 
    Please refer to the patient as "the patient" and the doctor as "the doctor".

    The conversation is as follows: \n\n {{conversation}} \n\n"""

    prompt = prompt_template.replace("{{conversation}}", text)

    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text


def generate_audio_name(patient_id, old_name):
    extension = old_name.split(".")[-1]
    # check the uploads folder whether there are any existing consultations with the patient name and then number accordingly
    existing_files = os.listdir(app.config['UPLOAD_FOLDER'])
    existing_files = [
        f for f in existing_files if f.startswith("patient" + str(patient_id))]
    if len(existing_files) > 0:
        existing_files = [int(f.split("_")[-1].split(".")[0].strip("_audio"))
                          for f in existing_files]
        new_number = max(existing_files) + 1
    else:
        new_number = 1
    new_name = f"patient{patient_id}_audio{new_number}.{extension}"
    return new_name


if __name__ == '__main__':
    app.run(debug=True)
