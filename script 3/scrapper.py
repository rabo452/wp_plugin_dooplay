# this program is scraping sites and add this to dooplay wordpress
# https://pelisplushd.net/
# https://cuevana3.io/
# https://gnula.nu/
# https://pelisplus.icu/

import grequests
import requests
from saver import *
from bs4 import BeautifulSoup as bs
this_module = __import__(__name__)


headers = {
  'user-agent': """Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36"""
}

#delete no need spaces
def clear_title(title):
    arr = title.split(' ')
    new_title = []
    for i in range(len(arr)):
        if arr[i] != '':
            new_title.append(arr[i])
    return ' '.join(new_title).replace('\t', '').replace('\n', '')



class Cuevana_scrapper:
    #return streaming links
    def scrape_movie(self,url):
        if 'cuevana3.io' not in url: return []
        streaming_links = []

        r = requests.get(url, headers = headers)
        if not bs(r.text, 'lxml').select('.TPlayer'): return streaming_links #cuevana can give you the serie 

        for block in bs(r.text, 'lxml').select('.TPlayer')[0].select('iframe'):
            stream_link = block.get('data-src')
            if 'www.youtube.com' in stream_link: continue
            if 'http' not in stream_link: stream_link = 'https:' + stream_link
            streaming_links.append(stream_link)
        return streaming_links

    #return the found movies
    def search_movie(self,movie_name):
        movies = []
        r = requests.get('https://cuevana3.io/?s={}'.format(movie_name.replace(' ', '+')), headers=headers)
        soup = bs(r.text, 'lxml')
        for block in soup.select('li.xxx.TPostMv'):
            movies.append({ 'title': clear_title(block.select('h2.Title')[0].text), 'href': block.select('.TPost > a')[0].get('href') })
        return movies


    #return streaming links for each episode and season
    def scrape_series(self,url):
        if 'https://cuevana3.io/serie' not in url: return {}
        stream_links = {}
        seasons_links = {} # season_num: episodes_links

        #get links of episodes
        r = requests.get(url, headers=headers)
        soup = bs(r.text,'lxml')
        season_num = 1
        for season_block in soup.select('ul.all-episodes.MovieList'):
            seasons_links[str(season_num)] = [episode_block.get('href') for episode_block in season_block.select('article.TPost.C > a')]
            stream_links[str(season_num)] = []
            season_num += 1

        #get episodes streaming links
        for page in grequests.map([grequests.get(url, headers=headers) for season_num in seasons_links for url in seasons_links[season_num]]):
            episode_stream_links = []
            for block in bs(page.text, 'lxml').select('.TPlayer')[0].select('iframe'):
                stream_link = block.get('data-src')
                if 'www.youtube.com' in stream_link: continue
                if 'http' not in stream_link: stream_link = 'https:' + stream_link
                episode_stream_links.append(stream_link)


            episode_stream_links = remove_unworked_links(episode_stream_links)
            #insert episode stream links to need season
            for season_num in seasons_links:
                for episode_index in range(len(seasons_links[season_num])):
                    episode_url = seasons_links[season_num][episode_index]
                    if page.url == episode_url: stream_links[season_num].insert(episode_index, episode_stream_links)

        return stream_links


    #return the found series
    def search_series(self, serie_name):
        series = []
        r = requests.get('https://cuevana3.io/serie/?s={}'.format(serie_name.replace(' ', '+')), headers=headers)
        soup = bs(r.text, 'lxml')
        for block in soup.select('li.xxx.TPostMv'):
            series.append({ 'title': clear_title(block.select('h2.Title')[0].text), 'href': block.select('.TPost > a')[0].get('href') })
        return series





#from gnula script can get only movies
class Gnula_scrapper:
    #return streaming links
    def scrape_movie(self,url):
        if 'gnula.nu' not in url: return []
        streaming_links = []

        r = requests.get(url, headers = headers)
        for iframe in bs(r.text, 'lxml').select('iframe'):
            streaming_links.append(iframe.get('src'))
        return streaming_links

    #return the found movies
    def search_movie(self,movie_name):
        movies = []

        r = requests.get('https://gnula.nu/', headers=headers)
        premier_link = bs(r.text, 'lxml').select('#foxmenu > ul > li:nth-child(2) > a')[0].get('href')

        r = requests.get(premier_link, headers=headers)
        soup = bs(r.text, 'lxml')
        for block in soup.select('a.Ntooltip'):
            if movie_name.lower() in block.text.replace('\n', '').lower():
                movies.append( {'title': clear_title(block.text.replace('\n', '')), 'href': block.get('href')} )
        return movies

    def search_series(self, serie_name):
        return []
    def scrape_series(self,url):
        return {}



