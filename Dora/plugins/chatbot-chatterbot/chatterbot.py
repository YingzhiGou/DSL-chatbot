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
        super(ChatterBot, self).activate()
        self._chatterbot = DSLChatterBot(storage=self.bot_config.BOT_DATA_DIR, name='Dora', read_only=True)

    @botcmd  # flags a command
    def test_chatterbot(self, msg, args):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return 'It *works* !'  # This string format is markdown.

    @staticmethod
    def _get_status(boo):
        return 'enabled' if boo else 'disabled'

    @arg_botcmd('option', type=str, default=['enable', 'disable'], help='enable or disable learning')
    def learning(self, msg, option):
        reply = '[{}] Learning: {} => '.format(self._chatterbot.my_name, self._get_status(self._chatterbot.is_learning))
        self._chatterbot.is_learning = True if option == 'enable' else False
        reply += self._get_status(self._chatterbot.is_learning)
        return reply

    def callback_message(self, msg):
        if msg.body.startswith(self.bot_config.BOT_PREFIX):
            # telegram command, don't reply
            return

        user = msg.frm
        if self._bot.mode == 'telegram':
            user = "{}({})".format(msg.frm.nick, msg.frm.id)

        answer = self._chatterbot.reply(msg.body, user)
        self.send(msg.frm, answer)

    @arg_botcmd('args', type=str, nargs='*', default=['conversation', 'memory', 'all'])
    def clear(self, msg, args):
        if isinstance(args, str):
            args = [args]
        args = set(args)
        if 'all' in args:
            args.update(['conversation', 'memory'])
        if 'conversation' in args:
            self._chatterbot.clear_conversation()
            yield "[{}] cleared conversation records".format(self._chatterbot.my_name)
        if 'memory' in args:
            self._chatterbot.clear_memory()
            yield "[{}] cleared all memory".format(self._chatterbot.my_name)

    @arg_botcmd('corpus', type=str, nargs='*', default='chatterbot.corpus.english', help='list of corpus for training')
    def learn(self, msg, corpus=None):
        if self._chatterbot.is_learning:
            yield "[{}] learning ...".format(self._chatterbot.my_name)
            self._chatterbot.train(corpus)
            yield "[{}] Learning complete.".format(self._chatterbot.my_name)
        else:
            return "[{}] Learning is disabled, please enable learning.".format(self._chatterbot.my_name)

    @botcmd
    def start(self, msg, args):
        """send hello card"""
        self.send(msg.frm, """
        ===
        You are talking to a chatbot created for the Human Robot Friendship Ball 2018, made by the Decision Systems Lab (DSL), University of Wollongong, Australia.
        
        WARNING: Your conversation with this bot may be recorded for research purposes. 
        
        DSL: http://www.dsl.uow.edu.au
        ChatterBot: https://github.com/gunthercox/ChatterBot
        """)

        self.send(msg.frm, """
        Greetings Human,
        
        I am a machine-learning based conversational bot. Ask me anything, and I may not answer you correctly :)
        I can learn to talk from our conversation, please teach me :P
        
        (Admin: learning is currently *{}*)
        """.format(self._get_status(self._chatterbot.is_learning)))
