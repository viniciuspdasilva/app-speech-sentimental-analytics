from ibm_cloud_sdk_core import ApiException
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import AudioSource

from lib.enum.Response import Response


def format_msg(status, msg, code) -> object:
    return {
        'status': status,
        'message': msg,
        'code': code
    }


class SpeechToText:
    def __init__(self):
        self.authenticator = IAMAuthenticator('8mmRiDi4dO5LVaMKurWAwbU0q2IS4arE0BpEGowSwQk1')
        self.speech_to_text = SpeechToTextV1(authenticator=self.authenticator)
        self.speech_to_text.set_service_url(
            'https://api.us-south.speech-to-text.watson.cloud.ibm.com/instances/6bbda3b3-d572-45e1-8c54-22d6ed9e52c2'
        )
        self.speech_to_text.set_disable_ssl_verification(True)

    def recognize(self, archive_audio):
        try:
            return self.speech_to_text.recognize_using_websocket(
                audio=AudioSource(archive_audio, True, True),
                content_type='audio/webm',
                model='pt-BR_BroadbandModel',
                interim_results=False
            )
        except ApiException as ex:
            return format_msg(
                Response.ERROR_SERVER,
                ex.message,
                ex.code
            )
