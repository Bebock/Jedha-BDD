#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Import des librairies utilisées 

import re  
import unidecode
from bs4 import BeautifulSoup
import requests
from math import *
import pandas as pd
import json
import plotly.graph_objects as go
import plotly.io as pio
pio.renderers.default = "notebook"
import plotly.express as px
from datetime import datetime
import os 
import logging
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.shell import inspect_response


# # Etape 1 : Liste des destinations
# 
# En première intention, on va se focaliser sur les meilleurs destinations de France. Ce top des villes où voyager sera basé sur le classement du site One Week In.com. 
# 
# On utilisera ici la librairie BeautifulSoup. 

# In[2]:


cities = []

response = requests.get('https://one-week-in.com/35-cities-to-visit-in-france/')
soup = BeautifulSoup(response.text, "html.parser")

ol = soup.find('ol')
for li in ol.find_all("li"):
    cities.append(li.text)


# In[3]:


# Remplacer les espaces par des tirets pour faciliter l'utilisation dans les recherches

def putTiret(input):  
    s1 = unidecode.unidecode(input)
    words = re.findall('[A-Z][a-z]*', s1)  
    result = []  
    for word in words:  
        word = chr( ord (word[0]) + 32) + word[1:]  
        result.append(word)  
    return('-'.join(result))  

for i in range(len(cities)) : 
    cities[i] = putTiret(cities[i])

print(cities)


# # Etape 2 : Scraper Booking.com
# 
# Pour recueillir les informations relatives aux hôtels des destinations possibles, on va scraper le site de booking.com : 
# 
# * Le nom de l'hôtel
# * L'Url de l'hôtel dans la page booking,
# * Ses coordonnées géographiques : latitude et longitude
# * Son score (rating)
# * La description de l'hôtel

# ## Etape 2.1 : Paramétrage des cookies et headers
# 
# Afin de faciliter le scraping, il convient de paramétrer les fonctions en accord avec le navigateur internet utilisé. 
# 
# Attention : Ce paramétrage doit être fait par l'utilisateur de ce code, sur son propre ordinateur. 
# 
# Methode : Dans Firefox, récuperer les infos header / cookies de la page Web Booking
# * Inspect 
# * Onglet Réseau 
# * Fichier www.booking.com
# * Clic droit - Copy - Copy as cURL (windows)
# * Convertir en python en utilisant https://curlconverter.com/
# 

# In[4]:


# Résultat obtenu pour ma configuration

cookies = {
    ### COPIER LE CONTENU CURL
}

headers = {
    ### COPIER LE CONTENU CURL
}


# ## Etape 2.1 : Solution BeautifulSoup
# 
# Avec BeautifulSoup il n'est pas possible de scraper en cascade (de suivre un lien pour scraper l'information contenu dans une page annexe). Le travail s'effectue donc en 2 temps. 
# 
# En premier lieu, on va pouvoir récupérer pour chacune des 35 destinations, la liste des 20 hôtels les mieux notés et l'url correspondant à chacun d'eux. 

# In[16]:


# Selection des 20 premiers hotels classés par "preferes" (Top 20) 
    # Pas de date pour prendre les meilleurs hotels indépendamment de la disponibilité
    # Peut être paramétré par la suite pour adapter le classement des hôtels selon leur disponibilité au moment du voyage

liste_villes = []
liste_url = []

for ville in cities :     
    params = (
        ('ss', ville),
        ('rows', '25'),
        ('offset', '0'), 
#        ('checkin_year', str(datetime.now().year)),
#        ('checkin_month', str(datetime.now().month)),
#        ('checkin_monthday', str(datetime.now().day)),
        ('order', 'popularity') 
    )
    response = requests.get('https://www.booking.com/searchresults.fr.html', headers = headers, params = params, cookies = cookies)
    soup=BeautifulSoup(response.text, "html.parser")
    nb_result = min(20, int(re.search(': (.+?) établissements', soup.find('h1').get_text()).group(1).replace(" ", "")))
   
    urls = [link['href'] for link in soup.select('a', href=True)]
    urls = list(set(
        [url for url in urls if "searchresults#hotelTmpl" in url and 
            "https://www.booking.com/hotel/fr" in url and
            any(i in url for i in ['hpos=' + str(i) + '&' for i in range(1,(nb_result+1))])]))
    liste_url.extend(urls) # URL stocké dans la liste d'url
    
    liste_villes.append([ville, nb_result]) # Récupération de l'information : Ville - Nombre de résultats trouvés


