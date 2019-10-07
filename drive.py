import urllib.request
from bs4 import BeautifulSoup
import lxml
import json
from collections import defaultdict
import multiprocessing as mp

def getData(outputQ, e):
    url = ('https://maps.googleapis.com/maps/api/geocode/json?address=Denver,+CA&key=AIzaSyASyM3IdilzuHe_6lbDBpC7L1WDkuWCres')
    page = urllib.request.urlopen(url)
    location_data = json.load(page)

    lat = location_data['results'][0]['geometry']['location']['lat']
    lng = location_data['results'][0]['geometry']['location']['lng']
    '''
    
    '''

    hikingurl = 'https://www.hikingproject.com/data/get-trails?lat=' + str(lat) + '&lon=' + str(lng) + '&maxDistance=10&key=200392139-ae0b007a125d0284aaf36fd7a5ec783b'

    hikingpage = urllib.request.urlopen(hikingurl)
    hikingdata = json.load(hikingpage)

    hiking_dict = defaultdict(list)

    e.set()
    for data in hikingdata['trails']:
        hiking_dict[data['name']].append(data['stars'])
        hiking_dict[data['name']].append(data['difficulty'])
        hiking_dict[data['name']].append(data['length'])
        hiking_dict[data['name']].append(data['summary'])
        hiking_dict[data['name']].append(data['location'])
        hiking_dict[data['name']].append(data['conditionStatus'])
        hiking_dict[data['name']].append(data['conditionDate'])
        hiking_dict[data['name']].append(data['high'])
        hiking_dict[data['name']].append(data['low'])
        hiking_dict[data['name']].append(data['type'])
        hiking_dict[data['name']].append(data['id'])
        hiking_dict[data['name']].append(data['type'])
        hiking_dict[data['name']].append(data['starVotes'])
        hiking_dict[data['name']].append(data['url'])
        hiking_dict[data['name']].append(data['longitude'])
        hiking_dict[data['name']].append(data['latitude'])

        temp_tuple = (data['name'], hiking_dict[data['name']])
        outputQ.put(temp_tuple)


    e.clear()

if __name__ == '__main__':
    '''
    outputQ = mp.Queue()
    e = mp.Event()

    p = mp.Process(target = getData, args = (outputQ, e, ))
    p.start()

    e.wait()

    while e.is_set() or (not outputQ.empty()):
        print(outputQ.get())
    '''

    s = 'Located less than two miles from the heart of downtown Denver, hiking this trail feels like an outing in the country.'
    print(len(s))

    if len(s) > 90:
        position = s.find(' ', len(s)//2)
        newstring = s[0: position] + '\n' + s[position + 1: ]

    print(newstring)
