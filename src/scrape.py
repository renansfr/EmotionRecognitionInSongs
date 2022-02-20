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
def scrape_song_lyrics(url, directory):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', id='lyrics-root')
    if(lyrics):
        title = html.find('h2').get_text()
        verses = lyrics.find_all('span')
        del verses[-1]
        formattedLyrics = ''
        for x in verses:
            if(len(x.contents) > 0 and x.get_text()):
                for y in x.contents:
                    if(isinstance(y, Tag)):
                        formattedLyrics = formattedLyrics + '\n'
                    else:
                        formattedLyrics = formattedLyrics + y
        f = open(directory + '/' + title.lower() + '.txt', 'w')
        f.write(formattedLyrics)
        f.close()
        return
    else:
        return

def write_lyrics_to_file(artist_name, song_count):
    urls = request_song_url(artist_name, song_count)
    directory = artist_name.lower()
    parent_dir = './'
    path = os.path.join(parent_dir, directory)
    if os.path.exists(path):
        shutil.rmtree(path)
    os.mkdir(path)
    for url in urls:
        scrape_song_lyrics(url, directory)


while(1):
    artist = input('Digite o nome do artista: ')
    count = int(input('Digite quantas músicas você quer do artista: '))
    write_lyrics_to_file(artist, count)
