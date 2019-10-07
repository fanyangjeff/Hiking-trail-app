import urllib.request
import requests
from bs4 import BeautifulSoup
import lxml
import json
import sqlite3
import csv
import re
import math

# Additional code for running GUI application on Mac
# these modules and the code below will be covered in module 4
import sys
import os


def gui2fg():
    """Brings tkinter GUI to foreground on Mac
    Call gui2fg() after creating main window and before mainloop() start
    """
    if sys.platform == 'darwin':
        tmpl = 'tell application "System Events" to set frontmost of every process whose unix id is %d to true'
        os.system("/usr/bin/osascript -e '%s'" % (tmpl % os.getpid()))


CITY_FILENAME = "/Users/yf/Downloads/BayAreaCities.csv"
DB_FILENAME = "trails.db"

conn = sqlite3.connect(DB_FILENAME)
cur = conn.cursor()


def createCityTable():
    cur.execute("DROP TABLE IF EXISTS CITY")
    cur.execute('''CREATE TABLE CITY(  
                       ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       NAME TEXT UNIQUE ON CONFLICT IGNORE,
                       TYPE TEXT,
                       COUNTY TEXT,
                       POPULATION_2010 INTEGER,
                       SQ_MI REAL,
                       SQ_KM REAL)''')


def insertCityData():
    try:
        # open file for reading
        with open(CITY_FILENAME) as fh:
            reader = csv.reader(fh)  # reader object is an iterator
            next(reader)  # Skips the header row
            # cur.execute('''INSERT INTO CITYS (NAME, TYPE, COUNTY, POPULATION_2010, SQ_MI, SQ_KM) VALUES(?,?,?,?,?,?)''', ('Alameda','City','Alameda', 73812, 10.61,27.5,) )

            for row in reader:  # each row is a list of fields in a line
                # print(row[0], row[1], row[2], row[3], row[4], row[5])    # print the first and last fields

                cur.execute(
                    '''INSERT INTO CITY (NAME, TYPE, COUNTY, POPULATION_2010, SQ_MI, SQ_KM) VALUES(?,?,?,?,?,?)'''
                    , (row[0], row[1], row[2], row[3], row[4], row[5],))
                print("completed:", row[0])

            conn.commit()

    # Prints error messages and exit program
    except FileNotFoundError:
        raise SystemExit(CITY_FILENAME, "is not found. Terminating Program")
    except ValueError:
        print(CITY_FILENAME, "is empty. Terminating Program")
        raise SystemExit

    except IOError:
        print("Can't open file", CITY_FILENAME, ". Terminating program")
        raise SystemExit


def findLatLong(city):
    url = (
                'https://maps.googleapis.com/maps/api/geocode/json?address=' + city + ',CA&key=AIzaSyASyM3IdilzuHe_6lbDBpC7L1WDkuWCres')
    page = urllib.request.urlopen(url)
    data = json.load(page)

    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']

    return lat, lng


