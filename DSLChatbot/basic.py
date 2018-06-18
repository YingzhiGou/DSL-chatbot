import logging

from DSLChatbot.utility.profanityfilter import ProfanitiesFilter


class BasicChatBot(object):
    def __init__(self, name, language_filter):
        self._my_name = name
        self._logger = logging.getLogger(self.__class__.__name__)

        if language_filter:
            self._logger.info("Profanities Filter Enabled")
            self._profanities_filter = ProfanitiesFilter()
        else:
            self._logger.info("Profanities Filter Disabled")
            self._profanities_filter = None

    def __get_name(self):
        return self._my_name

    def _get_answer(self, question, conversation_id=None):
        raise NotImplemented

    my_name = property(__get_name)

    def reply(self, input, frm=None):
        answer = self._get_answer(input, frm)
        if self._profanities_filter:
            answer = self._profanities_filter.clean(answer)
        self._logger.info("[{}] {}    [{}] {}".format(frm if frm is not None else "USER", input, self._my_name, answer))
        return answer
