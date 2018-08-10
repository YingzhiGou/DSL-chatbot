import threading
from enum import Enum
from functools import partial

from errbot import BotPlugin, botcmd, arg_botcmd
from speech_recognition import WaitTimeoutError

from DSLChatbot.Speech.speech_to_text import audio_from_microphone, audio_to_text_sphinx, audio_to_text_google_speech, \
    audio_to_text_google_cloud_speech
from DSLChatbot.Speech.text_to_speech import Text2Speech_eSpeak, Text2Speech_gTTS


class Speech2Text(BotPlugin):
    def activate(self):
        if self._bot.mode in ['text', 'graphic']:
            super().activate()
            self.__speech_engine = Speech2Text.SPEECH2TEXT_ENGINES.Sphinx  # default engine
            self.__speech_engine_kwargs = {}
            self.__text_engine = Speech2Text.TEXT2SPEECH_ENGINES.eSpeak
            self.__text_engine_instance = self.__text_engine()
            self.__listening_thread = None
            self.__speaking = True
            self.__listening = False
        else:
            self.log.error("Speech2Text only supports text and graphic mode.")

    def deactivate(self):
        self.stop_listening(None, None)
        self.__text_engine_instance.terminate()
        super().deactivate()

    class SPEECH2TEXT_ENGINES(Enum):
        Sphinx = partial(audio_to_text_sphinx)
        GoogleSpeech = partial(audio_to_text_google_speech)
        GoogleCloudSpeech = partial(audio_to_text_google_cloud_speech)

        def __call__(self, *args, **kwargs):
            return self.value(*args, **kwargs)

    class TEXT2SPEECH_ENGINES(Enum):
        eSpeak = Text2Speech_eSpeak
        gTTS = Text2Speech_gTTS

        def __call__(self, *args, **kwargs):
            return self.value()

    @botcmd(admin_only=True)
    def test_stt(self, msg, args):
        """
        test STT using selected STT engine
        :param msg:
        :param args:
        :return:
        """
        if not self.__listening:
            self.__listening = True
            self.send(msg.frm, "Start listening on microphone ...", msg)
            audio = audio_from_microphone()
            self.__listening = False
            self.send(msg.frm, "Processing audio ...", msg)
            text = self._audio_to_speech(audio)
            if text is not None:
                self.send(msg.frm, "You said: {}".format(text), msg)
            else:
                self.send(msg.frm, "Failed to recognize any words.", msg)
        else:
            self.send(msg.frm, "already listening", msg)

    @arg_botcmd('option', admin_only=True, type=str, default=['current', 'Sphinx', 'GoogleSpeech', 'GoogleCloudSpeech'],
                help='set or display the current speech recognition engine.')
    def set_stt(self, msg, option):
        """
        set or display the current speech recognition engine.
        :param msg:
        :param option:
        :return:
        """
        if option == 'current':
            reply = "Current Speech Recognition Engine: {}".format(self.__speech_engine.name)
        else:
            reply = self._set_stt(option)
        return reply

    def _set_stt(self, option):
        reply = "Switched Speech recognition Engine from \"{}\" to ".format(self.__speech_engine.name)
        self.__speech_engine = self.SPEECH2TEXT_ENGINES[option]
        reply += "\"{}\"".format(self.__speech_engine.name)
        return reply

    @arg_botcmd('option', admin_only=True, type=str, default=['current', 'eSpeak', 'gTTS'],
                help="set or display the current text-to-speech engine")
    def set_tts(self, msg, option):
        """
        set or display the current text-to-speech engine
        :param msg:
        :param option:
        :return:
        """
        if option == 'current':
            reply = "Current Text-to-Speech Engine: {}".format(self.__text_engine.name)
        else:
            reply = self._set_tts(option)
        return reply

    def _set_tts(self, option):
        reply = "Switched Text-to-Speech Engine from \"{}\" to ".format(self.__text_engine.name)
        self.__text_engine = self.TEXT2SPEECH_ENGINES[option]
        self.__text_engine_instance = self.__text_engine()
        reply += "\"{}\"".format(self.__text_engine.name)
        return reply

    def _audio_to_speech(self, audio):
        return self.__speech_engine(audio, **self.__speech_engine_kwargs)

    @botcmd(admin_only=True)
    def set_online(self, msg, args):
        """
        use only engines for STT and TTS
        :return:
        """
        replys = []
        replys.append(self._set_stt('GoogleCloudSpeech'))
        replys.append(self._set_tts('gTTS'))
        return "\n".join(replys)

    @botcmd(admin_only=True)
    def set_offline(self, msg, args):
        """
        use preferred online STT and TTS engines
        :return:
        """
        replys = []
        replys.append(self._set_stt('Sphinx'))
        replys.append(self._set_tts('eSpeak'))
        return "\n".join(replys)

    @botcmd(admin_only=True)
    def start_listening(self, msg, args):
        if self.__listening_thread is not None or self.__listening:
            return "Already listening"
        chatterbot = self.get_plugin("ChatterBot")._chatterbot

        # this is called from the background thread
        def threaded_listen():
            while self.__listening:
                self.log.info("Listening ...")
                self.send(msg.frm, "**[listening...]**")
                try:
                    audio = audio_from_microphone()
                except WaitTimeoutError:  # listening timed out, just try again
                    pass
                else:
                    self.log.info("Recognizing audio ...")
                    # received audio data, now we'll recognize it
                    text = self._audio_to_speech(audio)
                    if text:
                        self.send(msg.frm, "[MIC]: {}".format(text))
                        reply = chatterbot.reply(text, "MIC")
                        self.send(msg.frm, "[{}]: {}".format(chatterbot.my_name, reply))
                        if self.__speaking:
                            self.__text_engine_instance.speak(reply)
                    elif __debug__:
                        self.send(msg.frm, "[MIC]: ~~Cannot recognize audio~~")
                    self.log.info("Cannot recognize audio.")

        self.log.info("Starting listening thread ...")
        self.__listening = True
        self.__listening_thread = threading.Thread(target=threaded_listen)
        self.__listening_thread.start()
        self.log.info("Listening in the background.")
        # return "Start listening in background"

    @botcmd(admin_only=True)
    def stop_listening(self, msg, args):
        if self.__listening_thread is not None:
            yield "Stopping ..."
            self.__listening = False
            self.__listening_thread.join()
            self.__listening_thread = None
            return "no longer listening."
        else:
            return "not listening"
