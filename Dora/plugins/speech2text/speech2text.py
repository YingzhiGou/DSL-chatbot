from enum import Enum
from functools import partial

from errbot import BotPlugin, botcmd, arg_botcmd

from DSLChatbot.Speech.speech_to_text import audio_from_microphone, audio_to_text_sphinx, audio_to_text_google_speech, \
    audio_to_text_google_cloud_speech


class Speech2Text(BotPlugin):
    class SPEECH2TEXT_ENGINES(Enum):
        Sphinx = partial(audio_to_text_sphinx)
        GoogleSpeech = partial(audio_to_text_google_speech)
        GoogleCloudSpeech = partial(audio_to_text_google_cloud_speech)

        def __call__(self, *args, **kwargs):
            return self.value(*args, **kwargs)

    __speech_engine = SPEECH2TEXT_ENGINES.Sphinx  # default engine
    __speech_engine_kwargs = {}

    @botcmd
    def test_speech2text(self, msg, args):
        self.send(msg.frm, "Start listening on microphone ...")
        audio = audio_from_microphone()
        self.send(msg.frm, "Processing audio ...")
        text = self._audio_to_speech(audio)
        if text is not None:
            self.send(msg.frm, "You said: {}".format(text))
        else:
            self.send(msg.frm, "Failed to recognize any words.")

    @arg_botcmd('option', type=str, default=['current', 'Sphinx', 'GoogleSpeech', 'GoogleCloudSpeech'],
                help='set or display the current speech recognition engine.')
    def engine(self, msg, option):
        if option == 'current':
            reply = "Current Speech Recognition Engine: {}".format(Speech2Text.__speech_engine.name)
        else:
            reply = "Switched Speech recognition Engine from \"{}\" to ".format(Speech2Text.__speech_engine.name)
            Speech2Text.__speech_engine = Speech2Text.SPEECH2TEXT_ENGINES[option]
            reply += "\"{}\"".format(Speech2Text.__speech_engine.name)
        return reply

    @staticmethod
    def _audio_to_speech(audio):
        return Speech2Text.__speech_engine(audio, **Speech2Text.__speech_engine_kwargs)
    