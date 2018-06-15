import os

from chatterbot import ChatBot

from DSLChatbot.learning.bot import LearningChatBot


class ChatterBot(LearningChatBot):
    def __init__(self, name="ChatterBot", storage=":memory:", language_filter=True, read_only=False):
        super(ChatterBot, self).__init__(name, language_filter)
        self._read_only = read_only
        if storage == ":memory:":
            # inmemory SQLite database
            self._database_path = storage
        else:
            self._database_path = os.path.join(storage, '{}.sqlite3'.format(self._my_name))
        self._model = None
        self._conversation_dict = {}
        self._init_chatter_bot()

    def _init_chatter_bot(self):
        self._model = ChatBot(
            self._my_name,
            trainer='chatterbot.trainers.ChatterBotCorpusTrainer',
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            database=self._database_path,
            # database=":memory:",
            logic_adapters=[
                {
                    "import_path": "chatterbot.logic.BestMatch",
                    # "statement_comparison_function": "chatterbot.comparisons.levenshtein_distance",
                    "response_selection_method": "chatterbot.response_selection.get_random_response"
                },
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
            read_only=self._read_only
        )
        self._model.initialize()
        self.clear_conversation()

    def _get_is_learning(self):
        return not self._read_only

    def _set_is_learning(self, is_learning):
        if self._read_only != is_learning:
            self._logger.info("learning is already {}.".format('enabled' if is_learning else 'disabled'))
        else:
            self._logger.info("{}ing learning...".format('enabl' if is_learning else 'disabl'))
            self._read_only = not is_learning
            self._init_chatter_bot()

    is_learning = property(_get_is_learning, _set_is_learning)

    def _corpora_training(self, corpora="chatterbot.corpus.english"):
        if isinstance(corpora, str):
            corpora = [corpora]

        for corpus in corpora:
            self._logger.info("Training on {}".format(corpus))
            # Train based on the corpus
            self._model.train(corpus)

    def train(self, *corpus):
        if self._read_only:
            self._logger.warning('Not training as learning is disabled! please enable learning before start training.')
        else:
            self._corpora_training(*corpus)

    def _get_answer(self, question, conversation_id=None):
        if conversation_id not in self._conversation_dict:
            self._conversation_dict[conversation_id] = self._model.storage.create_conversation()
        response = self._model.get_response(question, conversation_id=self._conversation_dict[conversation_id])
        return response.text

    def clear_conversation(self):
        self._logger.info("Cleaning all {} conversations".format(len(self._conversation_dict)))
        self._conversation_dict.clear()

    def clear_memory(self):
        """this will clear ererything the bot have learnt"""
        self._logger.info("Clearing all my memories, i will be reborn!")
        self._model.storage.drop()
        if os.path.isfile(self._database_path):
            self._logger.debug("removing database file: {}".format(self._database_path))
            os.remove(self._database_path)
        self._logger.debug("building new database {}".format(self._database_path))
        self._model.storage.create()


if __name__ == "__main__":

    # logging.basicConfig()
    # logging.getLogger().setLevel(logging.DEBUG)

    bot = ChatterBot("TEST")
    print('Testing: Launch interactive mode:')
    SENTENCES_PREFIX = ["Q. ", "A. "]
    while True:
        question = input(SENTENCES_PREFIX[0])
        if question == '' or question == 'exit':
            break
        elif question == "train":
            bot.train('chatterbot.corpus')
            continue
        print('{}{}'.format(SENTENCES_PREFIX[1], bot.reply(question, "admin")))
