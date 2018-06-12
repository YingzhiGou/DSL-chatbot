import os
import sys

DSL_ROOT = os.path.dirname(os.path.abspath(__file__))
if "DEEPQA_PATH" in os.environ:
    DEEPQA_PATH = os.environ.get("DEEPQA_PATH")
else:
    DEEPQA_PATH = os.path.join(os.path.dirname(DSL_ROOT), "DeepQA")

if os.path.isdir(DEEPQA_PATH):
    sys.path.append(DEEPQA_PATH)