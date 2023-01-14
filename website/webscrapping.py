import requests
from bs4 import BeautifulSoup
import re


def get_main_wiki_image(artist):
  person_url = []
  urlpage =  'https://en.wikipedia.org/wiki/' + artist
  page = requests.get(urlpage).text
  soup = BeautifulSoup(page, 'html.parser')
  for raw_img in soup.find_all('img'):
   link = raw_img.get('src')
   if re.search('wikipedia/.*/thumb/', link) and not re.search('.svg', link):
     person_url = [artist, link]
     break
  try:
    return person_url[1][2:]
  except IndexError:
    return "No image"