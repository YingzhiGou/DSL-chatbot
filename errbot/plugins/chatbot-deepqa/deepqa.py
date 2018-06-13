import time

from errbot import BotPlugin, botcmd

from DSLChatbot.learning.bots import DeepQABot


class DeepQA(BotPlugin):
    autostarted = False

    def activate(self):
        """
        skip auto activate when errbot starts
        :return:
        """
        if not DeepQA.autostarted:
            # don't start the first time activate called
            DeepQA.autostarted = True
            self.log.info("Skip auto activate, this plugin has to be activated manually")
        else:
            super(DeepQA, self).activate()
            self._deepqa_bot = DeepQABot()

    def deactivate(self):
        """ clean bot memory"""
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
    def longcompute(self, mess, args):
        if self._bot.mode == "slack":
            self._bot.add_reaction(mess, "hourglass")
        else:
            yield "Finding the answer..."

        time.sleep(10)

        yield "The answer is: 42"
        if self._bot.mode == "slack":
            self._bot.remove_reaction(mess, "hourglass")

    def callback_message(self, msg):
        user = msg.frm
        if self._bot.mode == 'telegram':
            if msg.body.startswith('/'):
                # telegram command, don't reply
                return
            user = "{}({})".format(msg.frm.nick, msg.frm.id)

        answer = self._deepqa_bot.reply(msg.body, user)
        self.send(msg.frm,answer)

    @botcmd
    def start(self, msg, args):
        """send hello card"""
        self.send(msg.frm, """
    Greetings Human,
    
    You are talking to a chatbot created for the Human Robot Friendship Ball 2018, made by the Decision Systems Lab, University of Wollongong, Australia.
    
    Happy Chatting!
    
    Website: http://www.dsl.uow.edu.au
    """)
