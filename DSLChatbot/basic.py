import logging


class BasicChatBot(object):
    def __init__(self, name="bot"):
        self._my_name = name
        self._logger = logging.getLogger(self.__class__.__name__)

    def __get_name(self):
        return self._my_name

    def _get_answer(self, question):
        return None

    my_name = property(__get_name)

    def reply(self, input, frm=None):
        answer = self._get_answer(input)
        self._logger.info("[{}] {}    [{}] {}".format(frm if frm is not None else "USER", input, self._my_name, answer))
        return answer
