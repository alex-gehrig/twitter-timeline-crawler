# 1. Preface
This script came into existence after reading an article in the german IT-magazine c't.
Although I did not use OS-specific code (at least I think so), the script does not work
under Windows. The problem is, that there occur problems with emoticons used in the tweets.
Those will lead to a crash of the script, because Windows does not seem not to be able
to deal with them. Unfortunately I could not find a fix for that problem. And as I do
not own an Apple-device I could not test it with this OS.

Most of the variables and functions have english names, comments are in English too, whereas
the interaction with the user and the output is in German.

# 2. Purpose of the script
The script downloads the specified amount of tweets from a Twitter-account and stores them
together with some additional data in a SQLite3-Database, which gets its filename from the
chosen Twitter-account. Additionally all images, videos and animated gif's are downloaded to
the folder in which the script was started.

After that process you use the second Python-script together with the created database to create the
'final output': a HTML-file which contains the tweets, the additional data and the images
respectively videos. 

# 3. Preparation
## 3.1 Installing necessary Software and Python-modules
The script needs Python 3 and several standard-modules (like 'time' or 'sys'). Furthermore
you need tweepy and wget, which you can install using pip, for example using the provided
requirements.txt:

`sudo -H pip3 install -r requirements.txt`

## 3.2 Preparing the script after downloading it
You have to enter your own credentials for the Twitter-API. They must be entered in lines
132, 133, 135 and 136.

# 4. Usage
To start the script simply navigate to the folder where you stored the script and enter

`python3 twitter-timeline-crawler.py`

You will be prompted to enter the Twitter-name from which you want to save tweets. Now you have
to choose if you want to start a new download and database or if you want to update an existing
one.

In both cases a logfile will be written. The filename consists of the Twitter-name and the date
and time when the script started with his work.

## 4.1 New download and database
If you start a new download and database you have to specify how many tweets have to be
downloaded. Counting always starts from the newest tweet: 'from new to old'. If there is already
an older database of the same Twitter-name, the tables will be dropped.

## 4.2 Update
In case you chose to update you have to enter the ID of the newest tweet that is stored in
the actual version of the database. The script now searches for that ID to ensure, that
everything is going right. If the script does not find this ID, it will tell you and terminate.
If the script finds the ID in the database, it starts to download all the tweets since the
given one.

To avoid problems with duplicates, the tweets and additional media are only downloaded, if
they aren't already stored. Let's assume you enter a wrong ID by mistake and you have
already stored 10 tweets that are newer than the one of which you entered the ID. In this
case you will get the information for those 10 tweets that they got skipped.

## 4.3 Creating the HTML-file
When the download has finished, you have to use the second script. Let's assume, you stored
tweets from 'Twitter', so you end up with a database with the filename 'Twitter.sqlite3'. Now
type

`python3 report-html.py Twitter.sqlite3`

to produce the HTML-file, that will be named 'Twitter.html'. Now you can open the file with
your preferred browser, read the tweets, see the additional data of those tweets and eventually
existing media files. The media files are just linked to the downloaded files in the folder of
the script.

Thanks to HTML5, Videos can be controlled within the browser (play, pause, etc.).