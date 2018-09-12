import requests
import re
import json
import sys
import time
import folium
import pandas as pd
from random import randint

###

def Data():
    '''
    Gets data from accuweather for each country and stores it in the data dictionary, which is later stored as a json file.
    The data dictionary is not passed, but rather saved in a file for investigation purposes.
    '''
    data = {}

    customHeaders = {'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}

    try:
        site = requests.get('https://www.accuweather.com/en/browse-locations/eur', headers = customHeaders, timeout = 10)
    except requests.exceptions.Timeout:
        print('Timeout occurred when requesting for https://www.accuweather.com!')
        sys.exit(1)
    
    if site.status_code != 200:
        print('Status code ' + str(site.status_code) + ' when requesting for https://www.accuweather.com')
    
    countries = re.findall('href="https://www.accuweather.com/en/browse-locations/eur/(.*)"><em>(.*)</em>', site.text)

    for country, _ in countries:
        print('Getting data for', country)
        site = requests.get(f'https://www.accuweather.com/en/browse-locations/eur/{country}', headers = customHeaders)
        
        # choose a random region
        regions = re.findall(f'href="https://www.accuweather.com/en/browse-locations/eur/{country}/(.*)"><em>(.*)</em>', site.text)
        regionIndex, region = regions[randint(0, len(regions) - 1)]

        site = requests.get(f'https://www.accuweather.com/en/browse-locations/eur/{country}/{regionIndex}', headers = customHeaders)

        # choose a random city
        cities = re.findall(f'href="https://www.accuweather.com/en/{country}/(.*)/(.*)/weather-forecast/(.*)"><em>(.*)</em>', site.text)
        city, cityID, _, _ = cities[randint(0, len(cities) - 1)]
        
        data[country] = {}
        for monthIndex in range(1, 13):
            site = requests.get(f'https://www.accuweather.com/en/{country}/{city}/{cityID}/month/{cityID}?monyr={monthIndex}/01/2018', headers = customHeaders)

            # find temperatures
            regexPattern = '<h3 class="date">[a-zA-Z]{3} (.*)</h3>[\sa-zA-Z\<\>\"\=0-9\\\/]*class="large-temp">(.*)&#176;</span>[\s]*<span class="small-temp">/(.*)&#176;</span>'
            temps = re.findall(regexPattern, site.text)
            
            strStart = str(monthIndex) + '/'
            data[country][monthIndex] = []

            for date, maxTemp, minTemp in temps:
                if date[0 : len(strStart)] == strStart:
                    data[country][monthIndex].append(
                        {
                            'day' : date[len(strStart) : ],
                            'max' : maxTemp,
                            'min' : minTemp
                        }
                    )

        # wait 5s between each country
        time.sleep(5)
    
    # write data
    with open('data.json', 'w') as fout:
        json.dump(data, fout)

def Values():
    '''
    Builds the values dictionary, which will be plotted on the map. 
    '''
    values = {}

    with open('data.json') as fin:  
        data = json.load(fin)
    
    for country in data.keys():
        monthCounter = 0
        monthValue = 0

        for month in data[country]:
            maxTempPerMonth = 0
            minTempPerMonth = 0
            daysCounter = 0

            for vals in data[country][month]:
                maxTempPerMonth += int(vals['max'])
                minTempPerMonth += int(vals['min'])
                daysCounter += 1

            if daysCounter != 0:
                monthValue += (maxTempPerMonth / daysCounter)
                monthCounter += 1
        
        if monthCounter != 0:
            values[country.upper()] = monthValue / monthCounter
        else:
            print('No data for', country)
            values[country.upper()] = 0

    return values

def Map():
    '''
    Plots the map.
    '''
    m = folium.Map(location=[55.79, 9.70], zoom_start = 4)

    m.choropleth(
        geo_data = 'europe.geojson',
        name = 'choropleth',
        data = pd.Series(Values()),
        key_on = 'feature.properties.ISO2',
        fill_color = 'OrRd',
        legend_name = 'Average max temperatures',
        highlight = True
    )
    folium.LayerControl().add_to(m)

    m.save('map.html')

if __name__ == '__main__':
    Data()
    Map()