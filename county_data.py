#!/usr/bin/python3
"""Script for fetching the coordinates of the listed towns. From these
coordinates the distance matrix can then be calculated."""

from  urllib import request
import json

# Keep sorted.
COUNTY_TOWNS = [
  "Armagh",
  "Ballymena",
  "Carlow",
  "Carrick-on-Shannon",
  "Castlebar",
  "Cavan",
  "Coleraine",
  "Cork",
  "Downpatrick",
  "Dundalk",
  "Dungarvan",
  "Ennis",
  "Enniskillen",
  "Galway",
  "Kilkenny",
  "Lifford",
  "Limerick",
  "Longford",
  "Monaghan",
  "Mullingar",
  "Naas",
  "Navan",
  "Nenagh",
  "Omagh",
  "Portlaoise",
  "Roscommon",
  "Sligo",
  "Swords",
  "Tralee",
  "Tullamore",
  "Wexford",
  "Wicklow"
]

URL_TOWN_TEMPLATE = (
  "http://maps.googleapis.com/maps/api/geocode/json?address=%s+Ireland")


def get_coordinates():
  county_info = {}
  for town in COUNTY_TOWNS:
    response = request.urlopen(URL_TOWN_TEMPLATE % town)
    data = json.loads(response.read().decode('utf-8'))
    print(data)


if __name__ == "__main__":
  get_coordinates()
