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
import nbformat
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
import folium
from pyproj import crs
import matplotlib.pyplot as plt
from colour import Color
from turtle import width
from folium import plugins
from IPython.display import HTML
from folium.plugins import FastMarkerCluster, MarkerCluster


# # CARTE 1 : Classement des villes selon la météo à venir

# In[2]:


# Import des données 

liste_villes = pd.read_csv('PATH/table_villes_coord.csv')
data_meteo = pd.read_csv('PATH/data_meteo.csv')

# Aggrégation des 2 bases de données par ville

data = pd.merge(data_meteo, liste_villes, on = 'city')
data.head()


# In[3]:


# Création de la variable de classement inversé

data['rank_rev'] = 36 - data['rank']


# ## Version 1 : PLOTLY

# In[5]:


fig = px.scatter_mapbox(data, 
                        lat = "lat", 
                        lon = "lon",
                        hover_name = 'city', 
                        zoom = 4, 
                        size = 'rank_rev',
                        color = 'rank',
                        labels = {'rank' : "Classement"},
                        color_continuous_scale = px.colors.diverging.RdYlGn[::-1], 
                        hover_data = dict(rank_rev=False,
                                    rank=True,
                                    rain = ':.0f',
                                    lat=False, 
                                    lon=False), 
                        title = 'Classement des villes où la météo va être la plus favorable <br><sup>Source : https://openweathermap.org/appid', 
                        width = 900*1.5, 
                        height = 500*1.5)
fig.update_layout(
    title_x=0.5,
    mapbox_style="open-street-map", showlegend=False)
fig.show()


# ## Version 3 : FOLIUM
# 
# Permet d'ajouter directement le classement des villes sur la carte. 

# In[168]:


red = Color("green")
colors = list(red.range_to(Color("red"),35))

data['color'] = colors
data['anchor'] = data['rank'].apply(lambda x : (10,11) if x > 9 else (6.5,11))

locations = data[['lat', 'lon']]
locationlist = locations.values.tolist()
len(locationlist)

f = folium.Figure(width=1000, height=800)

map = folium.Map(titles = "essai", 
                 location=[46.8534, 2.3488],
               zoom_start=6, 
               width = 1000, 
               height = 600,
               tiles = 'Stamen Terrain').add_to(f)

for i in range(len(data)):
    icon = folium.DivIcon(icon_anchor= data['anchor'][i], html=f"""<div style="font-family: courier new; text-align: center; font-weight: bold; font-size: large">{data['rank'][i]}</div>""")
    folium.Marker(locationlist[i], popup=data['city'][i], icon=icon).add_to(map)
    map.add_child(folium.CircleMarker(locationlist[i], radius=12, color = str(data['color'][i])))

title_html = '''
             <h3 align="center" style="font-size:20px"><b>Classement des villes où la météo va être la plus favorable <br><sup>Source : https://openweathermap.org/appid</b></h3>
             '''

map.get_root().html.add_child(folium.Element(title_html))

map


# # CARTE 2 : Classement des hôtels pour la destination 

# In[139]:


table_hotels = pd.read_csv('PATH/table_hotel_booking.csv')


# ## Version 1 : Classement des hôtels pour la destination choisie par l'utilisateur

# In[22]:


choix = input('Entrez le classement de la destination où vous souhaitez aller :')


# In[ ]:


# Récupération des hotels de la destination choisie

hotels_choix = table_hotels[table_hotels['city'].isin(data['city'][data['rank'] == int(choix)])].reset_index()

# Extraction de la longitude et latitude 

hotels_choix['lat'] = 0
hotels_choix['lon'] = 0

for i in range(len(hotels_choix)) : 
    hotels_choix['lat'][i] = float(hotels_choix['latlong'].iloc(axis = 0)[i][hotels_choix['latlong'].iloc(axis = 0)[i].index("['")+ 2: hotels_choix['latlong'].iloc(axis = 0)[i].index(",")])
    hotels_choix['lon'][i] = float(hotels_choix['latlong'].iloc(axis = 0)[i][hotels_choix['latlong'].iloc(axis = 0)[i].index(",") + 1: hotels_choix['latlong'].iloc(axis = 0)[i].index("']")])


