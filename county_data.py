#!/usr/bin/python3
"""Script for fetching the coordinates of the listed towns. From these
coordinates the distance matrix can then be calculated."""

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import numpy as np

import time
import pickle
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
TOWN_NAMES: [%(TOWN_NAMES)s]
DIST_MATRIX: [
%(DIST_MATRIX)s];
"""
URL_TOWN_TEMPLATE = (
  "http://maps.googleapis.com/maps/api/geocode/json?address=%s+Ireland")

TownCoordinates = namedtuple('TownCoordinates', ['town', 'lat', 'lng'])

COORDINATES_FILENAME = 'coordinates.pickle'

def get_coordinate_data():
  """Fetch the coordinate data.

  Retrieves pickled data if available. If not queries Google Maps API. In the
  latter case it also saves it as a pickle to prevent the need to query the API
  in the future.
  """
  coordinates = load_coordinates()
  print(len(coordinates))
  if len(coordinates) == 0:
    # We have no coordinates
    for town in COUNTY_TOWNS:
      response = request.urlopen(URL_TOWN_TEMPLATE % town)
      data = json.loads(response.read().decode('utf-8'))
      while data['status'] != 'OK':
        # In case of throttling. API has a 50 query per second limit.
        time.sleep(10)
        response = request.urlopen(URL_TOWN_TEMPLATE % town)
        data = json.loads(response.read().decode('utf-8'))
      results = data.get('results')
      coordinates.append(TownCoordinates(
        town, **results[0].get('geometry').get('location')))
    save_coordinates(coordinates)
  return coordinates


def load_coordinates():
  """Attempt to load the pickled town data.

  Returns:
    Either a list of town named tuples or an empty list.
  """
  try:
    with open(COORDINATES_FILENAME, 'rb') as fp:
      return pickle.load(fp)
  except FileNotFoundError:
    return []


def save_coordinates(coordinates):
  """Write the pickled town data to a file."""
  with open(COORDINATES_FILENAME, 'wb') as fp:
    pickle.dump(coordinates, fp)


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


def generate_distance_matrix(coordinates):
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

def get_bounds(coordinates):
  lat_lower = min([point.lat for point in coordinates]) * 0.99
  lat_upper = max([point.lat for point in coordinates]) * 1.01

  lng_lower = min([point.lng for point in coordinates]) * 1.1
  lng_upper = max([point.lng for point in coordinates]) * 0.9

  return (lat_lower, lat_upper, lng_lower, lng_upper)


def plot_map(coordinates):
  """Plot on map.

  Inspired by the example at:
  https://peak5390.wordpress.com/2012/12/08/matplotlib-basemap-tutorial-plotting-points-on-a-simple-map/
  """
  lat_lower, lat_upper, lng_lower, lng_upper = get_bounds(coordinates)
  lat_0 = (lat_lower + lat_upper)/2
  lng_0 = (lng_lower + lng_upper)/2
  map = Basemap(projection='merc', lat_0 = lat_0, lon_0 = lng_0,
                resolution = 'h', area_thresh = 0.1,
                llcrnrlon=lng_lower, llcrnrlat=lat_lower,
                urcrnrlon=lng_upper, urcrnrlat=lat_upper)

  map.drawcoastlines()
  map.drawcountries()
  map.fillcontinents(color = 'orange')
  map.drawmapboundary()

  lons = [point.lng for point in coordinates]
  lats = [point.lat for point in coordinates]
  x,y = map(lons, lats)
  map.plot(x, y, 'bo', markersize=12)

  #TODO(max): Fix labelling.
  for point in coordinates:
    plt.text(point.lng, point.lat, point.town)

  plt.show()


if __name__ == "__main__":
  coordinates = get_coordinate_data()
  print(coordinates)
  dist_matrix = generate_distance_matrix(coordinates)
  # Simply printing output. Use UNIX > to pipe output into a file.
  print(populate_dat_file(coordinates, dist_matrix))
  plot_map(coordinates)
