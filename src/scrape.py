GENIUS_API_TOKEN='hgHXjEpkYI85Ud6Bw2LWCwrLlYcznI3pjq0NANvSq7fDkG6Pvb9qi06S7HnJVDCs'

# Make HTTP requests
import requests
# Scrape data from an HTML document
from bs4 import BeautifulSoup, Tag
# I/O
import os
# Search and manipulate strings
import re
import shutil
from nrclex import NRCLex
import text2emotion as te
import nltk
nltk.download('omw-1.4')

# MongoDB Configuratin
import pymongo
from pymongo import MongoClient
cluster = pymongo.MongoClient("mongodb+srv://luna-admin:1234@cluster0.sbx0f.mongodb.net/emotion_recognition?retryWrites=true&w=majority")
db = cluster["emotion_recognition"]
collection = db["artists"]


# Get artist object from Genius API
def request_artist_info(artist_name, page):
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_API_TOKEN}
    search_url = base_url + '/search?per_page=10&page=' + str(page)
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    return response

# Get Genius.com song url's from artist object
def request_song_url(artist_name, song_cap):
    page = 1
    songs = []
    
    while True:
        response = request_artist_info(artist_name, page)
        json = response.json()
        # Collect up to song_cap song objects from artist
        song_info = []
        for hit in json['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                song_info.append(hit)
    
        # Collect song URL's from song objects
        for song in song_info:
            if (len(songs) < song_cap):
                url = song['result']['url']
                songs.append(url)
            
        if (len(songs) == song_cap):
            break
        else:
            page += 1
        
    print('Found {} songs by {}'.format(len(songs), artist_name))
    return songs

# Scrape lyrics from a Genius.com song URL
def scrape_song_lyrics(url, artist_name):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    extractedLyrics = html.find('div', id='lyrics-root')
    if(extractedLyrics):
        artist_name = html.find('h2').get_text()
        lyricsArray = extractedLyrics.contents
        del lyricsArray[-1]
        formattedLyrics = ''
        for x in lyricsArray:
            if(len(x.contents) > 0):
                stringsContent = list(x.strings)
                formattedStringsContent = list(dict.fromkeys(stringsContent))
                for y in formattedStringsContent:
                    if(y[0] != '['):
                        txt2EmotionEmotions = te.get_emotion(y)
                        nrcLexEmotions = NRCLex(y)
                        emotionStr = ''
                        for x in nrcLexEmotions.top_emotions:
                            if(x[1] != 0):
                                emotionStr = x[0]
                            else:
                                for key in txt2EmotionEmotions:
                                    if(txt2EmotionEmotions[key] != 0):
                                        emotionStr = key
                        if(len(emotionStr) > 0):
                            formattedLyrics = formattedLyrics + '\n' + y + '\t' + emotionStr
        return formattedLyrics
    else:
        return

def Save_artist_on_DB(name):
    file = open(name.lower() + '.txt', 'r', encoding="utf8")
    content = file.read();
    doc = {
        "name": name.lower(),
        "content": content
    }
    collection.insert_one(doc)
    file.close()

def write_lyrics_to_file(artist_name, song_count):
    urls = request_song_url(artist_name, song_count)
    f = open(artist_name.lower() + '.txt', 'w', encoding="utf-8")
    lyrics = ''
    for url in urls:
        lyrics = lyrics + scrape_song_lyrics(url, artist_name)
    f.write(lyrics)
    f.close()
    Save_artist_on_DB(artist_name)


while(1):
    artist = input('Digite o nome do artista: ')
    if(collection.count_documents({"name":artist}) > 0):
        print(collection.find({"name": artist.lower()}).count())
        print("Já existe")
    else:
        count = 100
        write_lyrics_to_file(artist, count)
