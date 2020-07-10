import json
import os

import werkzeug
from flask import Flask
from flask_restful import Resource, Api, reqparse
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.websocket import RecognizeCallback, AudioSource

from lib.enum.Response import Response, Status
from lib.module.api import SpeechToText

app = Flask(__name__)
api = Api(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
UPLOAD_FOLDER = 'static/img'

authenticator = IAMAuthenticator('8mmRiDi4dO5LVaMKurWAwbU0q2IS4arE0BpEGowSwQk1')
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url(
    'https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/268b7b1c-7dbd-4929-9d09-5d6c0d755f2b'
)


class MyRecognizeCallback(RecognizeCallback):

    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        print(json.dumps(data, indent=2))

    def on_error(self, error):
        return format_msg(Status.SERVER_ERROR, error, Response.ERROR_SERVER)

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))


myRecognizeCallback = MyRecognizeCallback()


def format_msg(status: Status, msg: str, code: Response) -> object:
    return {
        'status': status,
        'message': msg,
        'code': code
    }


class HomeController(Resource):
    def get(self):
        return format_msg(Status.SUCCESS, 'seja bem vindo ao minha api', Response.SUCCESS_RESPONSE)


class SpeechResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('file', type=werkzeug.datastructures.FileStorage, location='files')
        args = parser.parse_args()
        if args['file'] == "":
            return format_msg(Status.SERVER_ERROR, '', Response.ERROR_SERVER)
        file = args['file']
        if file:
            filename = 'image.png'
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            audio_source = AudioSource(file)
            response = speech_to_text.recognize_using_websocket(
                audio=audio_source,
                content_type='audio/webm',
                model='pt-BR_BroadbandModel',
                interim_results=False,
                recognize_callback=myRecognizeCallback,
            )
            print(response)
            return format_msg(Status.SUCCESS, filename, Response.SUCCESS_RESPONSE)
        return format_msg(Status.SERVER_ERROR, 'File not found or file not save', Response.ERROR_SERVER)


api.add_resource(HomeController, '/')  # Route_1
api.add_resource(SpeechResource, '/api/speech/audio')

if __name__ == '__main__':
    app.run(port=5002, debug=True)