def createHikingTables():
    """
    Create database file called movies.db.
    Create 2 tables Movies and Genre and insert into the tables movie name, release dates, genre and star rating.
    """

    cur.execute("DROP TABLE IF EXISTS TYPE")
    cur.execute('''CREATE TABLE TYPE(             
                       ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       TRAIL_TYPE TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS DIFFICULTY")
    cur.execute('''CREATE TABLE DIFFICULTY(             
                       ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       DIFF_LEVEL TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS LOCATION")
    cur.execute('''CREATE TABLE LOCATION(             
                       ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       LOC TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS CONDITION")
    cur.execute('''CREATE TABLE CONDITION(             
                       ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       COND_STATUS TEXT UNIQUE ON CONFLICT IGNORE)''')

    cur.execute("DROP TABLE IF EXISTS TRAIL")
    cur.execute('''CREATE TABLE TRAIL(  
                       ID INTEGER NOT NULL PRIMARY KEY UNIQUE,
                       TRAILID INTEGER UNIQUE ON CONFLICT IGNORE,
                       TYPE_ID INTEGER,
                       NAME TEXT,
                       DIFF_ID INTEGER,
                       LOC_ID INTEGER,
                       SUMMARY TEXT,
                       STARS REAL,
                       STARVOTES INTEGER,
                       URL TEXT,
                       LENGTH REAL,
                       HIGH INTEGER,
                       LOW INTEGER,
                       LONGITUDE REAL,
                       LATITUDE REAL,
                       CONDSTAT_ID INTEGER,
                       COND_DATE TEXT,
                       CITY_ID INTEGER)''')


def insertHikingData(city, lat, lng, dist):
    hikingurl = 'https://www.hikingproject.com/data/get-trails?lat=' + str(lat) + '&lon=' + str(
        lng) + '&maxDistance=' + str(dist) + '&key=200392139-ae0b007a125d0284aaf36fd7a5ec783b'

    hikingpage = urllib.request.urlopen(hikingurl)
    hikingdata = json.load(hikingpage)

    print(hikingdata, '\n')

    for data in hikingdata['trails']:
        trailId = data['id']
        trailType = data['type']
        name = data['name']
        difficulty = data['difficulty']
        location = data['location']
        summary = data['summary']
        stars = data['stars']
        starVotes = data['starVotes']
        url = data['url']
        length = data['length']
        high = data['high']
        low = data['low']
        long = data['longitude']
        lat = data['latitude']
        condStatus = data['conditionStatus']
        condDate = data['conditionDate']

        cur.execute('''INSERT INTO TYPE (TRAIL_TYPE) VALUES (?)''', (trailType,))
        cur.execute('SELECT id FROM TYPE WHERE TRAIL_TYPE = ? ', (trailType,))
        type_id = cur.fetchone()[0]

        cur.execute('''INSERT INTO DIFFICULTY (DIFF_LEVEL) VALUES (?)''', (difficulty,))
        cur.execute('SELECT id FROM DIFFICULTY WHERE DIFF_LEVEL = ? ', (difficulty,))
        diff_id = cur.fetchone()[0]

        cur.execute('''INSERT INTO LOCATION (LOC) VALUES (?)''', (location,))
        cur.execute('SELECT id FROM LOCATION WHERE LOC = ? ', (location,))
        loc_id = cur.fetchone()[0]

        cur.execute('''INSERT INTO CONDITION (COND_STATUS) VALUES (?)''', (condStatus,))
        cur.execute('SELECT id FROM CONDITION WHERE COND_STATUS = ? ', (condStatus,))
        condstat_id = cur.fetchone()[0]

        cur.execute('SELECT id FROM CITY WHERE NAME = ? ', (city,))
        city_id = cur.fetchone()[0]

        cur.execute('''INSERT INTO TRAIL (TRAILID, TYPE_ID, NAME, DIFF_ID, LOC_ID, SUMMARY, STARS, STARVOTES, URL, 
                       LENGTH, HIGH, LOW, LONGITUDE, LATITUDE, CONDSTAT_ID, COND_DATE, CITY_ID) 
                       VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'''
                    , (trailId, type_id, name, diff_id, loc_id, summary, stars, starVotes, url, length, high, low, long,
                       lat, condstat_id, condDate, city_id,))
    conn.commit()


def main():
    createCityTable()
    insertCityData()

    createHikingTables()

    # Use the city name and area data from the CITY table to find and insert all Hiking Trails in the Bay Area
    cur.execute("SELECT NAME, SQ_MI FROM CITY")
    numOfCity = 1
    for record in cur.fetchall():
        city = record[0]
        area = record[1]
        # print(city, area)

        # use re.sub to replace to remove all spaces, if exist in city name
        cityNoSpace = re.sub(' ', '', city)
        # print("no space:"  , cityNoSpace)

        # calculate the radius for the city based on city sq miles (area)
        radius = math.sqrt(area / math.pi)
        # print("radius:", radius)

        # find the latitude and longitude of the city (api expect the city with no space)
        # if (not cityNoSpace in ('AmericanCanyon','CorteMadera') ):
        (latitude, longitude) = findLatLong(cityNoSpace)

        print(numOfCity, cityNoSpace, radius, latitude, longitude)
        numOfCity += 1

        insertHikingData(city, lat=latitude, lng=longitude, dist=radius)

    conn.close()


main()