class Pelisplus_scrapper:
    #return streaming links
    def scrape_movie(self,url):
        if 'pelisplus.icu' not in url: return []
        streaming_links = []

        r = requests.get(url, headers = headers)
        for block in bs(r.text, 'lxml').select('li.tab-video'):
            stream_link = block.get('data-video')
            if 'http' not in stream_link: stream_link = 'https:' + stream_link
            streaming_links.append(stream_link)
        return streaming_links

    #return true if it's movie otherwise false
    def is_it_movie(self,url):
        r = requests.get(url, headers = headers)
        if 'temporada' in bs(r.text,'lxml').select('.video-info-left > h1')[0].text.lower():
            return False
        return True

    #return the found movies
    def search_movie(self,movie_name):
        movies = []

        r = requests.get('https://pelisplus.icu/search.html?keyword={}'.format(movie_name.replace(' ', '+')), headers = headers)
        soup = bs(r.text, 'lxml')
        for block in soup.select('li.video-block'):
            if self.is_it_movie('https://pelisplus.icu' + block.select('a')[0].get('href')):
                movies.append({ 'title': clear_title(block.select('div.name')[0].text.replace('\n', '').replace('\\', '')), 'href': 'https://pelisplus.icu' + block.select('a')[0].get('href')})
        return movies

    #return the found series
    def search_series(self,serie_name):
        series = []

        r = requests.get('https://pelisplus.icu/search.html?keyword={}'.format(serie_name.replace(' ', '+')), headers = headers)
        soup = bs(r.text, 'lxml')
        for block in soup.select('li.video-block'):
            if not self.is_it_movie('https://pelisplus.icu' + block.select('a')[0].get('href')):
                series.append({ 'title': clear_title(self.get_true_serie_title('https://pelisplus.icu' + block.select('a')[0].get('href')).replace('\\', '')), 'href': 'https://pelisplus.icu' + block.select('a')[0].get('href')})
        return series

    def get_true_serie_title(self, url):
        r = requests.get(url, headers=headers)
        return bs(r.text,'lxml').select('div.video-details > span.date')[0].text

    def scrape_series(self, url):
        if 'pelisplus.icu' not in url: return {}
        stream_links = {}
        seasons_links = {}

        r = requests.get(url, headers = headers)
        soup = bs(r.text, 'lxml')

        season_num = 0
        for season_block in soup.select('ul.listing.items.lists'):
            #the program get seasons blocks reversly, for example it takes: 4 season block, 3 season block, 2 season block, 1 season block
            seasons_links[str(len(soup.select('ul.listing.items.lists')) - season_num)] = ['https://pelisplus.icu' + episode_block.get('href') for episode_block in season_block.select('li.video-block > a')]
            stream_links[str(len(soup.select('ul.listing.items.lists')) - season_num)] = []
            season_num += 1

        #get episodes streaming links
        for page in grequests.map([grequests.get(url, headers=headers) for season_num in seasons_links for url in seasons_links[season_num]]):
            episode_stream_links = []
            for block in bs(page.text, 'lxml').select('li.tab-video'):
                stream_link = block.get('data-video')
                if 'www.youtube.com' in stream_link: continue
                if 'http' not in stream_link: stream_link = 'https:' + stream_link
                episode_stream_links.append(stream_link)

            episode_stream_links = remove_unworked_links(episode_stream_links)
            #insert episode stream links to need season
            for season_num in seasons_links:
                for episode_index in range(len(seasons_links[season_num])):
                    episode_url = seasons_links[season_num][episode_index]
                    if page.url == episode_url: stream_links[season_num].insert(episode_index, episode_stream_links)

        return stream_links