# In[18]:


print(liste_villes)


# Une fois ce premier scraping effectué, on va pouvoir, à l'intérieur de chaque url précédemment recueilli, aller récupérer les informations dont on a besoin. 

# In[19]:


# Creation d'un vecteur qui attribue à chaque url dans la liste scrapée, la ville correspondante, en fonction de sa position dans la liste. 

vecteur = []
for i in iter(liste_villes): 
   vecteur = vecteur + [i[0] for j in range(int(i[1]))] 


# In[ ]:


# Initation d'une table vide pour recueillir les informations

table_hotels = pd.DataFrame([])

# Boucle qui permet pour chaque url de la liste : 
for i in range(len(liste_url)):
    response = requests.get(liste_url[i], headers=headers,  cookies=cookies)
    soup = BeautifulSoup(response.text, 'html.parser')
    data = json.loads(soup.find('script', type='application/ld+json').text)
    adresse = data.get('address').get('streetAddress') # Récupération de l'adresse
    rating = []
    if 'aggregateRating' in data.keys():
        rating.append(data.get('aggregateRating').get('ratingValue')) # Récupération du score moyen
        rating.append(data.get('aggregateRating').get('reviewCount')) # Récupération du nombre d'évaluations
        del data['aggregateRating']
        data['ratingValue'] = rating[0]
        data['nb_review'] = rating[1]
    del data['address']
    data['address'] = adresse
    data['city'] = vecteur[i] # Récupération de la ville 
    table_hotels = table_hotels.append(data, ignore_index = True) # Append du dictionnaire généré au datafrane table_hotel


# In[21]:


table_hotels.to_csv('PATH/table_hotels_BS.csv', index = False, header = True)


# ## Etape 2.2 : Solution Scrapy
# 
# On l'a vu, BeautifulSoup est très simple d'utilisation, mais il est chronophage et ne permet pas de suivre les liens pour scraper en chaine. 
# 
# Un outil un peu plus complexe à mettre en place, mais plus puissant va nous permettre de réaliser le même travail : Scrapy. Plus complexe, parce qu'en effet, il nécessaite d'aller récupérer sur le site web en question les balises qui permettent de localiser dans la page web les informations souhaitées. 
# Les balises se trouve avec l'outil INSPECTER (clic droit sur votre page web). 
# 
# ATTENTION : Booking.com, tout comme de nombreux sites web actualise régulièrement ses balises pour limiter le scraping. Il est donc tout à fait possible que ce code ne fonctionne plus et qu'il faille l'actualiser pour relancer le scraping. 
# L'avantage de BeautifulSoup ici est qu'il n'est pas nécessaire de recommencer ce process de localisation des balises. 

# In[ ]:


# Paramétrage des headers [navigateur web]

headers = {
    'User-Agent': 'custom user agent',
    'Accept': '*/*',
    'Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.booking.com/index.fr.html?label=gen173nr-1BCAEoggI46AdIM1gEaE2IAQGYAQ24ARfIAQ_YAQHoAQGIAgGoAgO4At_sipAGwAIB0gIkMjczOWJjYWUtYmQ3My00Mjk0LTlhZmEtOGZlMzE3NDBiMTE02AIF4AIB;sid=031a64604fe18bc00182763eefeee826;keep_landing=1&sb_price_type=total&',
    'Redirect_enabled': True
}

