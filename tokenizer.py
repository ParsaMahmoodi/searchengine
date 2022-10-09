from __future__ import unicode_literals
from hazm import *
import time
import re


class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def start_tokenizer(_input_html):

    normalizer = Normalizer()

    print(BColors.OKCYAN + "Please wait...\nIndexing..." + BColors.ENDC)
    start_time = time.time()

    # getting input data an list the data
    input_text = _input_html.split("\n")

    #################
    # Normalizations:

    tokens = {}
    for i in range(len(input_text)):

        # 1.remove all numbers
        input_text[i] = re.sub(r'\d+', '', input_text[i])
        #
        # # 2.remove all punctuation except words and space
        # input_text[i] = re.sub(r'[^\w\s]', ' ', input_text[i])
        #
        # # 3.remove redundant spaces
        # # input_text[i] = re.sub(r'\s+', ' ', input_text[i])
        # input_text[i] = input_text[i].strip()
        #
        # # 4.remove english words
        # input_text[i] = re.sub(r'[a-zA-Z]+', '', input_text[i])

        # 4.5.normalize
        input_text[i] = normalizer.normalize(input_text[i])

        # 5.extract data and only Persian strings and save their count
        # dividing some inputs in input list that are multi string
        input_split = input_text[i].split(" ")

        # iterate data in each input string
        for split in input_split:
            # 6.save only Persian strings and numbers
            if re.findall(r'^[\u0600-\u06FF\s]+$', split):

                # 7.ignore stop words
                # if split in stop_words:
                #     continue

                if split in tokens.keys():
                    tokens[split] += 1
                else:
                    tokens[split] = 1

    # End of Normalization.
    #######################

    # sorting dictionary [NOT NECESSARY]
    # tokens = collections.OrderedDict(sorted(tokens.items()))

    finish_time = str(time.time() - start_time)
    print(BColors.OKGREEN + "Indexing finished.\nProcess Took " + finish_time + " seconds." + BColors.ENDC + "\n")

    # for item in tokens:
    #     print(item, tokens[item])
    return tokens
