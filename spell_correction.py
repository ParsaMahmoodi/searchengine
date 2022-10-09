import json
import Levenshtein


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


def spell_check(_word):

    word = _word

    # change this to change edit distance limit
    distance_range = 2

    # change this to change word lengths
    edit_distance_threshold = 2

    # change this to change output count
    result_count = 5

    # open and load tokens file
    # print(BColors.OKCYAN + "\nLoading data...\nPlease wait..." + BColors.ENDC)
    with open('spell_tokens.txt') as f:
        data = f.read()
    tokens = json.loads(data)
    # print(BColors.OKGREEN + "Data has been loaded successfully.\n" + BColors.ENDC)

    # end results initialization
    results = {}

    # if the word is correct it will use this flag variable to skip searching
    flag_correct = 0

    # search through each data tokens and get each user input's edit distance
    # and add results to the "results" dictionary
    # Edit Distance threshold = 2
    for item in tokens:

        # we suggest that there is only [DISTANCE_RANGE] letter difference
        if len(item) > len(word) + distance_range or len(item) < len(word) - distance_range:
            continue

        distance = Levenshtein.distance(word, item)

        if distance == 0:
            flag_correct = 1
            break

        # we only choose words with desired edit distance value [EDIT_DISTANCE_THRESHOLD]
        if distance <= edit_distance_threshold:
            results[item] = distance

    # if the word is not correct continue and sort the results
    if flag_correct == 0:

        # sorting results by edit distance
        sorted_result = {k: v for k, v in sorted(results.items(), key=lambda x: x[1])}
        sorted_result_2 = dict(reversed(list(sorted_result.items())))

        # sorting by most common words
        # first extracts words that have equal edit distance and add them to a dictionary by there repetition count
        # then sort that dictionary by the number of repetition and then add the words to a list
        temp_ed = 0
        temp_list = []
        temp_dict = {}
        final_list = []
        for item in sorted_result:
            # we take groups of answers by their edit distance so in here to this we
            # keep last word's edit distance to check if our new word is still has the same edit distance or changed
            if sorted_result[item] == temp_ed:
                temp_list.append(item)
            else:
                # update our new groups edit distance
                temp_ed = sorted_result[item]

                # add grouped item to a new list with their repetition count
                for res in temp_list:
                    temp_dict[res] = tokens[res]

                # create new group of words with same edit distance
                temp_list = [item]

                # sort our previous grouped item by their repetition count
                temp_dict_2 = {k: v for k, v in sorted(temp_dict.items(), key=lambda x: x[1])}
                temp_dict_2 = dict(reversed(list(temp_dict_2.items())))

                # clear previous list
                temp_dict = {}

                # append data to final results list
                for f in temp_dict_2:
                    final_list.append(f)

        # this method is repeated after the main one to make sure all the items have been added to final list of answers
        for res in temp_list:
            temp_dict[res] = tokens[res]
        temp_dict_2 = {k: v for k, v in sorted(temp_dict.items(), key=lambda x: x[1])}

        # append data to final results list
        for f in temp_dict_2:
            final_list.append(f)

        # Only 5 top results will be returned

        # print as a python list
        # print(final_list)
        # print(final_list[:result_count])
        return final_list[:result_count]

    # this part runs if the word was correct
    else:
        return 1
