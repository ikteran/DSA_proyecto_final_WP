# Librerias
import pandas as pd
from IPython.display import display
import folium
from folium.plugins import HeatMap
import matplotlib.pyplot as plt
import seaborn as sns
import missingno as msno

# Cargue de los datos
def prueba():
  print('probando')

def clean_df():
  url = '../data/RTOP.csv'
  df = pd.read_csv(url, encoding='ISO-8859-1')

  df=df.rename(columns={'Ship ID - Ship Classification':'Vessel Type','Ship - Name':'Ship Name'})

  #Evaluacion de los datos
  print(df.info())

  print(df.isnull().sum())

  print(msno.matrix(df))

  #Limpieza de los datos
  df_clean=df[['Ship Name','Vessel Type','Country','Location','Arrival','Departure','Region Name','Status']]
  df_clean = df_clean.dropna(subset=['Arrival','Departure','Ship Name','Location','Vessel Type','Status'])
  df_clean = df_clean[df_clean['Status'] != 'Cancelled']
  # Convertir las columnas 'Arrival' y 'Departure' a datetime
  df_clean['Arrival'] = pd.to_datetime(df_clean['Arrival'], errors='coerce')
  df_clean['Departure'] = pd.to_datetime(df_clean['Departure'], errors='coerce')
  df_clean['Duration'] = (df_clean['Departure'] - df_clean['Arrival']).dt.days
  # Filtrar las filas donde 'Duration' sea menor o igual a 60 días
  df_clean = df_clean[(df_clean['Duration'] <= 60) & (df_clean['Duration'] >= 0)]

  return df_clean