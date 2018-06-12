import re

from errbot import BotPlugin, botcmd, re_botcmd

from DSLChatbot.learning.bots import DeepQABot

bot = DeepQABot()


class DeepQA(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """

    @botcmd  # flags a command
    def test_deepqa(self, msg, args):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return 'It *works* !'  # This string format is markdown.

    @re_botcmd(pattern=r".*", prefixed=False, flags=re.IGNORECASE)
    def listen_to_talk(self, msg, match):
        return bot.reply(msg.body)
