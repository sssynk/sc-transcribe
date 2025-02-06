from flask import Flask, request, jsonify, send_from_directory, request
from flask_cors import CORS
import youtube_dl
import tempfile
import os
import speech_recognition as sr

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory("./", "index.html")

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

    import subprocess
    import shlex

    def which(program):
        command = program.split("/")[-1]
        return subprocess.check_output(shlex.split(command))

    def ffmpeg_convert(input_file, output_file):
        which_program = "ffmpeg"
        try:
            which(which_program)
        except:
            print("failed to find ffmpeg")
            return None
        command = [
            "ffmpeg",
            "-i",
            input_file,
            "-y",
            "-loglevel",
            "warning",
            "-f",
            "pipe",
            "pipe",
        ]
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        output_file = output_file.replace(".mp3", ".wav")
        result = which(which_program)
        return result, proc

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': '%(id)s-%(title)s.%(ext)s',
        'nopart': True
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            audio_file_path = tmpfile.name
            input_file = tmpfile.name
            output_file = "audio.wav"
            ffmpeg_convert(input_file, output_file)
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

if __name__ == '__main__':
  app.run(debug=True, port=3000)


