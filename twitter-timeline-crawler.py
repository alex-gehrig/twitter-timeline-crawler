#!/usr/bin/python
# -*- coding: UTF-8 -*-

import time
import sys
import tweepy
import sqlite3
import wget


###############
# definitions #
###############

def infos_for_user(startzeit):
    """Prints informations for the user"""
    print()
    print("Start der Sicherung:", startzeit)
    logfile.write("Start der Sicherung: {}\n\n".format(startzeit))


def get_media(status):
    """getting the pictures, videos and gifs"""
    if "extended_entities" in status._json:
        if "media" in status._json["extended_entities"]:
            cur.execute('SELECT id FROM tweets WHERE tweet_id = ?', (status.id, ))
            tweets_id = cur.fetchone()[0]
            data = status._json["extended_entities"]["media"]
            for item in data:
                mediatype = item["type"]
                if mediatype == "video":
                    # find out, which file has the highest resolution
                    variantcount = 0
                    highest = 0
                    for variant in item["video_info"]["variants"]:
                        if "bitrate" in variant:
                            if variant["bitrate"] > highest:
                                highest = variant["bitrate"]
                                image_url = item["video_info"]["variants"][variantcount]["url"]
                                contenttype = item["video_info"]["variants"][variantcount]["content_type"]
                            else:
                                pass
                        else:
                            pass
                        variantcount += 1
                    height = item["sizes"]["large"]["h"]
                    width = item["sizes"]["large"]["w"]
                elif mediatype == "animated_gif":
                    image_url = item["video_info"]["variants"][0]["url"]
                    contenttype = item["video_info"]["variants"][0]["content_type"]
                    height = item["sizes"]["large"]["h"]
                    width = item["sizes"]["large"]["w"]
                else:
                    image_url = item["media_url_https"]
                    contenttype = "0"
                    height = item["sizes"]["small"]["h"]
                    width = item["sizes"]["small"]["w"]
                # download the attached files to the actual directory
                wget.download(image_url)
                # retrieve filename out of URL
                name_of_file = image_url.split("/")[-1]
                print()
                print("Dateiname:", name_of_file)
                logfile.write("Dateiname: {}\n".format(name_of_file))
                print("Medien (Typ: " + str(mediatype) + "): " + str(image_url))
                logfile.write("Medien (Typ: {}): {}\n".format(mediatype, image_url))
                # write data concerning media to the db
                cur.execute('''INSERT INTO media (tweets_id, mediatype, image, height, width, name_of_file, contenttype)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''', (tweets_id, mediatype, image_url, height, width, name_of_file, contenttype))
    elif "media" in status.entities:
        cur.execute('SELECT id FROM tweets WHERE tweet_id = ?', (status.id, ))
        tweets_id = cur.fetchone()[0]
        data = status.entities["media"]
        for item in data:
            mediatype = item["type"]
            if mediatype == "video":
                # find out, which file has the highest resolution
                variantcount = 0
                highest = 0
                for variant in item["video_info"]["variants"]:
                    if "bitrate" in variant:
                        if variant["bitrate"] > highest:
                            highest = variant["bitrate"]
                            image_url = item["video_info"]["variants"][variantcount]["url"]
                            contenttype = item["video_info"]["variants"][variantcount]["content_type"]
                        else:
                            pass
                    else:
                        pass
                    variantcount += 1
                height = item["sizes"]["large"]["h"]
                width = item["sizes"]["large"]["w"]
            elif mediatype == "animated_gif":
                image_url = item["video_info"]["variants"][0]["url"]
                contenttype = item["video_info"]["variants"][0]["content_type"]
                height = item["sizes"]["large"]["h"]
                width = item["sizes"]["large"]["w"]
            else:
                image_url = item["media_url_https"]
                contenttype = "0"
                height = item["sizes"]["small"]["h"]
                width = item["sizes"]["small"]["w"]
            # download the attached files to the actual directory
            wget.download(image_url)
            # retrieve filename out of URL
            name_of_file = image_url.split("/")[-1]
            print()
            print("Dateiname:", name_of_file)
            logfile.write("Dateiname: {}\n".format(name_of_file))
            print("Medien (Typ: " + str(mediatype) + "): " + str(image_url))
            logfile.write("Medien (Typ: {}): {}\n".format(mediatype, image_url))
            # write data concerning media to the db
            cur.execute('''INSERT INTO media (tweets_id, mediatype, image, height, width, name_of_file, contenttype)
            VALUES (?, ?, ?, ?, ?, ?)''', (tweets_id, mediatype, image_url, height, width, name_of_file, contenttype))


