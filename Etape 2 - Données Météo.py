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


# # Etape 1 : Collecter les coordonnées GPS de chaque ville via une API
# 
# On utilisera https://nominatim.org/ pour avoir les coordonnées GPS des 35 villes (pas de souscription requise). 
# 
# Documentation : https://nominatim.org/release-docs/develop/api/Search/

# In[7]:


liste_hotels = pd.read_csv('PATH/table_hotels_scrapy.csv')


# In[8]:


# Nombre d'hotels disponibles dans la ville (max 20 - on a choisi de ne retenir que les 20 meilleurs hotels)

liste_villes = pd.DataFrame(liste_hotels.groupby('city').size().reset_index(name = "N_hotels"))
liste_villes


# In[ ]:


# Initialisation des variables latitude et longitude

liste_villes['lat'] = None
liste_villes['lon'] = None

# Récupération des coordonnées pour chaque ville à l'aide d'une boucle
for i, c in enumerate(liste_villes.city):
    coord = requests.get('https://nominatim.openstreetmap.org/search?q={}+France&format=json'.format(c))
    coord2 = json.loads(coord.text)
    liste_villes['lat'][i] = coord2[0]['lat']
    liste_villes['lon'][i] = coord2[0]['lon']


# In[10]:


liste_villes.head()


# In[7]:


liste_villes.to_csv('PATH/table_villes_coord.csv', index = False, header=True)


# # Etape 2 : Collecter les données météorologiques via une API
# 
# On va utiliser le site https://openweathermap.org/appid (l'inscription est obligatoire pour obtenir une apikey gratuite) et https://openweathermap.org/api/one-call-api pour rassembler les informations météorologique des 35 villes. 

# In[ ]:


#liste_villes = pd.read_csv('PATH/table_villes_coord.csv')

data_meteo = pd.DataFrame([])
for i in range(len(liste_villes)) :
    meteo = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'.format(
        str(liste_villes.lat[i]), 
        str(liste_villes.lon[i]),
        'VOTRE_CLE'))

    weather_data = pd.json_normalize(meteo.json()['daily'])
    weather_data['city'] = liste_villes.city[i]
    data_meteo = data_meteo.append(weather_data,ignore_index=True) 

data_meteo.to_csv('PATH/data_meteo.csv', index = False, header=True)


# In[12]:


data_meteo.head()


# On obtient les données météorologiques pour les 7 prochains jours en plus d'aujourd'hui. 

# In[19]:


data_meteo['city'].value_counts()


# # Etape 3 : Classement des destinations

# On va maintenant retraiter cette base de données afin de générer un "score" pour chaque ville et donc un classement des villes selon la météo qu'il va faire dans la semaine qui s'annonce.
# 
# On décide (un peu arbitrairement et subjectivement) de baser notre classement météorologique sur 2 variables : La temperature ressentie moyenne sur les prochains jours et le nombre de jours de pluie. 

# In[20]:


#data_meteo = pd.read_csv('PATH/data_meteo.csv')

data_meteo = data_meteo.groupby(['city']).agg({'feels_like.day': 'mean', 
                                               'rain' : lambda x: x[x != 0].count()})

data_meteo = data_meteo.sort_values(['rain', 'feels_like.day'], ascending=[True, False])

data_meteo.reset_index(inplace=True)
data_meteo.insert(0, 'ID', data_meteo['city'].str[:5])
data_meteo['rank'] = range(1,len(data_meteo) + 1)

data_meteo.to_csv('PATH/data_meteo.csv', index = False, header=True)