class Booking(scrapy.Spider):
    # Name of your spider
    name = "Booking"
    cities = ['mont-saint-michel', 'st-malo', 'bayeux', 'le-havre', 'rouen', 'paris', 'amiens', 'lille', 'strasbourg', 'chateau-haut-koenigsbourg', 'colmar', 'eguisheim', 'besancon', 'dijon', 'annecy', 'grenoble', 'lyon', 'verdon-gorge', 'bormes-mimosas', 'cassis', 'marseille', 'aix-provence', 'avignon', 'uzes', 'nimes', 'aigues-mortes', 'saintes-maries', 'collioure', 'carcassonne', 'ariege', 'toulouse', 'montauban', 'biarritz', 'bayonne', 'la-rochelle']
    
    def start_requests(self):
        start_urls = [f'https://www.booking.com/searchresults.fr.html?ss={i}&rows=25&offset=0&order=popularity' for i in self.cities]
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=headers, 
                                 meta = {'url1' : url})

    def parse(self, response):
        url1 = response.meta['url1']
        for href in response.css("h3 > a::attr('href')"):
            link = response.urljoin(href.extract())
            if "searchresults#hotelTmpl" in link and "https://www.booking.com/hotel/fr" in link and any(i in link for i in ['hpos=' + str(i) + '&' for i in range(1,21)]):             
                yield scrapy.Request(url = link, callback = self.parse2, headers=headers, 
                                 meta={'url1' : url1})

    def parse2(self, response):
        url1 = response.meta['url1']
        hotels = response.xpath("//h2[@class='hp__hotel-name']") # Récupération du nom de l'hotel suivant sa balise
        adresses = response.xpath("//p[@class='address address_clean']/span") # Récupération de l'adresse de l'hotel suivant sa balise
        ratings = response.xpath("//div[@class='b5cd09854e d10a6220b4']") # Récupération du rating de l'hotel suivant sa balise
        raters = response.xpath("//div[@class='d8eab2cf7f c90c0a70d3 db63693c62']") # Récupération du nombre d'évaluations suivant sa balise
        latlon = response.xpath("//a[@id='hotel_address']") # Récupération des coordonnées de l'hotel suivant sa balise
        desc = response.xpath("//div[@id='property_description_content']") # Récupération de la description de l'hotel suivant sa balise
        for i in range(len(hotels)):
            yield{
                'url1' : url1,
                'url': response.url,
                'name': hotels[i].css('::text').extract()[2].strip(),
                'adresse': adresses[i].css('::text').extract()[0].strip(),
                'rating': ratings[i].css('::text').extract(),
                'rater': raters[i].css('::text').extract()[0].strip(),   
                'latlong': latlon[i].css('::attr("data-atlas-latlng")').extract(),
                'description': desc[i].css('::text').extract()    
            }
                
# Name of the file where the results will be saved
filename = "1_randomquote.json"

# If file already exists, delete it before crawling 
if filename in os.listdir('src/'):
        os.remove('src/' + filename)

process = CrawlerProcess(settings = {
    'USER_AGENT': 'custom user agent',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        'src/' + filename : {"format": "json"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(Booking)
process.start()


# In[8]:


df = pd.read_json('src/1_randomquote.json')   
df.shape


# In[9]:


df.head()


# In[10]:


# Data cleaning

df['city'] = None
for i in range(len(df)):
    df.city[i] = re.search("ss=(.+?)&rows",df.url1[i]).group(1)
    df.rating[i] = float(df.rating[i][0].replace(",", "."))
    if(' expériences' in df.rater[i].replace(" ", "")) : 
        df.rater[i] = int(df.rater[i].split(' expérience')[0].replace(" ", ""))
    else : 
        df.rater[i] = int(df.rater[i].split('expérience')[0].replace(" ", ""))
    df.description[i] = ' '.join(df.description[i][1:-1]).replace("\n", "")
df.head(5)


# In[11]:


df.to_csv('PATH/table_hotels_scrapy.csv', index = False, header=True)

