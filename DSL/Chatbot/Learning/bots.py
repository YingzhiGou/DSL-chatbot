from DSL.Chatbot.basic import BasicChatBot


class LearningChatBot(BasicChatBot):
    def __init__(self, name="bot"):
        super(LearningChatBot, self).__init__(name)

    def train(self, copus):
        pass


class DeepQABot(LearningChatBot):
    def __init__(self, name="DeepQA"):
        super(DeepQABot, self).__init__(name)
