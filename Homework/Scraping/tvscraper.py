#!/usr/bin/env python
# Name: Mick Roché
# Student number: 10739416
"""
This script scrapes IMDB and outputs a CSV file with highest rated tv series.
"""

import csv
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

TARGET_URL = "http://www.imdb.com/search/title?num_votes=5000,&sort=user_rating,desc&start=1&title_type=tv_series"
BACKUP_HTML = 'tvseries.html'
OUTPUT_CSV = 'tvseries.csv'


def extract_tvseries(dom):
    """
    Extract a list of highest rated TV series from DOM (of IMDB page).
    Each TV series entry should contain the following fields:
    - TV Title
    - Rating
    - Genres (comma separated if more than one)
    - Actors/actresses (comma separated if more than one)
    - Runtime (only a number!)
    """

    # opening the url, offload it to variable
    Client = urlopen(TARGET_URL)
    page_html = Client.read()
    Client.close()

    # parse the html
    page_soup = BeautifulSoup(page_html, "html.parser")

    # get each serie
    items = page_soup.findAll("div",{"class":"lister-item-content"})

    # loop for every item on page
    tvseries = []
    for item in items:

        # get title
        title = item.a.text         
                
        # get rating
        rating = item.strong.text
        
        # get genres
        genre = item.find("span",{"class":"genre"}).text.strip()

        # get actors
        actor_html = item.findAll("a", href=re.compile("name"))
        actors = []

        # iterate over different actors in html
        for actor in actor_html:
            actor_names = actor.text
            actors.append(actor_names)

        actors = ", ".join(actors)
        
        # get runtime
        runtime = item.find("span",{"class":"runtime"}).text.strip(' min')

        # append to series
        tvseries.append((title, rating, genre, actors, runtime))

    return tvseries   


def save_csv(outfile, tvseries):
    """
    Output a CSV file containing highest rated TV-series.
    """
    writer = csv.writer(outfile)
    writer.writerow(['Title', 'Rating', 'Genre', 'Actors', 'Runtime'])
 
    # use extract_tvseries to get all the info
    extract_tvseries(dom)

    # iterate over each item and write 
    for title, rating, genre, actors, runtime in tvseries:
            writer.writerow([title, rating, genre, actors, runtime])

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        print('The following error occurred during HTTP GET request to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns true if the response seems to be HTML, false otherwise
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


if __name__ == "__main__":

    # get HTML content at target URL
    html = simple_get(TARGET_URL)

    # save a copy to disk in the current directory, this serves as an backup
    # of the original HTML, will be used in grading.
    with open(BACKUP_HTML, 'wb') as f:
        f.write(html)

    # parse the HTML file into a DOM representation
    dom = BeautifulSoup(html, 'html.parser')

    # extract the tv series (using the function you implemented)
    tvseries = extract_tvseries(dom)

    # write the CSV file to disk (including a header)
    with open(OUTPUT_CSV, 'w', newline='') as output_file:
        save_csv(output_file, tvseries)