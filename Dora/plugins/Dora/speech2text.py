import threading
from enum import Enum
from functools import partial

from errbot import BotPlugin, botcmd, arg_botcmd
from speech_recognition import WaitTimeoutError

from DSLChatbot.Speech.speech_to_text import audio_from_microphone, audio_to_text_sphinx, audio_to_text_google_speech, \
    audio_to_text_google_cloud_speech


class Speech2Text(BotPlugin):

    def activate(self):
        if self._bot.mode in ['text', 'graphic']:
            super().activate()
            self.__speech_engine = Speech2Text.SPEECH2TEXT_ENGINES.Sphinx  # default engine
            self.__speech_engine_kwargs = {}
            self.__listening_thread = None
            self.__speaking = False
            self.__listening = False
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
        if not self.__listening:
            self.__listening = True
            self.send(msg.frm, "Start listening on microphone ...", msg)
            self.__listening = False
            audio = audio_from_microphone()
            self.send(msg.frm, "Processing audio ...", msg)
            text = self._audio_to_speech(audio)
            if text is not None:
                self.send(msg.frm, "You said: {}".format(text), msg)
            else:
                self.send(msg.frm, "Failed to recognize any words.", msg)
        else:
            self.send(msg.frm, "already listening", msg)

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
        if self.__listening_thread is not None or self.__listening:
            return "Already listening"
        chatterbot = self.get_plugin("ChatterBot")._chatterbot

        # this is called from the background thread
        def threaded_listen():
            while self.__listening:
                self.log.info("Listening ...")
                try:
                    audio = audio_from_microphone()
                except WaitTimeoutError:  # listening timed out, just try again
                    pass
                else:
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

        self.log.info("Starting listening thread ...")
        self.__listening = True
        self.__listening_thread = threading.Thread(target=threaded_listen)
        self.__listening_thread.start()
        self.log.info("Listening in the background.")
        return "Start listening in background"

    @botcmd
    def stop_listening(self, msg, args):
        if self.__listening_thread is not None:
            yield "Stopping ..."
            self.__listening = False
            self.__listening_thread.join()
            self.__listening_thread = None
            return "no longer listening."
        else:
            return "not listening"
