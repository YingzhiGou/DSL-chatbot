import os
import sys

import tensorflow as tf
from tensorflow.python import debug as tf_debug

from DSLChatbot import DSL_ROOT, DEEPQA_PATH
from DSLChatbot.basic import BasicChatBot

from chatbot.chatbot import Chatbot
from chatbot.textdata import TextData
from chatbot.model import Model


class LearningChatBot(BasicChatBot):
    def __init__(self, name="bot"):
        super(LearningChatBot, self).__init__(name)

    def train(self, copus):
        pass


class DeepQABot(LearningChatBot):
    def __init__(self, name="DeepQA"):
        super(DeepQABot, self).__init__(name)
        self._load_model()

    def _get_answer(self, input):
        return self.chatbot.daemonPredict(input)

    def _close(self):
        """ A utility function to close the daemon when finish
        """
        self.chatbot.sess.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _load_model(self):
        # load cornell-tf1.3
        self.chatbot = Chatbot()
        self._init_deep_qa_bot(self.chatbot, "cornell-tf1.3", args=[
            "--modelTag", "cornell-tf1.3",
            "--keepAll",
            "--test", "daemon",
            "--rootDir", DEEPQA_PATH
        ])

    def _init_deep_qa_bot(self, chatbot, name=None, args=None):
        """
        Launch the training and/or the interactive mode
        almost the same as chatbot.main() except the removal of print and replaced with log
        """
        self._logger.info('[{}] Welcome to DeepQA v0.1 !'.format(name))
        self._logger.info('[{}] TensorFlow detected: v{}'.format(name, tf.__version__))

        # General initialisation

        chatbot.args = chatbot.parseArgs(args)

        if not chatbot.args.rootDir:
            chatbot.args.rootDir = os.getcwd()  # Use the current working directory

        # tf.logging.set_verbosity(tf.logging.INFO) # DEBUG, INFO, WARN (default), ERROR, or FATAL

        chatbot.loadModelParams()  # Update the chatbot.modelDir and chatbot.globStep, for now, not used when loading Model (but need to be called before _getSummaryName)

        chatbot.textData = TextData(chatbot.args)
        # TODO: Add a mode where we can force the input of the decoder // Try to visualize the predictions for
        # each word of the vocabulary / decoder input
        # TODO: For now, the model are trained for a specific dataset (because of the maxLength which define the
        # vocabulary). Add a compatibility mode which allow to launch a model trained on a different vocabulary (
        # remap the word2id/id2word variables).
        if chatbot.args.createDataset:
            self._logger.info('[{}] Dataset created! Thanks for using this program'.format(name))
            return  # No need to go further

        # Prepare the model
        with tf.device(chatbot.getDevice()):
            chatbot.model = Model(chatbot.args, chatbot.textData)

        # Saver/summaries
        chatbot.writer = tf.summary.FileWriter(chatbot._getSummaryName())
        chatbot.saver = tf.train.Saver(max_to_keep=200)

        # Running session
        chatbot.sess = tf.Session(config=tf.ConfigProto(
            allow_soft_placement=True,  # Allows backup device for non GPU-available operations (when forcing GPU)
            log_device_placement=False)  # Too verbose ?
        )

        if chatbot.args.debug:
            chatbot.sess = tf_debug.LocalCLIDebugWrapperSession(chatbot.sess)
            chatbot.sess.add_tensor_filter("has_inf_or_nan", tf_debug.has_inf_or_nan)

        self._logger.info('[{}] Initialize variables...'.format(name))
        chatbot.sess.run(tf.global_variables_initializer())

        # Reload the model eventually (if it exist.), on testing mode, the models are not loaded here (but in predictTestset)
        if chatbot.args.test != Chatbot.TestMode.ALL:
            chatbot.managePreviousModel(chatbot.sess)

        # Initialize embeddings with pre-trained word2vec vectors
        if chatbot.args.initEmbeddings:
            chatbot.loadEmbedding(chatbot.sess)

        if chatbot.args.test:
            if chatbot.args.test == Chatbot.TestMode.INTERACTIVE:
                chatbot.mainTestInteractive(chatbot.sess)
            elif chatbot.args.test == Chatbot.TestMode.ALL:
                self._logger.info('[{}] Start predicting...'.format(name))
                chatbot.predictTestset(chatbot.sess)
                self._logger.info('[{}] All predictions done'.format(name))
            elif chatbot.args.test == Chatbot.TestMode.DAEMON:
                self._logger.info('[{}] Daemon mode, running in background...'.format(name))
            else:
                raise RuntimeError('[{}] Unknown test mode: {}'.format(name, chatbot.args.test))  # Should never happen
        else:
            chatbot.mainTrain(chatbot.sess)

        if chatbot.args.test != Chatbot.TestMode.DAEMON:
            chatbot.sess.close()
            self._logger.info("[{}] The End! Thanks for using this program".format(name))

if __name__ == "__main__":
    bot = DeepQABot("TEST")
    print('Testing: Launch interactive mode:')
    SENTENCES_PREFIX = ["Q. ", "A. "]
    while True:
        question = input(SENTENCES_PREFIX[0])
        if question == '' or question == 'exit':
            break
        print('{}{}'.format(SENTENCES_PREFIX[1], bot.reply(question)))