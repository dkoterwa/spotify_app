import requests
from bs4 import BeautifulSoup
import re
from unidecode import unidecode

def get_main_wiki_image(artist):
    artist = unidecode(artist).replace(' ', '-')
    person_url = []
    urlpage =  'https://www.aaemusic.com/artist/' + artist
    page = requests.get(urlpage).text
    soup = BeautifulSoup(page, 'html.parser')
    for raw_img in soup.find_all('img', {"class":"img-responsive artist-img lazyautosizes lazyload blur"}):
        link = raw_img.get('src')
        person_url = [artist, link]
    # if re.search('wikipedia/.*/thumb/', link) and not re.search('.svg', link):
    #   person_url = [artist, link]
    #   break
    try:
        return person_url[1]
    except IndexError:
        return artist