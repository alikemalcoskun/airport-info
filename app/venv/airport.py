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
    return airportData(icao="LTFM", iata="IST", name="Istanbul Airport", user=username)
    
    url = 'https://airportdb.io/api/v1/airport/{ICAO}?apiToken={apiToken}'.format(icao, AIRPORTDB_API_KEY)
    response = requests.get(url)
    if not response: raise HTTPException(status_code=404, detail=f"Cannot connect to API.")
    data = response.json()
    result = airportData(icao=data['icao'], 
    iata=data['iata'], 
    name=data['name'],)
    """
    type=data['type'],
    country=data['country']
    continent=data['continent'],
    wikipedia=data['wikipedia'],
    website=data['website'])
    """
    return result