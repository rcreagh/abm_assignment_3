#!/usr/bin/python3
"""Script for fetching the coordinates of the listed towns. From these
coordinates the distance matrix can then be calculated."""

import math
from  urllib import request
import json
from collections import namedtuple

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
  "Dublin",
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

DAT_FILE_TEMPLATE = """
! Data file for `tsp.mos'
! data rigged to demonstrate violated sub-tour

N_COUNTIES: %(N_COUNTIES)s
TOWN_NAMES: [%(TOWN_NAMES)s];
DIST_MATRIX: [
%(DIST_MATRIX)s];
"""
URL_TOWN_TEMPLATE = (
  "http://maps.googleapis.com/maps/api/geocode/json?address=%s+Ireland")

TownCoordinates = namedtuple('TownCoordinates', ['town', 'lat', 'lng'])


def get_coordinate_data():
  coordinates = []
  for town in COUNTY_TOWNS:
    response = request.urlopen(URL_TOWN_TEMPLATE % town)
    data = json.loads(response.read().decode('utf-8'))
    results = data.get('results')
    coordinates.append(TownCoordinates(
      town, **results[0].get('geometry').get('location')))
  return coordinates


def haversine(point_1, point_2):
  """Compute distance between two points using Haversine algoithm
     Adapted from: http://stackoverflow.com/questions/365826/calculate-distance-between-2-gps-coordinates
  """
  lat1 = float(point_1.lat)
  lng1 = float(point_1.lng)
  lat2 = float(point_2.lat)
  lng2 = float(point_2.lng)

  degree_to_rad = float(math.pi / 180.0)

  d_lat = (lat2 - lat1) * degree_to_rad
  d_lng = (lng2 - lng1) * degree_to_rad

  a = (pow(math.sin(d_lat / 2), 2) + math.cos(lat1 * degree_to_rad) *
       math.cos(lat2 * degree_to_rad) * pow(math.sin(d_lng / 2), 2))
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
  km = 6367 * c

  return km


def generate_distance_matrix(cooridantes):
  matrix = []
  for index_1, point_1 in enumerate(coordinates):
    row = []
    for index_2, point_2 in enumerate(coordinates):
      # Rounding to 2 decimal places.
      dist = round(haversine(point_1, point_2), 2)
      row.append(dist)
    matrix.append(row)
  return(matrix)


def populate_dat_file(coordinates, dist_matrix):
  n_counties = len(coordinates)
  string_mat = ''
  for row in dist_matrix:
    fixed_row = ' '.join(str(elem) for elem in row)
    string_mat = string_mat + fixed_row + '\n'
  return DAT_FILE_TEMPLATE % {
      'TOWN_NAMES': ' '.join(['"%s"' % town for town in COUNTY_TOWNS]),
      'DIST_MATRIX': string_mat,
      'N_COUNTIES': n_counties}


if __name__ == "__main__":
  coordinates = get_coordinate_data()
  dist_matrix = generate_distance_matrix(coordinates)
  # Simply printing output. Use UNIX > to pipe output into a file.
  print(populate_dat_file(coordinates, dist_matrix))

