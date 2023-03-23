import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

class SpeechRecognizer:
    def __init__(self):
        load_dotenv()
    
        speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))

        speech_config.speech_recognition_language="en-US"
        speech_config.set_service_property('punctuation', 'explicit', speechsdk.ServicePropertyChannel.UriQueryParameter)
        speech_config.set_property(property_id=speechsdk.PropertyId.Speech_SegmentationSilenceTimeoutMs, value="300")

        audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        self.recognizer = speech_recognizer
        self.all_events = []

    def recognize(self):

        # The event recognized signals that a final recognition result is received.
        self.recognizer.recognized.connect(lambda event: self.all_events.append([event.result.text, False]))

        self.recognizer.start_continuous_recognition_async()