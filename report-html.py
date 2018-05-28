#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import sqlite3

# user must specify the sqlite3-db, where the data is stored
if len(sys.argv) == 1:
    print("""
    Es muss die als Grundlage dienende Datenbank angegeben werden!
    Das Skript wird nun beendet.
    """)
    sys.exit()
else:
    dbname = sys.argv[1]

# establishing a connecting to the db and opening the file for the
# HTML-report
conn = sqlite3.connect(dbname)
cur = conn.cursor()

filename = dbname[:-8] + ".html"
report = open(filename, 'w')


# creating the start of the html-code, including a "headline"
report.write("<!doctype html>\n")
report.write("<html lang=\"de\">\n")
report.write("<head>\n")
report.write("<meta charset=\"UTF-8\"/>\n")
report.write("<title>Twitternachrichten von ")
report.write(dbname[:-8])
report.write("</title>\n")
report.write("<style>\n")
report.write("body {font-family: sans-serif;}\n")
report.write("</style>\n")
report.write("</head>\n\n")
report.write("<body>\n")

report.write("<h1>Twitternachrichten von ")
report.write(dbname[:-8])
report.write("</h1>\n\n")

# This is how the data are returned form the db
# tweet[0] = id
# tweet[1] = ID of Twitter-User
# tweet[2] = tweettime
# tweet[3] = text of the tweet
# tweet[4] = ID of the tweet
# tweet[5] = url ("0" if no URL attached to tweet)
# tweet[6] = amount of attached media-files

# we creat an empty list to temporarily store all the data of the
# tweets coming from the db
tweetlist = []

# we append all tweets to the list. Why? Because otherwise there will be
# problems with the further SQL-statements...
data = cur.execute('''SELECT * from tweets ORDER BY tweets.tweettime DESC''')
for row in data:
    tweetlist.append(row)

# how many tweets do we have?
countdown = len(tweetlist)

# writing the data from the db into the html-file by processing all the
# tweets in the list
for tweet in tweetlist:
    report.write("<p><strong>")
    report.write(str(countdown))
    report.write(". Tweet vom ")
    report.write(tweet[2])
    report.write(" (ID des Tweets: ")
    report.write(str(tweet[4]))
    report.write("):</strong><br>\n")
    report.write(str(tweet[3]))
    report.write("<br>\n")
    if tweet[5] == "0": # has tweet an extra URL attached?
        report.write("URL: keine zusätzliche URL angefügt.<br>\n")
    else:
        report.write("URL: <a href=\"")
        report.write(str(tweet[5]))
        report.write("\" target=\"_blank\">")
        report.write(str(tweet[5]))
        report.write("</a><br>\n")
    if tweet[6] == 1 or tweet[6] > 1:
        for item in cur.execute('''SELECT mediatype, image, height, width, name_of_file, contenttype FROM media WHERE tweets_id = ?''', (tweet[0], )):
            report.write("URL zum Medium: <a href=\"")
            report.write(str(item[1]))
            report.write("\" target=\"_blank\">")
            report.write(str(item[1]))
            report.write("</a><br>")
            report.write("Medien (Typ: ")
            report.write(item[0])
            report.write("):<br>\n")
            if item[0] == "photo":
                imgstr = "<img src=\"" + str(item[4]) + "\" width=\"" + str(item[3]) + "\" height=\"" + str(item[2]) + "\" alt=\"Bild konnte nicht geladen werden!\" /><br>"
                report.write(imgstr)
            elif item[0] == "video" or item[0] == "animated_gif":
                imgstring1 = "<video width=\"" + str(item[3]) + "\" height=\"" + str(item[2]) + "\" controls>\n"
                report.write(imgstring1)
                imgstring2 = "<source src=\"" + str(item[4]) + "\" type=\"" + str(item[5]) + "\">\n"
                report.write(imgstring2)
                imgstring3 = "</video>\n"
                report.write(imgstring3)
            report.write("\n")
    else:
        report.write("Medien: keine Medien angefügt.\n")
    report.write("</p>\n")
    countdown -= 1


# closing the body- and the html-tag
report.write("</body>\n")
report.write("</html>")

# close outout-file after work is finished
report.close()
