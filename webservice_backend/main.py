from __future__ import division
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session  # 로그인을 유지시켜주는 세션!
from werkzeug.utils import secure_filename
import pymysql
import os
import time
import requests, json
import librosa
import pyaudio
#pip install pipwin
#pipwin install pyaudio

import speech_recognition as sr  #pip3 install --upgrade speechrecognition

app = Flask(__name__)
app.secret_key = os.urandom(24)


@app.route('/')
def home():
    conn = pymysql.connect(
        user='admin',
        password='qwer1234',
        host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
        db='kti',
        charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT * FROM board ORDER BY bnum DESC;"
    cursor.execute(sql)
    result = cursor.fetchall()

    return render_template('index.html', datas=result)


@app.route('/login')
def login():
    return render_template('login.html')


# DB에서 사용자 확인후 로그인
@app.route('/dologin', methods=['POST'])
def dologin():
    userid = request.form.get('userid')
    userpw = request.form.get('userpw')

    conn = pymysql.connect(
        user='admin',
        password='qwer1234',
        host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
        db='kti',
        charset='utf8')
    cursor = conn.cursor()
    sql = "select mid, mpw, mname from member where mid = '" + userid + "' and mpw = '" + userpw + "';"

    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        print('로그인실패')
        return redirect(url_for('login'))
    else:
        print('로그인성공')
        session.clear()
        session['logFlag'] = True
        session['mid'] = result[0][0]
        session['mname'] = result[0][2]
        return redirect(url_for('home'))

    return 'goodluck'


# 로그아웃 기능  -
########################선생님 어떻게 로그아웃 적용시켰는지 보기
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


# 회원가입 페이지 접속
@app.route('/register')
def register():
    return render_template('register.html')


# DB에 회원 정보 저장
@app.route('/doregister', methods=['POST'])
def doregister():
    username = request.form.get('username')
    userid = request.form.get('userid')
    userpw = request.form.get('userpw')
    userpwagain = request.form.get('userpwagain')
    useremail = request.form.get('useremail')

    if userpw == userpwagain:
        conn = pymysql.connect(
            user='admin',
            password='qwer1234',
            host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
            db='kti',
            charset='utf8')
        cursor = conn.cursor()
        sql = "INSERT INTO member (mid, mpw, mname, memail) values ('" + userid + "', '" + userpw + "', '" + username + "','" + useremail + "');"
        cursor.execute(sql)
        conn.commit()
        return redirect(url_for('login'))
    else:
        print('잘못된 입력입니다.')
        return redirect(url_for('register'))
    return 'goodluck'


@app.route('/password')
def password():
    return render_template('password.html')

@app.route('/dopassword',methods=['POST'])
def dopassword():
    useremail = request.form.get('useremail')

    conn = pymysql.connect(
        user='admin',
        password='qwer1234',
        host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
        db='kti',
        charset='utf8')
    cursor = conn.cursor()
    sql = "select mid, mpw, memail from member where memail = '" + useremail + "';"

    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 0:
        print('잘못된 이메일입니다.')
        return redirect(url_for('password'))
    else:
        print('찾으신 정보는 다음과 같습니다.')
        id = result[0][0]
        pswd = result[0][1]
        email = result[0][2]
        print('ID : ', id, end='\n')
        print('PASSWORD : ', pswd, end='\n')
        print('EMAIL : ', email , end='\n')

        return render_template('returnpassword.html', datas=result)







@app.route('/board')
def board():
    conn = pymysql.connect(
        user='admin',
        password='qwer1234',
        host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
        db='kti',
        charset='utf8')
    cursor = conn.cursor()
    sql = "SELECT * FROM board ORDER BY bnum DESC;"
    cursor.execute(sql)
    result = cursor.fetchall()

    return render_template('board.html', datas=result)


# 게시글 작성 가기
@app.route('/content')
def content():
    if 'logFlag' in session:
        return render_template('content.html')
    else:
        return redirect(url_for('login'))



# 게시물 작성 후 db에 저장
@app.route('/docontent', methods=['POST'])
def docontent():
    title = request.form.get('title')
    contents = request.form.get('contents')
    writer = request.form.get('writer')

    conn = pymysql.connect(
        user='admin',
        password='qwer1234',
        host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
        db='kti',
        charset='utf8')

    cursor = conn.cursor()
    sql2 = "select mid from member where mid = '" + writer + "';"

    cursor.execute(sql2)
    result = cursor.fetchall()
    if len(result) == 0:
        print('올바른 id를 입력해주세요.')
        return redirect(url_for('content'))
    else:
        sql = "INSERT INTO board (btitle, bcontents, bwriter,btime) values ('" + title + "','" + contents + "','" + writer + "',now());"
        cursor.execute(sql)
        conn.commit()
        return render_template('board.html')


@app.route('/doupdate',methods=['POST'])
def doupdate():
    bnum = request.form.get('bnum')
    title = request.form.get('title')
    contents = request.form.get('contents')
    writer = request.form.get('writer')

    conn = pymysql.connect(
        user='admin',
        password='qwer1234',
        host='database-1.cieed6lc0z0o.ap-northeast-2.rds.amazonaws.com',
        db='kti',
        charset='utf8')
    cursor = conn.cursor()
    sql = "update board set btitle = '" + title + "' , bcontents = '" + contents + "' where bnum = '" + bnum + "';"
    cursor.execute(sql)
    conn.commit()

    return render_template('password.html')

# 말하면 음성인식 후 출력되게 하는 페이지
@app.route('/audio')
def audio():
    if 'logFlag' in session:
        return render_template('audio.html')
    else:
        return redirect(url_for('login'))


# 오디오 음성인식 기능
@app.route('/doaudio', methods = ["GET", "POST"])
def doaudio():
    start = request.form.get('start')

    if start == '시작':
        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something!")
            audio = r.listen(source)
            try:
                transcript = r.recognize_google(audio, language="ko-KR")
                transcript = translate(transcript)
                print("Google Speech Recognition thinks you said " + transcript)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return render_template('audio.html', transcript=transcript)


#-----------------------------------------------------------------


import re
import sys
import io
from google.cloud import speech
#from pydub import AudioSegment
#from pydub.utils import make_chunks
import pyaudio
from six.moves import queue
import wave
from google.cloud import texttospeech # pip install --upgrade google-cloud-texttospeech
#from playsound import playsound # 음성파일 재생하는 라이브러리 : pip install playsound

import requests    # pip install requests
from datetime import datetime
import time
import json
import scipy.io as sio
import scipy.io.wavfile

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/test/gcloud_key.json"


# 녹음 파일에서 음성 인식 진행
'''
def transcribe_file(speech_file):

    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="ko-KR",
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        print(u"Transcript: {}".format(result.alternatives[0].transcript))
'''
def transcribe_file(speech_file):
    text = ''
    client = speech.SpeechClient()

    with io.open(speech_file, "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED,
        sample_rate_hertz=48000,
        language_code="ko-KR",
    )

    response = client.recognize(config=config, audio=audio)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        text = text + result.alternatives[0].transcript + ' '
        # The first alternative is the most likely one for this portion.
        #print(u"Transcript: {}".format(result.alternatives[0].transcript))
    return text

print(transcribe_file('./audio/audio.wav'))


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
  

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
    
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def listen_print_loop(responses):

    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + "\r")
            sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            word = transcript + overwrite_chars
            talk = TTS()
            global seoul
            seoul = translate(word)

            print(seoul)
            talk.TextToSpeech(seoul)
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            if re.search(r"\b(종료|끄기)\b", transcript, re.I):
                print("Exiting..")

                break

            if re.search(r"\b(시작)\b", transcript, re.I):
                # ai 호출하면 반응
                print("말씀하세요")

            num_chars_printed = 0