# In[146]:


# Creation d'une nouvelle colonne pour le nom de l'hotel (name étant un terme réservé)

hotels_choix['Hotel'] = hotels_choix.name


# In[147]:


# Classement des hotels selon leur rating

hotels_choix = hotels_choix.sort_values('rating', ascending=False)
hotels_choix.reset_index(inplace=True)
hotels_choix['rank'] = range(1,len(hotels_choix) + 1)
hotels_choix['rev_rank'] = len(hotels_choix) - hotels_choix['rank']


# In[160]:


fig = px.scatter_mapbox(hotels_choix, 
                        lat = "lat", 
                        lon = "lon",
                        hover_name = 'Hotel', 
                        size = 'rev_rank',
                        zoom = 12, 
                        opacity = 1,
                        color = 'rank',
                        labels = {'rank' : "Classement"},
                        color_continuous_scale = px.colors.diverging.RdYlGn[::-1], 
                        hover_data = dict(
                                    rank=True,
                                    rating = ':.0f',
                                    rev_rank = False,
                                    rater = True,
                                    lat=False, 
                                    lon=False), 
                        title = 'Classement des hôtels dans la destination de votre choix <br><sup>Source : https://www.booking.com', 
                        width = 900*1.5, 
                        height = 500*1.5)
fig.update_layout(
    title_x=0.5,
    mapbox_style="open-street-map", showlegend=False)
fig.show()


# ## Version 2 : Classement des hôtels pour les 5 TOP destinations

# In[ ]:


# Récupération des hotels du TOP 5 des destinations

hotels_Top5 = table_hotels[table_hotels['city'].isin(data['city'][data['rank'] < 6])].reset_index()

# Extraction de la longitude et latitude 

hotels_Top5['lat'] = 0
hotels_Top5['lon'] = 0

for i in range(len(hotels_Top5)) : 
    hotels_Top5['lat'][i] = float(hotels_Top5['latlong'].iloc(axis = 0)[i][hotels_Top5['latlong'].iloc(axis = 0)[i].index("['")+ 2: hotels_Top5['latlong'].iloc(axis = 0)[i].index(",")])
    hotels_Top5['lon'][i] = float(hotels_Top5['latlong'].iloc(axis = 0)[i][hotels_Top5['latlong'].iloc(axis = 0)[i].index(",") + 1: hotels_Top5['latlong'].iloc(axis = 0)[i].index("']")])


# In[106]:


# Creation d'une nouvelle colonne pour le nom de l'hotel (name étant un terme réservé)

hotels_Top5['Hotel'] = hotels_Top5.name


# In[107]:


# Classement des hotels selon leur rating

hotels_Top5 = hotels_Top5.sort_values('rating', ascending=False)
hotels_Top5.reset_index(inplace=True)
hotels_Top5['rank'] = range(1,len(hotels_Top5) + 1)


# In[111]:


# Attribution d'une coleur selon le rang assigné (création de 4 catégories)

hotels_Top5['marker_color'] = pd.cut(hotels_Top5['rank'], bins = 4, labels = ['green', 'lightgreen', 'orange', 'red'])


# In[169]:


# Création de la carte

f = folium.Figure(width=1000, height=800)

map = folium.Map(location=[hotels_Top5['lat'].mean(), 
                         hotels_Top5['lon'].mean()], 
               zoom_start = 6, 
               width = 1000,
               height = 800,
               tiles='Stamen Terrain').add_to(f)

marker = MarkerCluster(name = "Marker Cluster")

for index, row in hotels_Top5.iterrows():
  
  folium.CircleMarker(location = [row['lat'], row['lon']],
                        radius = 15,
                        color = row['marker_color'],
                        popup = folium.Popup("Nom :{}<br>Evaluation :{}<br>".format(row.Hotel, row.rating), 
                                             min_width = 100, 
                                             max_width = 200),
                        fill = True).add_to(marker)

marker.add_to(map)

folium.LayerControl().add_to(map)

title_html = '''
             <h3 align="center" style="font-size:20px"><b>Hotels du TOP 5 des destinations <br><sup>Source : www.booking.com</b></h3>
             '''
             
map.get_root().html.add_child(folium.Element(title_html))

map

