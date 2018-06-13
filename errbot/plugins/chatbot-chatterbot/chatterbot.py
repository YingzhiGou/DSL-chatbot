from errbot import BotPlugin, botcmd


class ChatterBot(BotPlugin):
    """
    This is a very basic plugin to try out your new installation and get you started.
    Feel free to tweak me to experiment with Errbot.
    You can find me in your init directory in the subdirectory plugins.
    """

    @botcmd  # flags a command
    def test_chatterbot(self, msg, args):  # a command callable with !tryme
        """
        Execute to check if Errbot responds to command.
        Feel free to tweak me to experiment with Errbot.
        You can find me in your init directory in the subdirectory plugins.
        """
        return 'It *works* !'  # This string format is markdown.

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
