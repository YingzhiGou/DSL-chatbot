from enum import Enum
from functools import partial
from time import sleep

from errbot import BotPlugin, botcmd, arg_botcmd

from DSLChatbot.Speech.speech_to_text import audio_from_microphone, audio_to_text_sphinx, audio_to_text_google_speech, \
    audio_to_text_google_cloud_speech, listen_in_background


class Speech2Text(BotPlugin):

    def activate(self):
        if self._bot.mode in ['text', 'graphic']:
            super().activate()
            self.__speech_engine = Speech2Text.SPEECH2TEXT_ENGINES.Sphinx  # default engine
            self.__speech_engine_kwargs = {}
            self.__stop_listening = None
            self.__speaking = False
        else:
            self.log.error("Speech2Text only supports text and graphic mode.")

    class SPEECH2TEXT_ENGINES(Enum):
        Sphinx = partial(audio_to_text_sphinx)
        GoogleSpeech = partial(audio_to_text_google_speech)
        GoogleCloudSpeech = partial(audio_to_text_google_cloud_speech)

        def __call__(self, *args, **kwargs):
            return self.value(*args, **kwargs)

    @botcmd
    def test_speech2text(self, msg, args):
        self.send(msg.frm, "Start listening on microphone ...", msg)
        audio = audio_from_microphone()
        self.send(msg.frm, "Processing audio ...", msg)
        text = self._audio_to_speech(audio)
        if text is not None:
            self.send(msg.frm, "You said: {}".format(text), msg)
        else:
            self.send(msg.frm, "Failed to recognize any words.", msg)

    @arg_botcmd('option', type=str, default=['current', 'Sphinx', 'GoogleSpeech', 'GoogleCloudSpeech'],
                help='set or display the current speech recognition engine.')
    def engine(self, msg, option):
        if option == 'current':
            reply = "Current Speech Recognition Engine: {}".format(self.__speech_engine.name)
        else:
            reply = "Switched Speech recognition Engine from \"{}\" to ".format(self.__speech_engine.name)
            self.__speech_engine = self.SPEECH2TEXT_ENGINES[option]
            reply += "\"{}\"".format(self.__speech_engine.name)
        return reply

    def _audio_to_speech(self, audio):
        return self.__speech_engine(audio, **self.__speech_engine_kwargs)

    @botcmd
    def start_listening(self, msg, args):
        if self.__stop_listening is not None:
            return "Already listening"
        chatterbot = self.get_plugin("ChatterBot")._chatterbot

        # this is called from the background thread
        def callback(recognizer, audio):
            self.log.info("Recognizing audio ...")
            # received audio data, now we'll recognize it
            text = self._audio_to_speech(audio)
            if text:
                print("[MIC]: {}".format(text))
                reply = chatterbot.reply(text, "MIC")
                print("[{}]: {}".format(chatterbot.my_name, reply))
                if self.__speaking:
                    raise NotImplemented  # todo speek!
            elif __debug__:
                print("[MIC]: ** Cannot recognize audio. **")
            self.log.info("Cannot recognize audio.")

        self.__stop_listening = listen_in_background(callback=callback)
        self.log.info("Listening in the background.")
        return "Start listening in background"

    @botcmd
    def stop_listening(self, msg, args):
        if self.__stop_listening is not None:
            yield "Stopping ..."
            self.__stop_listening(wait_for_stop=False)
            sleep(3)
            self.__stop_listening = None
            return "no longer listening."
        else:
            return "not listening"
