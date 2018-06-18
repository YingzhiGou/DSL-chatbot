from DSLChatbot.basic import BasicChatBot


class LearningChatBot(BasicChatBot):
    def __init__(self, name, language_filter):
        super(LearningChatBot, self).__init__(name, language_filter)
        self._deepqa_models = []

    def train(self, corpus):
        raise NotImplemented

    def save(self, file=None):
        raise NotImplemented

    def load(self, file=None):
        raise NotImplemented
