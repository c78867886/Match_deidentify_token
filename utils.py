import json
import collections
import pickle
import sys
import numpy as np

def test_import():
    print("all functions in utils: load_data, save2json, load_json, token2dict, save_dict, load_dict")

def load_data(file):
    sents = []
    print("load data")
    with open(file, "r", encoding="utf-8") as f:
        sent = dict()
        tokens = []
        pos_tags = []
        bio_tags = []
        for each in f:
            info = each[:-1].split()
            if info:
                #information in the same sentence
                tokens.append(info[0])
                pos_tags.append(info[1])
                bio_tags.append(info[-1])
            else:
                #end of a sentence
                sent['tokens'] = tokens
                sent['pos'] = pos_tags
                sent['bio'] = bio_tags
                sents.append(sent)
                sent = dict()
                tokens = []
                pos_tags = []
                bio_tags = []

    return sents[:2]

def save2json(data, file):
    with open(file, "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_json(file):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def token2dict(tokens, max_tokens=30000, stop_words=[]):
    token_list = []
    for token in tokens:
        if token not in stop_words:
            token_list.append(token)
    counts = collections.Counter(token_list)
    unique_tokens = list(set(token_list))
    sorted_tokens = sorted(unique_tokens, key=lambda x: counts[x], reverse=True)
    token_dict = {k: v for v, k in enumerate(sorted_tokens)}
    inv_token_dict = {v: k for k, v in token_dict.items()}

    return token_dict, inv_token_dict

def save_dict(fname, dictionary):
    with open(fname, 'wb') as f:
        pickle.dump(dictionary, f)

def load_dict(fname):
    with open(fname, 'rb') as f:
        return pickle.load(f)

def load_embeddings(matrix, word):
    with open(matrix, "r", encoding='utf-8') as fm, open(word, "r", encoding='utf-8') as fw:
        embedding_table = dict()
        mt = np.array(np.array([each[:-1].split() for each in fm]), dtype=np.float32)
        wd = [each[:-1] for each in fw]
        for each in zip(mt, wd):
            embedding_table[each[1]] = each[0]
    return embedding_table

def get_embedding_table_shape(emb):
    rows= len(emb)
    i = -1
    for k, v in emb.items():
        if i == -1:
            i = len(v)
        else:
            if i != len(v):
                print("vectors are not the same length, check you embedding process!")
                sys.exit(1)
    return (rows, i)

def startOfChunk(prevTag, tag, prevType, type):
    chunkStart = False

    if prevTag == "B":
        if tag == "B":
            chunkStart = True
    elif prevTag == "I":
        if tag == "B":
            chunkStart = True
    else:
        if tag == "B" or tag == "I":
            chunkStart = True

    if tag != "O" and tag != "." and prevType != type:
        chunkStart = True

    return chunkStart

# endOfChunk: checks if a chunk ended between the preivous and current word
# arguments:  previous and current chunk tags, previous and current types
# note:       this code is not capable of handling other chunk representations
#             than the default CoNLL-2000 ones, see EACL'99 paper of Tjong
#             Kim Sang and Veenstra http://xxx.lanl.gov/abs/cs.CL/9907006
def endOfChunk(prevTag, tag, prevType, type):
    chunkEnd = False

    if prevTag == "B":
        if tag == "B" or tag == "O":
            chunkEnd = True
    elif prevTag == "I":
        if tag == "B" or tag == "O":
            chunkEnd = True

    if prevTag != "O" and prevTag != "." and prevType != type:
        chunkEnd = True

    return chunkEnd

'''
results is a list containing all the lines in testing file with predicated BIO tags
set delimiter to "\t" if dlmt == 1 else set delimiter to " "
set spliter to "-" if spl == 1 else set spliter to "_"
'''
def conlleval(results, dlmt, spl):
    boundary = "-X-"        # sentence boundary
    correct = ""            # current corpus chunk tag (T, O, B)
    correctChunk = 0        # number of correctly identified chunks
    correctTags = 0         # number of correct chunk tags
    correctType = ""        # type of current corpus chunk tag (NP, VP, etc.)
    if dlmt == 1:
        delimiter = "\t"
    else:
        delimiter = " "         # field delimiter
    f1_score = 0.0          # FB1 score
    firstItem = ""          # first feature (for sentence boundary checks)
    foundCorrect = 0        # number of chunks in corpus
    foundGuessed = 0        # number of identified chunks
    guessed = ""            # current guessed chunk tag
    guessedType = ""        # type of current guessed chunk tag
    inCorrect = False       # currently processed chunk is correct until now
    lastCorrect = "O"       # previous chunk tag in corpus
    lastCorrectType = ""    # type of previous chunk tag in corpus
    lastGuessed = "O"       # previously identified chunk tag
    lastGuessedType = ""    # type of previously identified chunk tag
    lastType = ""           # temporary storage for detecting duplicates
    nbrOfFeatures = -1      # number of features per line
    precision = 0.0         # precision score
    recall = 0.0            # recall score
    oTag = "O"              # outside tag, default O
    tokenCounter = 0        # token counter (ignores sentence breaks)
    if spl == 1:
        spliter = "-"
    else:
        spliter = "_"           # spliter used to connect preTag with subTag

    correctChunkByType = {} # number of correctly identified chunks per type
    foundCorrectByType = {} # number of chunks in corpus per type
    foundGuessedByType = {} # number of identified chunks per type

    for oline in results:
        line = oline.strip()
        if line == "":
            features = []
        else:
            features = line.split(delimiter)

        if nbrOfFeatures < 0:
            nbrOfFeatures = len(features)
        elif nbrOfFeatures != len(features) and len(features) != 0:
            sys.stderr.write("unexpected number of features: " + str(len(features)) + "(" + str(nbrOfFeatures) + ")\n")
            sys.exit(1)

        if len(features) == 0 or features[0] == boundary:
            features = [boundary, "O", "O"]

        if len(features) < 2:
            sys.stderr.write("conlleval: unexpected number of features in line: " + line + "\n")
            sys.exit(1)

        guessedLabel = features[-1]
        if spliter in guessedLabel:
            tokens = guessedLabel.split(spliter)
            guessed = tokens[0]
            guessedType = tokens[1]
        else:
            guessed = guessedLabel
            guessedType = ""
        features.pop()

        goldLabel = features[-1]
        if spliter in goldLabel:

            tokens = goldLabel.split(spliter)
            correct = tokens[0]
            correctType = tokens[1]
        else:
            correct = goldLabel
            correctType = ""
        features.pop()

        firstItem = features[0]
        features = features[1:]

        if firstItem == boundary:
            guessed = "O"

        if inCorrect:
            correctEndOfChunk = endOfChunk(lastCorrect, correct, lastCorrectType, correctType)
            guessedEndOfChunk = endOfChunk(lastGuessed, guessed, lastGuessedType, guessedType)

            if correctEndOfChunk and guessedEndOfChunk and lastGuessedType == lastCorrectType:
                inCorrect = False
                correctChunk += 1

                if lastCorrectType not in correctChunkByType:
                    correctChunkByType[lastCorrectType] = 0

                correctChunkByType[lastCorrectType] += 1
            elif correctEndOfChunk != guessedEndOfChunk or guessedType != correctType:
                inCorrect = False

        correctStartOfChunk = startOfChunk(lastCorrect, correct, lastCorrectType, correctType)
        guessedStartOfChunk = startOfChunk(lastGuessed, guessed, lastGuessedType, guessedType)

        if correctStartOfChunk and guessedStartOfChunk and guessedType == correctType:
            inCorrect = True

        if correctStartOfChunk:
            foundCorrect += 1
            if correctType not in foundCorrectByType:
                foundCorrectByType[correctType] = 0

            foundCorrectByType[correctType] += 1

        if guessedStartOfChunk:
            foundGuessed += 1

            if guessedType not in foundGuessedByType:
                foundGuessedByType[guessedType] = 0

            foundGuessedByType[guessedType] += 1

        if firstItem != boundary:
            if correct == guessed and guessedType == correctType:
                correctTags += 1
            tokenCounter += 1

        lastGuessed = guessed
        lastCorrect = correct
        lastGuessedType = guessedType
        lastCorrectType = correctType

    if inCorrect:
        correctChunk += 1

        if lastCorrectType not in correctChunkByType:
            correctChunkByType[lastCorrectType] = 0

        correctChunkByType[lastCorrectType] += 1

    # read in
    print ("processed " + str(tokenCounter) + " tokens with " + str(foundCorrect) + " phrases;")
    print ("found: " + str(foundGuessed) + " phrases; correct: " + str(correctChunk) + ".")

    if foundGuessed == 0:
        precision = 0.0
    else:
        precision = 100 * float(correctChunk) / foundGuessed

    if foundCorrect == 0:
        recall = 0.0
    else:
        recall = 100 * float(correctChunk) / foundCorrect

    if precision + recall == 0.0:
        f1_score = 0.0
    else:
        f1_score = 2 * precision * recall / (precision + recall)

    print ("accuracy: %6.2f%%; " % (100 * float(correctTags) / tokenCounter))
    print ("precision: %6.2f%%; " % precision)
    print ("recall: %6.2f%%; " % recall)
    print ("FB1: %6.2f" % f1_score)

    sortedTypes = [x for x in sorted(list(set(foundCorrectByType.keys()) & set(foundGuessedByType.keys())))]
    for type in sortedTypes:
        if type not in correctChunkByType:
            correctChunkByType[type] = 0

        if type not in foundGuessedByType:
            precision = 0.0
        else:
            precision = 100 * float(correctChunkByType[type]) / foundGuessedByType[type]

        if type not in foundCorrectByType:
            recall = 0.0
        else:
            recall = 100 * float(correctChunkByType[type]) / foundCorrectByType[type]

        if precision + recall == 0.0:
            f1_score = 0.0
        else:
            f1_score = 2 * precision * recall / (precision + recall)

        print ("%17s: " % type)
        print ("precision: %6.2f%%; " % precision)
        print ("recall: %6.2f%%; " % recall)
        print ("FB1: %6.2f %d" % (f1_score, foundGuessedByType[type]))

def main():
    results = []

    file = "for_conell_eval.txt"
    with open(file, "r") as f:
        for each in f:
            results.append(each[:-1])

    # 0: delimiter is  " "
    # 1: B-tag; I-tag

    conlleval(results, 0, 1)

if __name__ == '__main__':
    main()