def check_number_of_media(status):
    """check if there are media-files attached to the tweet. If yes, count how many"""
    if "extended_entities" in status._json:
        if "media" in status._json["extended_entities"]:
            amount = len(status._json["extended_entities"]["media"])
    elif "media" in status.entities:
        amount = len(status.entities["media"])
    else:
        amount = 0
    return(amount)


############################
# data for the Twitter-API #
############################
consumer_key = ""
consumer_secret = ""

access_token = ""
access_token_secret = ""


#########################
# Interaction with user #
#########################

print("""
            -::::::::::::::::::::::::::::////////////////-
            -:::::::::::::::::::::::::.`````.-://::-/////-
            -:::::- .:::::::::::::::`          `` .//////-
            -:::::.   `-:::::::::::              ``.:////-
            -:::::.      .-::::://.              .://////-
            -::::::.         ``..-.              :///////-
            -:::::-..`                           ////////-
            -:::::-                             `////////-
            -::::::-`                           :///////+-
            -::::::::-.`                       -////////+:
            -:::::///.                        -///////+++:
            -::://////-`                    `://////+++++:
            -///////////:-.`               -////+++++++++:
            -/////////::-.              `-////+++++++++++:
            :////:-.`                `-:////+++++++++++++:
            :////////:--..````...-:///////+++++++++++++++:
            :///////////////////////////+++++++++++++++++:
    """)
print("""
    Twitter-Sicherung: Im folgenden wird die Timeline des vom Nutzer
    angegebenene Twitter-Accounts gesichert. Hierzu muss der Nutzername
    eingegeben werden, beispielsweise \"Twitter\". Für weitere Infor-
    mationen siehe Readme-Datei!""")
twitteruser = input("""
    Nutzername eingeben: """)

if len(twitteruser) == 0:
    print("""
    Es muss ein Nutzername eingegeben werden - beispielsweise
    \"Twitter\". Das Skript wird nun beendet.
    """)
    sys.exit()


################################################
# Establish connection to Twitter using tweepy #
################################################

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
try:
    twittuser_id = api.get_user(twitteruser).id
except tweepy.error.TweepError as err:
    print("Fehlercode: ", err.api_code)
    print("Die Erklärung des Fehlercodes kann hier nachgeschlagen werden:")
    print("https://dev.twitter.com/overview/api/response-codes")
    print("Das Skript wird nun beendet!")
    sys.exit()


#################
# Connect to db #
#################

dbname = twitteruser + ".sqlite3"
conn = sqlite3.connect(dbname)
cur = conn.cursor()


##############################
# More Interaction with user #
##############################

# display remaining calls to API
possibilities = api.rate_limit_status()["resources"]["statuses"]["/statuses/user_timeline"]["remaining"]
print("""
    Es sind derzeit noch""", possibilities, """Aufrufe über die API möglich,
    bevor gewartet werden muss.""")

# ask user for instructions to begin new or append to existing db
print()
print("""
    Soll eine neue Sicherung begonnen werden (1)
    oder soll eine bestehende Sicherung aktualisiert werden (2)?""")

