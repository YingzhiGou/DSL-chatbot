import re

from errbot import BotPlugin, botcmd, re_botcmd

from DSLChatbot.learning.bots import DeepQABot




class DeepQA(BotPlugin):
    bot = DeepQABot()

    @botcmd  # flags a command
    def test_deepqa(self, msg, args):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return 'It *works* !'  # This string format is markdown.

    def callback_message(self, msg):
        self.send(msg.frm, DeepQA.bot.reply(msg.body))