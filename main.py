import requests
import re
import json
import sys
import time

###

def data():
    data = {}

    customHeaders = {'user-agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}

    site = requests.get('https://www.accuweather.com/en/browse-locations/eur', headers = customHeaders)
    
    countries = re.findall('href="https://www.accuweather.com/en/browse-locations/eur/(.*)"><em>(.*)</em>', site.text)

    for country, _ in countries:
        print('Country is', country)
        site = requests.get(f'https://www.accuweather.com/en/browse-locations/eur/{country}', headers = customHeaders)
        
        # choose region
        regions = re.findall(f'href="https://www.accuweather.com/en/browse-locations/eur/{country}/(.*)"><em>(.*)</em>', site.text)
        
        '''
        for number, reg in regions:
            if reg == region:
                regionIndex = number
                break
        '''
        regionIndex, region = regions[0]

        site = requests.get(f'https://www.accuweather.com/en/browse-locations/eur/{country}/{regionIndex}', headers = customHeaders)

        cities = re.findall(f'href="https://www.accuweather.com/en/{country}/(.*)/(.*)/weather-forecast/(.*)"><em>(.*)</em>', site.text)

        # choose city
        '''
        city = 'agim'
        for cityName, cityID, _, _ in cities:
            if cityName == city:
                ID = cityID
                break
        '''
        # first city
        city, cityID, _, _ = cities[0]
        
        data[country] = {}
        for monthIndex in range(1, 13):
            print('###', monthIndex)
            site = requests.get(f'https://www.accuweather.com/en/{country}/{city}/{cityID}/month/{cityID}?monyr={monthIndex}/01/2018', headers = customHeaders)

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
        time.sleep(5)
    
    with open('data.json', 'w') as fout:
        json.dump(data, fout)



if __name__ == '__main__':
    data()