#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Import des librairies utilisées 

import pandas as pd
import boto3
import io
from sqlalchemy import create_engine
from sqlalchemy.sql import text
import os


# # Etape 1 : Export des données sous S3
# 
# On va stocker toutes nos données dans un fichier .csv sur un datalake (S3).
# 
# Un datalake est globalement un espace de stockage de données brutes (données structurées ou non structurées) qui peuvent provenir de sources différentes. Les datalakes sont régis par des règles ELT (Extract Load Transform). C'est à dire que les données sont stockées avant d'éventuelles transformations pour usage (dashboard, analyses...). Le datalake est orienté pour la data science. 

# In[ ]:


# Importation des données 

table_hotels = pd.read_csv('PATH/table_hotel_booking.csv')
liste_villes = pd.read_csv('PATH/table_villes_coord.csv')
data_meteo = pd.read_csv('PATH/data_meteo.csv')

# Traitement des coordonées GPS des hotels

table_hotels['H_lat'] = 0
table_hotels['H_lon'] = 0

for i in range(len(table_hotels)) : 
    table_hotels['H_lat'][i] = float(table_hotels['latlong'].iloc(axis = 0)[i][table_hotels['latlong'].iloc(axis = 0)[i].index("['")+ 2: table_hotels['latlong'].iloc(axis = 0)[i].index(",")])
    table_hotels['H_lon'][i] = float(table_hotels['latlong'].iloc(axis = 0)[i][table_hotels['latlong'].iloc(axis = 0)[i].index(",") + 1: table_hotels['latlong'].iloc(axis = 0)[i].index("']")])

# Merging des 3 données en 1 seule 

data = pd.merge(liste_villes, table_hotels, on = 'city')
data = pd.merge(data, data_meteo, on = 'city')

# Stockage des données dans un fichier .csv

csv = data.to_csv()


# In[ ]:


# Connexion à AWS

session = boto3.Session(aws_access_key_id = "YOUR_ACCESS_KEY", # Rempacer par votre key_id
                        aws_secret_access_key = "YOUR_SECRET_ACCESS_KEY") # Rempacer par votre mot de passe

s3 = session.resource("s3")

# Création du Bucket

bucket =s3.create_bucket(Bucket = "citiesandhotels2022") # Le nom doit être unique - A updater

# Import du CSV dans le bucket créé

put_object = bucket.put_object(Key = "villes_et_hotels.csv", Body = csv)

# Verification du contenu du bucket

all_files = [obj.key for obj in bucket.objects.all()]
all_files


# # Etape 2 : Extract, Transform and Load (ETL)
# 
# On va ensuite pouvoir passer du datalake au data warehouse.
# 
# Un entrepôt de données rassemble des données pré-traitées / nettoyées et les stocke de manière structurée. De fait, les entrepôts sont régis par des règles ETL (Extract Transform Load). C'est à dire que les données sont transformées avant le stockage. Les entrepôts sont orientés pour les business decisions. 

# On va donc créer une base de données SQL (structurée) à l'aide de AWS RDS dans laquelle on va venir stocker les données. 

# In[ ]:


# Récupérer l'objet S3 

obj = s3.get_object(
    Bucket = 'citiesandhotels2022',
    Key = 'villes_et_hotels.csv')
    
data = pd.read_csv(obj['Body'])

# Connexion à AWS : Remplacer USERNAME, PASSWORD et HOSTNAME par vos informations de connexion

engine = create_engine("postgresql+psycopg2://USERNAME:PASSWORD@HOSTNAME/postgres", echo = True)
conn = engine.connect()

# Passer la base de données à une base sql

data.to_sql("villes_et_hotels", con = engine)

# Lecture de la base SQL

pd.read_sql(text(" SELECT * FROM villes_et_hotels "), con = engine)

