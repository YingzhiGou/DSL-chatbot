import os

from chatterbot import ChatBot

from DSLChatbot import DSL_ROOT
from learning.bot import LearningChatBot


class ChatterBot(LearningChatBot):
    def __init__(self, name="ChatterBot"):
        super(ChatterBot, self).__init__(name)
        self._model = ChatBot(
            name,
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database=os.path.join(DSL_ROOT, 'database.sqlite3'),
            logic_adapters=[
                "chatterbot.logic.BestMatch",
                'chatterbot.logic.MathematicalEvaluation',
                # {
                #     'import_path': 'chatterbot.logic.TimeLogicAdapter',
                #     'positive': [
                #         'what time is it',
                #         'hey what time is it',
                #         'do you have the time',
                #         'do you know the time',
                #         'do you know what time it is',
                #         'what is the time'
                #     ],
                #     'negiative': [
                #         'it is time to go to sleep',
                #         'what is your favorite color',
                #         'i had a great time',
                #         'thyme is my favorite herb',
                #         'do you have time to look at my essay',
                #         'how do you have the time to do all this'
                #         'what is it',
                #         'how are you'
                #     ]
                #
                # },
                {
                    'import_path': 'chatterbot.logic.LowConfidenceAdapter',
                    'threshold': 0.65,
                    'default_response': 'I am sorry, but I do not understand.'
                }
            ],
        )
        self._model.initialize()
        self._conversation_dict = {}

    def _corpora_training(self, corpora="chatterbot.corpus.english"):
        if isinstance(corpora, str):
            corpora = [corpora]

        for corpus in corpora:
            self._logger.info("Training on {}".format(corpus))
            # Train based on the corpus
            self._model.train(corpus)

    def train(self, corpus):
        self._corpora_training(corpus)

    def _get_answer(self, question, conversation_id=None):
        if conversation_id not in self._conversation_dict:
            self._conversation_dict[conversation_id] = self._model.storage.create_conversation()
        response = self._model.get_response(question, conversation_id=self._conversation_dict[conversation_id])
        return response.text


if __name__ == "__main__":
    import logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    bot = ChatterBot("TEST")
    print('Testing: Launch interactive mode:')
    SENTENCES_PREFIX = ["Q. ", "A. "]
    while True:
        question = input(SENTENCES_PREFIX[0])
        if question == '' or question == 'exit':
            break
        elif question == "train":
            bot.train('chatterbot.corpus.english')
            continue
        print('{}{}'.format(SENTENCES_PREFIX[1], bot.reply(question, "admin")))
