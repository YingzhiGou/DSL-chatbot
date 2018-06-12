import logging


class BasicChatBot(object):
    def __init__(self, name="bot"):
        self._my_name = name
        self._logger = logging.getLogger(self.__class__.__name__)

    def __get_name(self):
        return self._my_name

    #my_name = property(__get_name)

    def reply(self, input):
        pass
