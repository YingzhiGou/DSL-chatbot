from errbot import BotPlugin, botcmd, arg_botcmd

from DSLChatbot.learning import ChatterBot as DSLChatterBot


class ChatterBot(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """
    autostarted = False

    def activate(self):
        """
        skip auto activate when errbot starts
        :return:
        """
        if not ChatterBot.autostarted:
            # don't start the first time activate called
            ChatterBot.autostarted = True
            self.log.info("Skip auto activate, this plugin has to be activated manually")
            self._deepqa_bot = None
        else:
            super(ChatterBot, self).activate()
            self._chatterbot = DSLChatterBot(storage=self.bot_config.BOT_DATA_DIR)

    @botcmd  # flags a command
    def test_chatterbot(self, msg, args):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return 'It *works* !'  # This string format is markdown.

    def callback_message(self, msg):
        if msg.body.startswith(self.bot_config.BOT_PREFIX):
            # telegram command, don't reply
            return

        user = msg.frm
        if self._bot.mode == 'telegram':
            user = "{}({})".format(msg.frm.nick, msg.frm.id)

        answer = self._chatterbot.reply(msg.body, user)
        self.send(msg.frm, answer)

    @botcmd
    def clear_conversation(self, msg, args):
        self._chatterbot.clear_conversation()

    @botcmd
    def clear_memory(self, msg, args):
        self._chatterbot.clear_memory()

    @arg_botcmd('corpus', type=str, nargs='*', default='chatterbot.corpus.english', help='list of corpus for training')
    def train(self, msg, corpus=None):
        self._chatterbot.train(corpus)

    @botcmd
    def start(self, msg, args):
        """send hello card"""
        self.send(msg.frm, """
        You are talking to a chatbot created for the Human Robot Friendship Ball 2018, made by the Decision Systems Lab (DSL), University of Wollongong, Australia.

        DSL: http://www.dsl.uow.edu.au
        ChatterBot: https://github.com/gunthercox/ChatterBot
        """)

        self.send(msg.frm, """
        Greetings Human,
        
        I am a machine-learning based conversational bot. Ask me anything, and I may not answer you correctly :)

        Happy Chatting!
        """)
