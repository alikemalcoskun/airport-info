from model import airportData
from urllib import response
import requests
import json
from dotenv import load_dotenv
import os
from fastapi import HTTPException


load_dotenv()
AIRPORTDB_API_KEY = os.getenv('AIRPORTDB_API_KEY')


def getAirportInfo(icao, username):
    
    url = 'https://airportdb.io/api/v1/airport/{}?apiToken={}'.format(icao, AIRPORTDB_API_KEY)
    response = requests.get(url)
    if not response: raise HTTPException(status_code=404, detail=f"Cannot connect to API.")
    data = response.json()
    result = airportData(user=username,
    icao=data['icao_code'], 
    iata=data['iata_code'], 
    name=data['name'],
    type=data['type'],
    country=data['iso_country'],
    continent=data['continent'],
    wikipedia=data['wikipedia_link'],
    website=data['home_link'])
    return result