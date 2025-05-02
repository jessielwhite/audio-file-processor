import os
from celery import Celery
from moviepy import AudioFileClip
import boto3

app = Celery("av-worker",
	broker=os.environ.get('CELERY_BROKER_URL'),
	backend=os.environ.get('CELERY_RESULT_BACKEND')
)

s3 = boto3.client('s3')

def download_from_s3(bucket_name, key, download_path):
    s3.download_file(bucket_name, key, download_path)

def upload_to_s3(bucket_name, key, file_path):
    s3.upload_file(file_path, bucket_name, key)

def convert_audio(input_path, output_path, bitrate, sample_rate, channels):
    audio = AudioFileClip(input_path)
    audio = audio.set_fps(sample_rate).set_audio_channels(channels)
    audio.write_audiofile(output_path, codec="aac", bitrate=bitrate)

@app.task(soft_time_limit=60 * 60)
def voiceover(voiceover_id):
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    input_key = f"voiceovers/{voiceover_id}/input_audio"
    output_key_high = f"voiceovers/{voiceover_id}/high_quality.m4a"
    output_key_browser = f"voiceovers/{voiceover_id}/browser_quality.m4a"

    input_path = "/tmp/input_audio"
    high_quality_path = "/tmp/high_quality.m4a"
    browser_quality_path = "/tmp/browser_quality.m4a"

    download_from_s3(bucket_name, input_key, input_path)
    convert_audio(input_path, high_quality_path, bitrate="256k", sample_rate=48000, channels=2)
    convert_audio(input_path, browser_quality_path, bitrate="128k", sample_rate=44100, channels=2)

    upload_to_s3(bucket_name, output_key_high, high_quality_path)
    upload_to_s3(bucket_name, output_key_browser, browser_quality_path)

    os.remove(input_path)
    os.remove(high_quality_path)
    os.remove(browser_quality_path)

    return True
