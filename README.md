# 
## 1. Présentation du projet 

### Cadre général 

Kayak est un moteur de recherche qui aide les utilisateurs à planifier leur voyage à meilleur prix. La société a été fondée en 2004 par Steve Hafner & Paul English. Kayak a par la suite était acquise par Booking qui regroupe à présent plsuieurs entités : Booking.com, Kayak, Priceline, Agoda, RentalCars & OpenTable. 

Avec plus de 300 millions de dollars de revenu annuel, Kayal est présent dans la plupart des pays, et dans la plupart des langues pour permettre à ses utilisateurs de voyager partout autour du monde. 

### Le projet 

L'équipe Marketing a besoin d'aide pour son prochain projet. Après ses recherches, il est apparu que 70% des utilisateurs souhaiteraient avoir plus d'informations sur la destination envisagée. De plus, les personnes semblent méfiantes quant aux informations qu'elles lisent si l'auteur du contenu n'est pas connu. 
Forte de ces nouveaux insigths, l'équipe Marketing souhaiterait créer une application qui pourrait recommander où aller en fonction de la météo actuelle et des hotels disponibles dans la région. 
L'application devrait permettre de recommander les meilleurs destinations selon ces 2 variables à n'importe quel moment. 

----

## 2. Objectifs 

Comme étape préliminaire à ce projet, il est demandé de : 

  * Scraper les données sur les destinations
  * Scraper les données météorologiques relatives à ces destinations
  * Scraper les informations des hôtels présents dans ces destinations 
  * Proposer deux premières cartographies 
    * Classement des destinations selon la météo à venir
    * Classement des hôtels dans une destination 

----

## 3. Comment procéder ?

### Pré-requis

Les librairies suivantes sont nécessaires : 
  * re  
  * unidecode
  * bs4 
  * requests
  * math 
  * pandas 
  * json
  * plotly
  * datetime 
  * os 
  * logging
  * scrapy
  * folium
  * pyproj 
  * matplotlib
  * colour 
  * turtle 
  * IPython

### Les fichiers

Les notebooks peuvent s'utiliser les uns à la suite des autres ou indépendamment puisque les données générées par chaque notebook sont fournies dans les fichiers csv. 

  * **Etape 1 - Infos des hotels.ipynb** fournit le scraping de Booking.com selon 2 méthodes : 
    * Utilisation de SCRAPY -> table_hotels_scrapy.csv
    * Utilisation de BEAUTIFULSOUP -> table_hotels_BS.csv
  * **Etape 2 - Données Météo.ipynb** prend en input table_hotels_scrapy.csv ou table_hotels_BS.csv et fournit les données météorologiques
    * Coordonnées GPS des villes : table_villes_coord.csv
    * Météo d'aujourd'hui et des 7 prochains jours : data_meteo.csv
  * **Etape 3 - Cartographies.ipynb** prend en input les 3 fichiers csv (hotels, coord et meteo)
  * **Etape 4 - ETL.ipynb** prend en input les 3 fichiers csv (hotels, coord et meteo)

----

## 4. Overview des principaux résultats

### Classement des villes selon la météo à venir - PLOTLY

![image](https://user-images.githubusercontent.com/38078432/185938879-5c58982c-8cba-42a2-929d-bd354d5e131e.png)

### Classement des hôtels de la destination choisie selon les évaluations des utilisateurs de Booking.com - PLOTLY

![image](https://user-images.githubusercontent.com/38078432/185939372-e02d4dcd-254f-40d9-8ce4-9a48f8da9828.png)

----

## 5. Informations

### Outils

Les notebooks ont été développés avec [Visual Studio Code](https://code.visualstudio.com/). 
La partie ETL fonctionne avec un compte AWS (payant). 

### Auteurs & contributeurs

Auteur : 
  * Helene alias [@Bebock](https://github.com/Bebock)

La dream team :
  * Henri alias 
  * Jean alias
  * Nicolas alias 
  
### Sites sources des données

Informations des hôtels : www.booking.com

Coordonnées GPS : https://nominatim.org/ (Documentation : https://nominatim.org/release-docs/develop/api/Search/)

Données météorologiques : https://openweathermap.org/appid (inscription gratuite pour une utilisation limitée)


----
