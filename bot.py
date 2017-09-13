# Copyright (c) 2015–2016 Molly White
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import tweepy
import argparse
import hashlib
import math
import random
import re
from secrets import *
from time import gmtime, strftime
from pythonosc import dispatcher
from pythonosc import osc_server
from wordnik import swagger
from wordnik import WordApi
from wordnik import WordsApi
from wordfilter import wordfilter

# ====== Individual bot configuration ==========================
bot_username = 'sbotssoon'
logfile_name = bot_username + ".log"


# ==============================================================


def tweet(text):
    """Send out the text as a tweet."""
    # Twitter authentication
    auth = tweepy.OAuthHandler(C_KEY, C_SECRET)
    auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)
    api = tweepy.API(auth)

    # Send the tweet and log success or failure
    try:
        api.update_status(text)
    except tweepy.error.TweepError as e:
        log(e.message)
    else:
        log("Tweeted: " + text)


def log(message):
    """Log message to logfile."""
    path = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    with open(os.path.join(path, logfile_name), 'a+') as f:
        t = strftime("%d %b %Y %H:%M:%S", gmtime())
        f.write("\n" + t + " " + message)


def digital_root(n):
    x = sum(int(digit) for digit in str(n))
    if x < 10:
        return x
    else:
        return digital_root(x)


def orderHash(hash):
    ints_in_hash = ''
    letters_in_hash = ''
    slim_hash = ''
    split_hash = (re.findall('\d+|\D+', hash))
    for entries in split_hash:
        while True:
            try:
                int(entries)
                sum_hash_digits = digital_root(entries)
                ints_in_hash = ints_in_hash + str(sum_hash_digits)
                slim_hash = slim_hash + str(sum_hash_digits)
                break
            except ValueError:
                str(entries)
                letters_in_hash = letters_in_hash + entries
                slim_hash = slim_hash + entries
                break

    integers_in_hash = int(ints_in_hash)

    digits = 1
    hash_numerology = 0

    if integers_in_hash > 0:
        digits = int(math.log10(integers_in_hash)) + 1
    elif integers_in_hash == 0:
        digits = 1

    if digits > 1:
        hash_numerology = digital_root(ints_in_hash)
    elif digits == 1:
        hash_numerology = integers_in_hash

    new_ordered_hash = str(hash_numerology) + letters_in_hash
    return new_ordered_hash, ints_in_hash


def sortAndOrderHash(hash):
    sorted_hash = orderHash(hash)
    ints_in_hash = sorted_hash[1]
    resorted_hash_tuple = orderHash(''.join(set(sorted_hash[0])))
    resorted_hash = resorted_hash_tuple[0]
    return resorted_hash, ints_in_hash


