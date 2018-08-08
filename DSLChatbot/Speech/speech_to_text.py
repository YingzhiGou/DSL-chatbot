import logging
import os

import speech_recognition as sr

# get keys
with open(os.path.join(os.path.dirname(__file__), 'api_key_google_cloud_speech.json')) as key_file:
    GOOGLE_CLOUD_SPEECH_KEY = key_file.read()

_logger = logging.getLogger(__name__)
_recognizer = sr.Recognizer()


def audio_from_microphone(recognizer=_recognizer, timeout=5, phrase_time_limit=15, adjust_for_ambient_noise=True):
    with sr.Microphone() as source:
        _logger.info("Listening on microphone")
        if adjust_for_ambient_noise:
            # listen for 1 second to calibrate the energy threshold for ambient noise levels
            recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
    return audio


def listen_in_background(recognizer=_recognizer, phrase_time_limit=15, adjust_for_ambient_noise=True, callback=None):
    _logger.info("Starting background listening")
    mic = sr.Microphone()
    if adjust_for_ambient_noise:
        _logger.info("Adjusting for ambient noise ...")
        with mic as source:
            recognizer.adjust_for_ambient_noise(source, duration=3)
    return recognizer.listen_in_background(mic,
                                           callback if callback is not None else audio_to_text_google_speech,
                                           phrase_time_limit=phrase_time_limit)


def audio_to_text_sphinx(audio, recognizer=_recognizer, language="en-US", keyword_entries=None, show_all=False):
    # recognize speech using Sphinx
    text = None
    try:
        text = recognizer.recognize_sphinx(audio, language=language, keyword_entries=keyword_entries,
                                           show_all=show_all)
        _logger.info("Sphinx thinks you said: {}".format(text))
    except sr.UnknownValueError:
        _logger.warning("Sphinx could not understand audio")
    except sr.RequestError as e:
        _logger.warning("Sphinx error; {0}".format(e))
    return text


def audio_to_text_google_speech(audio, recognizer=_recognizer, key=None, language="en-US", show_all=False):
    text = None
    try:
        # for testing purposes, we're just using the default API key
        text = recognizer.recognize_google(audio, key=key, language=language, show_all=show_all)
        _logger.info("Google Speech Recognition thinks you said: {}".format(text))
    except sr.UnknownValueError:
        _logger.warning("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        _logger.warning("Could not request results from Google Speech Recognition service; {0}".format(e))
    return text


def audio_to_text_google_cloud_speech(audio, recognizer=_recognizer, language="en-US", preferred_phrases=None,
                                      show_all=False):
    text = None
    try:
        text = recognizer.recognize_google_cloud(audio,
                                                 credentials_json=GOOGLE_CLOUD_SPEECH_KEY,
                                                 language=language,
                                                 preferred_phrases=preferred_phrases,
                                                 show_all=show_all)
        _logger.info("Google Cloud Speech thinks you said: {}".format(text))
    except sr.UnknownValueError:
        _logger.warning("Google Cloud Speech could not understand audio")
    except sr.RequestError as e:
        _logger.warning("Could not request results from Google Cloud Speech service; {0}".format(e))
    return text
