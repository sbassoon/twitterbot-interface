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


def tweetOSC(data_type, args):
    hash_me = str(data_type) + str(args)
    hashed_str = hashlib.md5(hash_me.encode()).hexdigest()
    reduced_hash = sortAndOrderHash(hashed_str)

    hash_int = int(reduced_hash[1])
    hash_integer_array = [(hash_int//(10**i))%10 for i in range((int(math.ceil(math.log(hash_int, 10))) - 1), -1, -1)]
    hash_list = (re.findall('\d+|\D+', reduced_hash[0]))

    print(hash_integer_array)
    print(hash_list)



    #tweet("null")


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
