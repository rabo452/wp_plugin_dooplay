import grequests
import requests
import json
from bs4 import BeautifulSoup as bs
import os

from config import secret_key, wordpress_plugin_link

headers = {
    'user-agent': """Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36""",
}


# check if this movie has already in wordpress .txt file
def has_movie(movie_name):
    try:
        f = open('movieNames.txt', 'r+', encoding='utf-8')
        file_text = f.read()
        f.close()
        movies = json.loads(file_text)
    except:
        return False

    for movie in movies:
        if movie_name.lower().replace(' ', '') == movie.lower().replace(' ', ''):
            return True
    return False


# check if this serie has already in wordpress .txt file
def has_serie(serie_name):
    try:
        f = open('serieNames.txt', 'r+', encoding='utf-8')
        file_text = f.read()
        f.close()
        series = json.loads(file_text)
    except:
        return False

    for serie in series:
        if serie_name.lower().replace(' ', '') == serie.lower().replace(' ', ''):
            return True
    return False


# add movie to file moviesNames.txt
def add_movie_to_file(movie_name):
    try:
        f = open('movieNames.txt', 'r+', encoding='utf-8')
        file_text = f.read()
        f.close()
        movies = json.loads(file_text)
    except:
        f = open('movieNames.txt', 'w+', encoding='utf-8')
        f.write(json.dumps([movie_name]))
        f.close()
        return

    movies.append(movie_name)
    f = open('movieNames.txt', 'w+', encoding='utf-8')
    f.write(json.dumps(movies))
    f.close()


# add series to file serieNames.txt
def add_serie_to_file(serie_name):
    try:
        f = open('serieNames.txt', 'r+', encoding='utf-8')
        file_text = f.read()
        f.close()
        series = json.loads(file_text)
    except:
        f = open('serieNames.txt', 'w+', encoding='utf-8')
        f.write(json.dumps([serie_name]))
        f.close()
        return

    series.append(serie_name)
    f = open('serieNames.txt', 'w+', encoding='utf-8')
    f.write(json.dumps(series))
    f.close()


# delete links that doesn't work
def remove_unworked_links(links):
    rs = [grequests.get(link, headers=headers, allow_redirects=True) for link in links]
    pages = grequests.map(rs)

    blocked_sites = [
        'ww16.xdrive.cc',
        'ww25.byter.tv',
        'hqq.tv',
        'evoload.io',
        'jetload.net'
    ]  # sites that 100% doesn't give the streaming link
    text_block = [
        '404',
        'unavailable',
        'deleted',
        'unable',
        'removed',
        'error'
    ]  # the sites can contains these phrases when video hasn't

    working_links = []
    for page in pages:
        if not page:
            continue
        if page.status_code != 200:
            continue

        block = False
        for block_url in blocked_sites:
            if block_url in page.url:
                block = True
                break
        for text in text_block:
            if text in page.text.lower():
                block = True
                break
        if block:
            continue
        # in cuevana need to check link there cuevana redirect for sure it's not broken link
        if 'cuevana' in page.url:
            block = check_cuevana_broken_link(page.url, text_block)  # return true or false
            if block:
                continue

        working_links.append(page.url)
    return working_links


def check_cuevana_broken_link(url, text_block):
    block = False
    try:
        redirected_link = 'https://api.cuevana3.io/ir/' + bs(requests.get(url).text, 'lxml').select('.link')[0].get(
            'href')
    except:
        return False
    r = requests.get(redirected_link, headers=headers, allow_redirects=True)
    for text in text_block:
        if '404' in r.text.lower() or text in r.text.lower():
            block = True
            break
    return block


def send_movie_to_wordpress(stream_links, movie_name):
    stream_links = remove_unworked_links(stream_links)
    if len(stream_links) == 0 or has_movie(movie_name):
        return

    add_movie_to_file(movie_name)
    r = requests.post(wordpress_plugin_link, headers=headers, data={
        'secret_key': secret_key,
        'stream_links': json.dumps(stream_links),
        'movie_name': movie_name})

    print('request sent to wordpress, please check the site')


def send_series_to_wordpress(stream_links_series, series_name):
    if len(stream_links_series) == 0 or has_serie(series_name):
        return

    add_serie_to_file(series_name)
    r = requests.post(wordpress_plugin_link, headers=headers, data={
        'secret_key': secret_key,
        'stream_links_series': json.dumps(stream_links_series),
        'series_name': series_name})

    print('request sent to wordpress, please check the site')


this_module = __import__(__name__)
