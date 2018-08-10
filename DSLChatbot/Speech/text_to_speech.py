import logging
from abc import ABCMeta, abstractmethod


class Text2Speech(object, metaclass=ABCMeta):
    _instance = None

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
        if Text2Speech._instance is not None:
            # terminate the old enstance so the new one can be create
            Text2Speech._instance.terminate()
        Text2Speech._instance = self

    @abstractmethod
    def speak(self, text):
        pass

    @abstractmethod
    def terminate(self):
        pass


class Text2Speech_gTTS(Text2Speech):
    def __init__(self):
        super(Text2Speech_gTTS, self).__init__()

        from gtts import gTTS
        self.tts = gTTS("Testing, testing")

        import tempfile
        self.__temp_mp3 = tempfile.mktemp()

        # select player
        try:
            import mpv
            self.player = mpv.MPV()
        except ImportError:
            try:
                import vlc
                self.player = vlc
            except ImportError:
                print("ERROR, python-mpv or python-vlc is required")

    def speak(self, text):
        self._logger.info("Text to speech using gTTS ...")
        self.tts.text = text
        self._logger.info("Saving audio to {}".format(self.__temp_mp3))
        self.tts.save(self.__temp_mp3)
        self._logger.info("playing audio from {}".format(self.__temp_mp3))
        self.player.play(self.__temp_mp3)
        self.player.wait_for_playback()

    def terminate(self):
        self.player.terminate()


class Text2Speech_eSpeak(Text2Speech):
    def __init__(self):
        super(Text2Speech_eSpeak, self).__init__()
        import subprocess
        self.espeak_process = subprocess.Popen(["espeak", "-m", "--stdin", "-ven+f1"], stdin=subprocess.PIPE)

    def speak(self, text: str):
        self.espeak_process.communicate(text.encode())
        # if not text.endswith('\n'):
        #     self.espeak_process.communicate("\n")

    def terminate(self):
        self.espeak_process.terminate()
        self.espeak_process = None


if __name__ == "__main__":
    tts = Text2Speech_gTTS()
    tts.speak("The quick brown fox jumps over the lazy dog.")
    tts.terminate()

    tts = Text2Speech_eSpeak()
    tts.speak("The quick brown fox jumps over the lazy dog.")
    tts.terminate()
