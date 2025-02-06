from flask import Flask, request, jsonify
from flask_cors import CORS
import youtube_dl
import tempfile
import os
import speech_recognition as sr

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    return 'Hello world'

@app.route('/transcribe', methods=['POST'])
def transcribe():
  if 'url' not in request.form or request.form['url'] == '':
    return jsonify({'error': 'url is required'})
  
  url = request.form['url']

  try:
    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': '%(id)s-%(title)s.%(ext)s',
        'nopart': True
    }

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
      with youtube_dl.YoutubeDL(ydl_opts) as ydl:
          ydl.download([url], tmpfile.name)
          audio_file_path = 'audio.mp3'
          os.rename(tmpfile.name, audio_file_path)

    with sr.AudioFile(audio_file_path) as source:
        r = sr.Recognizer()
        audio = r.record(source)
        try:
          transcription = r.recognize_google(audio)
        except Exception as e:
          transcription = str(e)
        
        
    return jsonify({'status': 'success', 'transcription': transcription})
  except Exception as e:
    return jsonify({'status': 'error', 'message': str(e)})