class Pelisplushd_scrapper:
    #return streaming links
    def scrape_movie(self,url):
        if 'pelisplushd.net' not in url: return []
        streaming_links = []

        r = requests.get(url, headers = headers)
        for script in bs(r.text,'lxml').select('script'):
            if script.contents:
                if "var video" in script.contents[0]:
                    the_list = script.contents[0].split("\n")
                    for item in the_list:
                        if "http" in item:
                            streaming_links.append(item.strip(" ").strip(";").strip('\'').split('\'')[1])
        return streaming_links

    #return found movies
    def search_movie(self,movie_name):
        movies = []

        r = requests.get('https://pelisplushd.net/search?s={}&page=1'.format(movie_name.replace(' ', '+')), headers=headers)
        #get count of pages
        soup = bs(r.text,'lxml')

        pages_to_scrape = []
        blocks = soup.select('li.page-item')
        if not blocks:
            #if here is no another pages then scrape 1 page
            pages_to_scrape.append(r.url)
        else:
            #get the second block from end
            count_of_pages = int(blocks[len(blocks) - 2].text)
            for i in range(1, count_of_pages + 1):
                pages_to_scrape.append('https://pelisplushd.net/search?s={}&page={}'.format(movie_name.replace(' ', '+'), i))

        #scrape pages using the grequests
        for page in grequests.map([grequests.get(url, headers = headers) for url in pages_to_scrape]):
            soup = bs(page.text, 'lxml')
            blocks = soup.select('.Posters > a')
            for block in blocks:
                if 'Serie' not in block.select('.centrado')[0].text:
                    movies.append({ 'title': clear_title(block.select('.listing-content > p')[0].text.replace('\n', '')) , 'href': block.get('href') })
        return movies



    #return the found series
    def search_series(self,serie_name):
        series = []

        r = requests.get('https://pelisplushd.net/search?s={}&page=1'.format(serie_name.replace(' ', '+')), headers=headers)
        #get count of pages
        soup = bs(r.text,'lxml')

        pages_to_scrape = []
        blocks = soup.select('li.page-item')
        if not blocks:
            #if here is no another pages then scrape 1 page
            pages_to_scrape.append(r.url)
        else:
            #get the second block from end
            count_of_pages = int(blocks[len(blocks) - 2].text)
            for i in range(1, count_of_pages + 1):
                pages_to_scrape.append('https://pelisplushd.net/search?s={}&page={}'.format(serie_name.replace(' ', '+'), i))

        #scrape pages using the grequests
        for page in grequests.map([grequests.get(url, headers = headers) for url in pages_to_scrape]):
            soup = bs(page.text, 'lxml')
            blocks = soup.select('.Posters > a')
            for block in blocks:
                if 'Serie' in block.select('.centrado')[0].text:
                    series.append({ 'title': clear_title(block.select('.listing-content > p')[0].text.replace('\n', '')) , 'href': block.get('href') })
        return series


    #return the streaming links
    def scrape_series(self, url):
        if 'https://pelisplushd.net/serie' not in url: return {}
        stream_links = {}
        seasons_links = {}

        r = requests.get(url, headers = headers)
        soup = bs(r.text, 'lxml')

        season_num = 1
        for season_block in soup.select('div.tab-content > div.tab-pane.fade.in'):
            #the program get seasons blocks reversly, for example it takes: 4 season block, 3 season block, 2 season block, 1 season block
            seasons_links[str(season_num)] = [episode_block.get('href') for episode_block in season_block.select('a')]
            stream_links[str(season_num)] = []
            season_num += 1

        #get episodes streaming links
        for page in grequests.map([grequests.get(url, headers=headers) for season_num in seasons_links for url in seasons_links[season_num]]):
            episode_stream_links = []
            for script in bs(page.text,'lxml').select('script'):
                if script.contents:
                    if "var video" in script.contents[0]:
                        the_list = script.contents[0].split("\n")
                        for item in the_list:
                            if "http" in item:
                                episode_stream_links.append(item.strip(" ").strip(";").strip('\'').split('\'')[1])

            episode_stream_links = remove_unworked_links(episode_stream_links)
            #insert episode stream links to need season
            for season_num in seasons_links:
                for episode_index in range(len(seasons_links[season_num])):
                    episode_url = seasons_links[season_num][episode_index]
                    if page.url == episode_url: stream_links[season_num].insert(episode_index, episode_stream_links)
        return stream_links
