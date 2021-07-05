from bs4 import BeautifulSoup as bs
import requests
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def owned_cat_per_country():
    website = requests.get("http://carocat.eu/statistics-on-cats-and-dogs/")
    soup = bs(website.text, "html.parser")
    list = soup.find("table", {"width":"561"}).find_all("tr")
    countries = []
    number_of_cats = []
    for info in list[2:]:
        inner = info.find_all("td")
        countries.append(inner[0].p.text.strip("\n"))
        number_of_cats.append(int(inner[1].p.text.strip("\n\t").replace(',', '')))

    return countries, number_of_cats


# some countries have second name with paranthesis so this regex process is for removing it from raw name
def edit_country_name(name):
    return re.sub(r'\([^)]*\)', "", name).rstrip()

def concat_with_population(countries):
    website = requests.get("https://www.worldometers.info/world-population/population-by-country/")
    soup = bs(website.text, "html.parser")
    list = soup.find("table", id="example2").tbody.find_all("tr")
    all_countries_on_population_info = []
    
    for country in list:        
        country_name = edit_country_name(country.a.text)
        all_countries_on_population_info.append(country_name)

    commons = intersection(countries, all_countries_on_population_info)
    populations = [0] * len(commons)

    for country in list:
        country_name = edit_country_name(country.a.text)
        if (country_name in commons):
            print(commons.index(country_name))
            populations[commons.index(country_name)] = int(country.find("td", {"style":"font-weight: bold;"}).text.replace(',', ''))

    return populations


def concat_with_welfare_index(countries):
    website = requests.get("https://en.wikipedia.org/wiki/Social_Progress_Index")
    soup = bs(website.text, "html.parser")
    list = soup.find("table", class_="wikitable sortable").tbody.find_all("tr")
    all_countries_on_welfare_info = []
    for country in list[2:]:
        country_name = edit_country_name(country.a.text)
        all_countries_on_welfare_info.append(country_name)
    
    commons = intersection(countries, all_countries_on_welfare_info)
    indexes = [0] * len(commons)

    for country in list[2:]:
        country_name = edit_country_name(country.a.text)
        if (country_name in commons):
            indexes[commons.index(country_name)] = float(country.find_all('td')[2].text.strip('\n'))

    return indexes

# cancel
# def search_and_get_index(name, countries):
#     return list(filter(lambda info: info["Country"] == name, countries))

def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


def main():
    countries, number_of_cats = owned_cat_per_country()
    populations = concat_with_population(countries)
    indexes = concat_with_welfare_index(countries)
    labels = ['Country', 'Number of Owned Cats', 'Population', 'Social Progress Index']
    columns = [countries, number_of_cats, populations, indexes]
    df = pd.DataFrame(dict(list(zip(labels, columns))))
    df['Cat Density by Population'] = df['Population'] / df['Number of Owned Cats']
    x = df['Cat Density by Population']
    y = df['Social Progress Index']
    print(x.corr(y))
    
    figure, axis = plt.subplots(2)


    axis[0].scatter(x,y)
    axis[0].plot(np.unique(x), np.poly1d(np.polyfit(x,y,1))(np.unique(x)), color='red')
    axis[0].set_title('CORRELATION')
    axis[0].set(xlabel='Density', ylabel='Social Progess Index')

    axis[1].plot(df['Country'], df['Cat Density by Population'])
    axis[1].plot(df['Country'], df['Social Progress Index'])
    axis[1].set_ylabel('Index and Owned Cat Density')
    axis[1].tick_params(axis='both', which='major', labelsize=8)
    plt.title('THE RELATIONSHIP BETWEEN THE SOCIAL PROGESS INDEX AND THE DENSITY OF CAT OWNERS')
    plt.xticks(rotation=90)
    plt.show()


main()