import time

from errbot import BotPlugin, botcmd

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

        answer = DeepQA.bot.reply(msg.body, user)
        self.send(msg.frm,answer)