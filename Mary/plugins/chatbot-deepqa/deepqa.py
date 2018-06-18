import time

from errbot import BotPlugin, botcmd

from DSLChatbot.learning import DeepQABot


class DeepQA(BotPlugin):
    autostarted = False

    def activate(self):
        """
        skip auto activate when errbot starts
        :return:
        """
        super(DeepQA, self).activate()
        self._deepqa_bot = DeepQABot()

    def deactivate(self):
        """ clean bot memory"""
        if "_deepqa_bot" in self.__dict__ and self._deepqa_bot is not None:
            self._deepqa_bot._close()
        super(DeepQA, self).deactivate()

    @botcmd  # flags a command
    def test_deepqa(self, msg, args):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return 'It *works* !'  # This string format is markdown.

    @botcmd
    def test_longcompute(self, mess, args):
        if self._bot.mode == "slack":
            self._bot.add_reaction(mess, "hourglass")
        else:
            yield "Finding the answer..."

        time.sleep(10)

        yield "The answer is: 42"
        if self._bot.mode == "slack":
            self._bot.remove_reaction(mess, "hourglass")

    def callback_message(self, msg):
        if msg.body.startswith(self.bot_config.BOT_PREFIX):
            # telegram command, don't reply
            return

        user = msg.frm
        if self._bot.mode == 'telegram':
            user = "{}({})".format(msg.frm.nick, msg.frm.id)

        answer = self._deepqa_bot.reply(msg.body, user)
        self.send(msg.frm,answer)

    @botcmd
    def start(self, msg, args):
        """send hello card"""
        self.send(msg.frm, """
    ===
    You are talking to a chatbot created for the Human Robot Friendship Ball 2018, made by the Decision Systems Lab (DSL), University of Wollongong, Australia, using a deep artificial neural network (DeepQA) that is trained on movie dialogs.
    
    WARNING: Your conversation with this bot may be recorded for research purposes. 
    
    Happy Chatting!
    
    DSL: http://www.dsl.uow.edu.au
    DeepQA: https://github.com/Conchylicultor/DeepQA
    Cornell Movie Dialogs: http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html
       """)

        self.send(msg.frm, """
    Greetings Human,
    
    I learned language from movie dialogs. Ask me anything, and I may not answer you correctly :)
    """
                  )
