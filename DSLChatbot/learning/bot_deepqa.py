import os
import random

import tensorflow as tf
from tensorflow.python import debug as tf_debug

from DSLChatbot import DEEPQA_PATH
from DSLChatbot.learning.bot import LearningChatBot
from chatbot.chatbot import Chatbot
from chatbot.model import Model
from chatbot.textdata import TextData


class DeepQABot(LearningChatBot):
    def __init__(self, name="DeepQA", language_filter=True):
        super(DeepQABot, self).__init__(name, language_filter=language_filter)
        self._max_length = 100  # max length
        self._load_model()

    def _get_answer(self, input, conversation_id=None):
        answers = []
        for models in self._deepqa_models:
            answer = models.daemonPredict(input)
            if not answer:
                self._logger.debug("model {} did not produce answer for \"{}\"".format(models.args.modelTag, input))
                continue
            self._logger.debug("model {} says \"{}\" TO \"{}\"".format(models.args.modelTag, answer, input))
            answers.append(answer)
        if answers is None:
            return None
        return random.choice(answers)

    def _close(self):
        """ A utility function to close the daemon when finish
        """
        self._logger.info("Closing Tensorflow sessions")
        for model in self._deepqa_models:
            self._logger.debug("closing model {}".format(model.args.modelTag))
            model.sess.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close()

    def _load_model(self):
        model_path = os.path.join(DEEPQA_PATH, 'save')
        saved_models = os.listdir(model_path)
        saved_models = [saved_model.replace("model-", "") for saved_model in saved_models if
                        not saved_model.startswith(".") and os.path.isdir(os.path.join(model_path, saved_model))]

        self._logger.info('TensorFlow detected: v{}'.format(tf.__version__))

        for saved_model in saved_models:
            self._logger.info("loading model {}".format(saved_model))
            model = Chatbot()
            try:
                self._init_deep_qa_bot(model, args=[
                    "--modelTag", saved_model,
                    "--keepAll",
                    "--test", "daemon",
                    "--rootDir", DEEPQA_PATH
                ])
                self._deepqa_models.append(model)
                if self._max_length > model.args.maxLength:
                    self._max_length = model.args.maxLength
            except Exception as e:
                self._logger.warning("failed to load model {}".format(saved_model))
                self._logger.error(e)

        self._logger.info("loaded model {}".format([model.args.modelTag for model in self._deepqa_models]))

    def _init_deep_qa_bot(self, chatbot, args=None):
        """
        Launch the training and/or the interactive mode
        almost the same as chatbot.main() except the removal of print and replaced with log
        """
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
            self._logger.info('[{}] Dataset created! Thanks for using this program'.format(chatbot.args.modelTag))
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

        self._logger.info('[{}] Initialize variables...'.format(chatbot.args.modelTag))
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
                self._logger.info('[{}] Start predicting...'.format(chatbot.args.modelTag))
                chatbot.predictTestset(chatbot.sess)
                self._logger.info('[{}] All predictions done'.format(chatbot.args.modelTag))
            elif chatbot.args.test == Chatbot.TestMode.DAEMON:
                self._logger.info('[{}] Daemon mode, running in background...'.format(chatbot.args.modelTag))
            else:
                raise RuntimeError('[{}] Unknown test mode: {}'.format(chatbot.args.modelTag,
                                                                       chatbot.args.test))  # Should never happen
        else:
            chatbot.mainTrain(chatbot.sess)

        if chatbot.args.test != Chatbot.TestMode.DAEMON:
            chatbot.sess.close()
            self._logger.info("[{}] The End! Thanks for using this program".format(chatbot.args.modelTag))


if __name__ == "__main__":
    import logging

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    bot = DeepQABot("TEST")
    print('Testing: Launch interactive mode:')
    SENTENCES_PREFIX = ["Q. ", "A. "]
    while True:
        question = input(SENTENCES_PREFIX[0])
        if question == '' or question == 'exit':
            break
        print('{}{}'.format(SENTENCES_PREFIX[1], bot.reply(question)))
