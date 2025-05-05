from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from celery import Celery
import os
import boto3
import prometheus_client
from botocore.exceptions import NoCredentialsError
from uuid import uuid4

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/yourdatabase'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200 MB
ALLOWED_EXTENSIONS = {'wav', 'aac', 'm4a', 'mp3'}

db = SQLAlchemy(app)
celery = Celery(app.name, broker=os.environ.get('CELERY_BROKER_URL'), backend=os.environ.get('CELERY_BROKER_URL'))

S3_BUCKET = 'your-s3-bucket'
S3_REGION = 'your-region'
s3_client = boto3.client('s3')

class Voiceover(db.Model):
    voiceover_id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    job_id = db.Column(db.String(255), nullable=False)
    job_status = db.Column(db.String(50), nullable=False, default=1)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_signed_url(key):
    try:
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': S3_BUCKET, 'Key': key},
            ExpiresIn=3600
        )
        return url
    except NoCredentialsError:
        return None

@app.route('/voiceover', methods=['POST'])
def upload_voiceover():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    video_id = request.form.get('video_id')
    if not video_id:
        return jsonify({'error': 'Missing video_id'}), 400
    
    ## Sanitize filename
    filename = secure_filename(file.filename)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(file_path)

    ## Insert new record into Voiceover table
    voiceover = Voiceover(
        video_id=video_id,
        filename=filename,
        job_id='',
        job_status=1
    )
    db.session.add(voiceover)
    db.session.commit()

    task_id = str(uuid4())
    voiceover_id = voiceover.voiceover_id
    celery.send_task('av-worker.voiceover', task_id=task_id, args=(voiceover_id,))
    voiceover.job_id = task_id
    db.session.commit()

    return jsonify({'voiceover_id': voiceover.voiceover_id, 'job_id': task_id}), 201

@app.route('/voiceover/<int:voiceover_id>', methods=['GET'])
def get_voiceover_status(voiceover_id):
    voiceover = Voiceover.query.get(voiceover_id)
    if not voiceover:
        return jsonify({'error': 'Voiceover not found'}), 404
    
    ## Get current status of Celery job
    task = celery.AsyncResult(voiceover.job_id)
    
    if task:
        voiceover = Voiceover.query.get(voiceover_id)
        voiceover.job_status = task.status
        db.session.commit()

        response = {
            'voiceover_id': voiceover.voiceover_id,
            'job_status': voiceover.job_status
        }

        if voiceover.job_status == 2:
            processed_key = f'processed/{voiceover.voiceover_id}.mp3'
            proxy_key = f'proxies/{voiceover.voiceover_id}_proxy.mp3'
            response['processed_url'] = generate_signed_url(processed_key)
            response['proxy_url'] = generate_signed_url(proxy_key)

        return jsonify(response)
    return jsonify({'error': 'Task not found'}), 404

if __name__ == '__main__':
    app.run(debug=True)
