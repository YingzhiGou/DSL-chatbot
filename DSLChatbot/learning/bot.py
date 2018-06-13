from DSLChatbot.basic import BasicChatBot


class LearningChatBot(BasicChatBot):
    def __init__(self, name="bot"):
        super(LearningChatBot, self).__init__(name)
        self._deepqa_models = []

    def train(self, corpus):
        raise NotImplemented

    def save(self, file=None):
        raise NotImplemented

    def load(self, file=None):
        raise NotImplemented
