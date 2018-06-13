from DSLChatbot.basic import BasicChatBot


class LearningChatBot(BasicChatBot):
    def __init__(self, name="bot"):
        super(LearningChatBot, self).__init__(name)
        self._deepqa_models = []

    def train(self, copus):
        pass

    def save(self, file=None):
        pass

    def load(self, file=None):
        pass