def assignLetterFromNumber(number):
    letters = ['a','b','c','d','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    letter_assignment = letters[number]
    return letter_assignment

def wordChooser(hash_array, hash_list):
    wordnikAPIUrl = 'http://api.wordnik.com/v4'
    wordnikAPIKey = WORDNIK_KEY
    client = swagger.ApiClient(wordnikAPIKey, wordnikAPIUrl)

    letter_values = 0
    for character in hash_list[1]:
        if character == 'a':
            letter_values += 1
        elif character == 'b':
            letter_values += 2
        elif character == 'c':
            letter_values += 3
        elif character == 'd':
            letter_values += 4
        elif character == 'e':
            letter_values += 5
        elif character == 'f':
            letter_values += 6
    letter_values = letter_values * int(hash_list[0])
    letter_value_assignment = letter_values % 26

    hash_array_average = int(math.ceil(sum(hash_array) / len(hash_array)))

    min_word_length = hash_array_average - random.randint(0,math.ceil(hash_array_average / 1.5))
    chosen_letter = assignLetterFromNumber(letter_value_assignment)
    limit_words = random.randint(1, (len(hash_array) - 1))

    word_search = WordsApi.WordsApi(client)
    search_results = word_search.searchWords(query=chosen_letter, minLength=min_word_length, limit=limit_words)

    search_index = random.randint(0,(len(search_results.searchResults) - 1))
    chosen_word = search_results.searchResults[search_index].word

    if badWordHandler(chosen_word) is True:
        wordChooser(hash_array,hash_list)
    else:
        return chosen_word

def pronunciationChooser(word):
    wordnikAPIUrl = 'http://api.wordnik.com/v4'
    wordnikAPIKey = WORDNIK_KEY
    client = swagger.ApiClient(wordnikAPIKey, wordnikAPIUrl)

    word_book = WordApi.WordApi(client)
    word_pronunciation = word_book.getTextPronunciations(word)
    pronunciation_type = random.randint(0,9)

    if pronunciation_type >= 3:
        pronunciation_type = 0
    else:
        pronunciation_type = 1

    word_pronunciation = word_pronunciation[pronunciation_type].raw

    if pronunciation_type == 0:
        word_pronunciation = ''.join(char for char in word_pronunciation if char not in "() -ˈ")
        word_pronunciation = word_pronunciation.split(",")
        pronunciation_part = random.randint(0,len(word_pronunciation)-1)
        word_pronunciation = word_pronunciation[pronunciation_part]
    elif pronunciation_type == 1:
        word_pronunciation = ''.join(char for char in word_pronunciation if char not in "0123456789")
        word_pronunciation = word_pronunciation.lower()
        word_pronunciation = ''.join(char for char in word_pronunciation if char not in " ")

    if badWordHandler(word_pronunciation) is True:
        pronunciationChooser(word)
    else:
        return word_pronunciation

def definitionChooser(word):
    wordnikAPIUrl = 'http://api.wordnik.com/v4'
    wordnikAPIKey = WORDNIK_KEY
    client = swagger.ApiClient(wordnikAPIKey, wordnikAPIUrl)

    word_book = WordApi.WordApi(client)
    word_definition = word_book.getDefinitions(word, limit=len(word))

    definition_number = random.randint(0,len(word_definition) - 1)

    word_definition = word_definition[definition_number].text
    word_definition = word_definition.lower().split(':')

    definition_segment_number = random.randint(0,len(word_definition) - 1)
    word_definition = word_definition[definition_segment_number].strip()
    word_definition = word_definition.split(';')

    definition_subsegment_number = random.randint(0,len(word_definition) - 1)
    word_definition = word_definition[definition_subsegment_number].strip()

    word_definition = ''.join(char for char in word_definition if char not in "0123456789")
    word_definition = word_definition.replace('  ',' ')
    word_definition = word_definition.replace('  ',' ')
    word_definition = word_definition.strip()

    if badWordHandler(word_definition) is True:
        definitionChooser(word)
    else:
        return word_definition

def exampleChooser(word):
    wordnikAPIUrl = 'http://api.wordnik.com/v4'
    wordnikAPIKey = WORDNIK_KEY
    client = swagger.ApiClient(wordnikAPIKey, wordnikAPIUrl)

    word_book = WordApi.WordApi(client)
    word_example = word_book.getExamples(word, limit=len(word))

    example_number = random.randint(0,len(word_example.examples) - 1)
    word_example = word_example.examples[example_number].text.strip()

    word_example = word_example.split()
    word_example = word_example[-5:]
    word_example = ' '.join(word_example)
    word_example = word_example.replace('_','')
    word_example = word_example.replace('  ',' ')
    word_example = word_example.replace('  ',' ')
    word_example = word_example.strip()

    if badWordHandler(word_example) is True:
        exampleChooser(word)
    else:
        return word_example

def relatedWordsChooser(word):
    wordnikAPIUrl = 'http://api.wordnik.com/v4'
    wordnikAPIKey = WORDNIK_KEY
    client = swagger.ApiClient(wordnikAPIKey, wordnikAPIUrl)

    word_book = WordApi.WordApi(client)
    word_related = word_book.getRelatedWords(word)

    list_number = random.randint(0,len(word_related) - 1)
    word_related = word_related[list_number].words

    word_number = random.randint(0,len(word_related) - 1)
    word_related = word_related[word_number]

    if badWordHandler(word_related) is True:
        exampleChooser(word)
    else:
        return word_related

def badWordHandler(word):
    if wordfilter.blacklisted(word) == True:
        return True
    elif wordfilter.blacklisted(word) == False:
        return False

def tweetLengthFixer(string):
    the_tweet = string
    if len(the_tweet) > 140:
        the_tweet = the_tweet.split(' ')
        del(the_tweet[random.randint(0,len(the_tweet) - 1)])
        the_tweet = ' '.join(the_tweet)
        return tweetLengthFixer(the_tweet)
    else:
        return the_tweet


def createTweet(hash_integer_array,hash_list):


    word_count = 0
    a_count = 0
    b_count = 0
    c_count = 0
    d_count = 0
    e_count = 0
    f_count = 0
    word_seed = random.randint(0, 10)
    a_part = ''
    b_part = ''
    c_part = ''
    d_part = ''
    e_part = ''
    f_part = ''

    for character in hash_list[1]:
        word_count += 1
        if character == 'a':
            a_count = 1
        elif character == 'b':
            b_count = 1
        elif character == 'c':
            c_count = 1
        elif character == 'd':
            d_count = 1
        elif character == 'e':
            e_count = 1
        elif character == 'f':
            f_count = 1

    if a_count == 1:
        a_part = (wordChooser(hash_integer_array, hash_list)).strip()

    if (b_count == 1 and word_seed > 9):
        b_part = (pronunciationChooser(wordChooser(hash_integer_array, hash_list))).strip()
    elif (b_count == 1 and word_seed <= 9):
        b_part = (wordChooser(hash_integer_array, hash_list)).strip()

    if c_count == 1:
        c_part = (definitionChooser(wordChooser(hash_integer_array, hash_list))).strip()

    if d_count == 1:
        d_part = (exampleChooser(wordChooser(hash_integer_array, hash_list))).strip()

    if e_count == 1:
        e_part = (relatedWordsChooser(wordChooser(hash_integer_array, hash_list))).strip()

    if f_count == 1:
        f_part = (relatedWordsChooser(wordChooser(hash_integer_array, hash_list))).strip()

    the_phrase = [a_part, b_part, c_part, d_part, e_part, f_part]

    for entry in the_phrase:
        if entry == '':
            the_phrase.remove(entry)

    random.shuffle(the_phrase)

    the_phrase = ' '.join(the_phrase)
    the_phrase = the_phrase.strip()
    the_phrase = the_phrase.lower()
    the_phrase = the_phrase.replace('  ', ' ')

    the_phrase = tweetLengthFixer(the_phrase)

    return the_phrase

def tweetOSC(data_type, args):
    hash_me = str(data_type) + str(args)
    hashed_str = hashlib.md5(hash_me.encode()).hexdigest()
    reduced_hash = sortAndOrderHash(hashed_str)

    hash_int = int(reduced_hash[1])
    hash_integer_array = [(hash_int//(10**i))%10 for i in range((int(math.ceil(math.log(hash_int, 10))) - 1), -1, -1)]
    hash_list = (re.findall('\d+|\D+', reduced_hash[0]))

    bot_tweet = createTweet(hash_integer_array,hash_list)

    tweet(bot_tweet)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip",
                        default="127.0.0.1", help="The ip to listen on")
    parser.add_argument("--port",
                        type=int, default=5006, help="The port to listen on")
    args = parser.parse_args()

    dispatcher = dispatcher.Dispatcher()
    dispatcher.map("/pipeA", tweetOSC)
    dispatcher.map("/laneB", tweetOSC)
    dispatcher.map("/pikeC", tweetOSC)
    dispatcher.map("/roadD", tweetOSC)

    server = osc_server.ThreadingOSCUDPServer(
        (args.ip, args.port), dispatcher)
    print("Serving on {}".format(server.server_address))
    server.serve_forever()