def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = "ko-KR"  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


# 텍스트 입력하면 음성파일로 저장하는 함수 만들기
class TTS:

    def TextToSpeech(self, text) :

        client = texttospeech.TextToSpeechClient()

        # 합성할 text 지정
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # voice gender ("neutral")
        voice = texttospeech.VoiceSelectionParams(
            language_code="ko-KR",
            name = 'ko-KR-Wavenet-D',
            ssml_gender=texttospeech.SsmlVoiceGender.MALE
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # The response's audio_content is binary.
        filename = os.path.join(os.getcwd(), 'static', 'audio', 'output.mp3')
        with open(filename, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

        return "complete"




def translate(text) :
    # URL 지정
    url = 'http://svc.saltlux.ai:31781'

    # Header 정보 지정
    headers = {'Content-Type': 'application/json; charset=utf-8'}

    # Request Parameter 정보 지정
    params = {
        "key": "ffe069c1-6aa8-4652-bb43-a22ee1a8bc2c",
        "serviceId": "01400309787",
        "argument": {
            "text": text,
            "local": "gyeongsang"
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps((params)))

    data = response.content  # 이거 결과가 str로 나옴
    result = json.loads(data)  # input을 str로 받고 output을 dict로 줌

    return result['results']['translation']


# -----------------------------------------------------------------------------


@app.route('/audio2')
def audio2():
    if 'logFlag' in session:
        return render_template('audio2.html')
    else:
        return redirect(url_for('login'))

# 오디오 작성 가기
@app.route('/doaudio2', methods = ["GET", "POST"])
def doaudio2():
    start = request.form.get('start')

    if start == '시작':

        if __name__ == "__main__":
            print('시작합니다')

            main()

        #audio, sr = librosa.load('C:/test/output.wav')


    return render_template('audio2.html')



@app.route('/audio3')
def audio3():

    return render_template('audio3.html')

'''
# 오디오 작성 가기
@app.route('/doaudio3', methods = ["GET", "POST"])
def doaudio3():
    start = request.form.get('start')

    if start == '시작':

        transcribe_file(record.wav)


    return render_template('audio3.html')
'''

@app.route('/audio4')
def audio4():
    if 'logFlag' in session:
        return render_template('audio4.html')
    else:
        return redirect(url_for('login'))

# 오디오 작성 가기
@app.route('/doaudio4', methods = ["GET", "POST"])
def doaudio4():
    start = request.form.get('start')
    result = ''
    if start == '시작':

        text1 = transcribe_file('./audio/audio.wav')
        print('사투리는 : ', text1)
        trans = translate(text1)
        print('표준어는 : ', trans)
        talk = TTS()
        tts = talk.TextToSpeech(trans)

        if tts == 'complete' :
            return 'end'


@app.route('/audio5')
def audio5():
    if 'logFlag' in session:
        return render_template('audio5.html')
    else:
        return redirect(url_for('login'))

# 오디오 작성 가기
@app.route('/doaudio5', methods = ["GET", "POST"])
def doaudio5():
    start = request.form.get('start')
    result = ''
    if start == '시작':

        text1 = transcribe_file('./audio/audio.wav')
        print('사투리는 : ', text1)
        trans = translate(text1)
        print('표준어는 : ', trans)
        talk = TTS()
        talk.TextToSpeech(trans)

        result = '녹음한 사투리 : ' + text1 + '<br>' + '표준어 : '+trans
    return result




@app.route('/upload_audio', methods=['POST'])
def upload():
    fname = request.files['file']
    print(fname.filename)

    path = os.getcwd()
    path = os.path.join(path,'audio',fname.filename)
    with open(path, "wb") as f:  ## Excel File
        f.write(fname.getbuffer())

    #filename = secure_filename(file.filename)
    #print(filename)
    #path = os.getcwd()
    #file.save(os.path.join(path,'audio',filename))

    return "test"





'''
if __name__ == "__main__":
    main()
'''




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)


