while True:
    choice = input("""
    Bitte Auswahl treffen: """)
    if choice == "1":
        while True:
            # check if input was an integer
            tweetnumber = input("""
    Wie viele Tweets sollen gesichert werden (\"0\" für alle). Maximal
    können 3200 Tweets über die API abgerufen werden. Ggf. muss man auf-
    grund der Rate-Limits Pausen in Kauf nehmen: """)
            try:
                int(tweetnumber)
            except:
                print("""
    Es muss eine Zahl eingegeben werden!
                """)
                continue
            break
        break
    elif choice == "2":
            while True:
                startpoint = input("""
    Welches ist der aktuellste bereits gesicherte Tweet: """)
                try:
                    # check if id of tweet is already in db. If not, this must be an in valid input
                    cur.execute("SELECT id FROM tweets WHERE tweet_id = ?", (startpoint, ))
                    validate = cur.fetchone()[0]
                except:
                    print("""
    Die ID des aktuellsten Tweets ist entweder ungültig oder nicht in der
    Datenbank enthalten!""")
                    continue
                break
            break
    else:
        print("""
    Ungültige Auswahl! Nur \"1\" oder \"2\" sind erlaubt!!!""")
        continue


#################################
# prepare txt-file as "logfile" #
#################################
startzeit = time.strftime("%A %d.%m.%Y; %H-%M-%S %Z")
logfile = open("logfile_" + twitteruser + "_" + startzeit + ".txt", 'w')


#  11111
#     11
#     11
#     11
#     11
#     11

# If we start a new backup of tweets or if we want to overwrite what has been
# stored yet
if choice == "1":
    cur.execute('DROP TABLE IF EXISTS users')
    cur.execute('DROP TABLE IF EXISTS tweets')
    cur.execute('DROP TABLE IF EXISTS media')
    cur.execute('''CREATE TABLE users (id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        user TEXT, twittuser_id INTEGER)''')
    cur.execute('''CREATE TABLE tweets (id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        users_id INTEGER, tweettime DATETIME, tweet TEXT, tweet_id INTEGER, url TEXT,
        amount INTEGER)''')
    cur.execute('''CREATE TABLE media (id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        tweets_id INTEGER, mediatype TEXT, image TEXT, height INTEGER,
        width INTEGER, name_of_file TEXT, contenttype TEXT)''')
    conn.commit()

    infos_for_user(startzeit)

    # write basic data concerning the Twitter-user to db
    cur.execute('''INSERT INTO users (user, twittuser_id) VALUES (?, ?)''', (twitteruser, twittuser_id))
    conn.commit()

    # get the primary key for the user out of the db to use it as foreign key
    # in the table "tweets"
    cur.execute('SELECT id FROM users WHERE user = ?', (twitteruser, ))
    user_id = cur.fetchone()[0]

    print("Benutzername:", twitteruser, "\n")
    print("")
    logfile.write("Benutzername: {}\n\n".format(twitteruser))

    print("Abarbeitung der Tweets:")
    logfile.write("Abarbeitung der Tweets:\n")

    # variable for counting the tweets
    counter = 1

    # looping through the tweets
    for status in tweepy.Cursor(api.user_timeline, tweet_mode="extended", screen_name = twitteruser).items(int(tweetnumber)):
        logfile.write("{}.\n".format(counter))
        print("Benutzername:", status.author.screen_name)
        logfile.write("Benutzername: {}\n".format(status.author.screen_name))
        print("Erstellzeitpunkt:", status.created_at)
        logfile.write("Erstellzeitpunkt: {}\n".format(status.created_at))
        print("ID des Tweets:", status.id)
        logfile.write("ID des Tweets: {}\n".format(status.id))
        print("Tweet:", status.full_text)
        logfile.write("Tweet:\n{}\n".format(status.full_text))
        # retrieve URLs attached to the tweet
        if len(status.entities["urls"]) > 0:
            data = status.entities["urls"]
            for item in data:
                url = item["url"]
            print("Kurz-URL:", url)
            logfile.write("Kurz-URL: {}\n".format(url))
        else:
            url = "0"
        amount = check_number_of_media(status)
        # write data received so far into db
        cur.execute('''INSERT INTO tweets (users_id, tweettime, tweet, tweet_id, url, amount)
            VALUES (?, ?, ?, ?, ?, ?)''', (user_id, status.created_at, status.full_text, status.id, url, amount))
        get_media(status)
        print()
        conn.commit()
        logfile.write("\n\n")
        counter += 1

#  222222
# 22     22
#      22
#     22
#   22
# 222222222

# If we want to update an existing db
elif choice == "2":
    cur.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        user TEXT, twittuser_id INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS tweets (id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        users_id INTEGER, tweettime DATETIME, tweet TEXT, tweet_id INTEGER, url TEXT,
        amount INTEGER)''')
    cur.execute('''CREATE TABLE IF NOT EXISTS media (id INTEGER PRIMARY KEY NOT NULL UNIQUE,
        tweets_id INTEGER, mediatype TEXT, image TEXT, height INTEGER,
        width INTEGER, name_of_file TEXT, contenttype TEXT)''')
    conn.commit()

    infos_for_user(startzeit)

    # get the primary key for the user out of the db to use it as foreign key
    # in the table "tweets"
    cur.execute('SELECT id FROM users WHERE user = ?', (twitteruser, ))
    user_id = cur.fetchone()[0]

    print("Benutzername:", twitteruser, "\n")
    print("")
    logfile.write("Benutzername: {}\n\n".format(twitteruser))

    print("Abarbeitung der Tweets:")
    logfile.write("Abarbeitung der Tweets:\n")

    # variable for counting the tweets
    counter = 1

    # looping through the tweets
    for status in tweepy.Cursor(api.user_timeline, since_id=startpoint, tweet_mode="extended", screen_name=twitteruser).items(0):
        # check if actual tweet is already stored in db
        cur2 = conn.cursor()
        cur2.execute('''SELECT tweet_id FROM tweets WHERE tweet_id = ?''',
            (status.id, ))

        try:
            found = cur2.fetchone()[0]
            print("Der Tweet mit der ID", status.id, "ist bereits in der Datenbank enthalten!")
            print("Er wird nicht erneut gespeichert.")
            print()
            logfile.write("Der Tweet mit der ID {} ist bereits in der Datenbank enthalten.\n".format(status.id))
            logfile.write("Er wird nicht erneut gespeichert.\n\n")
            continue
        except:
            pass
        logfile.write("{}.\n".format(counter))
        print("Benutzername:", status.author.screen_name)
        logfile.write("Benutzername: {}\n".format(status.author.screen_name))
        print("Erstellzeitpunkt:", status.created_at)
        logfile.write("Erstellzeitpunkt: {}\n".format(status.created_at))
        print("ID des Tweets:", status.id)
        logfile.write("ID des Tweets: {}\n".format(status.id))
        print("Tweet:", status.full_text)
        logfile.write("Tweet:\n{}\n".format(status.full_text))
        # retrieve URLs attached to the tweet
        if len(status.entities["urls"]) > 0:
            data = status.entities["urls"]
            for item in data:
                url = item["url"]
            print("Kurz-URL:", url)
            logfile.write("Kurz-URL: {}\n".format(url))
        else:
            url = "0"
        amount = check_number_of_media(status)
        # write data received so far into db
        cur.execute('''INSERT INTO tweets (users_id, tweettime, tweet, tweet_id, url, amount)
            VALUES (?, ?, ?, ?, ?, ?)''', (user_id, status.created_at, status.full_text, status.id, url, amount))
        get_media(status)
        print()
        conn.commit()
        logfile.write("\n\n")
        counter += 1


# The "end", which is the same in both cases
print("Es wurden insgesamt", counter - 1, "Tweets gesichert.")
logfile.write("Es wurden insgesamt {} Tweets gesichert.\n\n".format(counter - 1))
abschlusszeit = time.strftime("%A %d.%m.%Y; %H-%M-%S %Z")
print("Ende der Sicherung:", abschlusszeit)
logfile.write("Ende der Sicherung: {}".format(abschlusszeit))


# closing the logfile
logfile.close()
