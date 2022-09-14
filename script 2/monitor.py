from saver import *
from scrapper import *
import requests
import json


# this class monitor wordpress site,
# change links to news if they exists
# this subprogram get the list of movies and update it each by each
class Monitorer_Wordpress:
    def __init__(self, url_site, secret_key):
        self.url_site = url_site
        self.headers = {
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
        self.secret_key = secret_key

    def monitor_site(self):
        # monitor movies and series after
        movies = json.loads(requests.post(self.url_site, headers=self.headers, data={
            'secret_key': self.secret_key,
            'get_movies_info': '1'
        }).text)
        self.monitor_movies(movies)
        tvshows = json.loads(requests.post(self.url_site, headers=self.headers, data={
            'secret_key': self.secret_key,
            'get_tvshows_info': '1'
        }).text)
        self.monitor_tvshows(tvshows)

    def monitor_movies(self, movies):
        for i in range(len(movies)):
            movie_name = movies[i]['title']
            wordpress_post_id = movies[i]['ID']
            movie_stream_links = movies[i]['stream_links']
            print('Trying to find the need streaming links for the {}'.format(movie_name))

            the_same_movie_links = []
            for movie_obj in [*Cuevana_scrapper().search_movie(movie_name), *Gnula_scrapper().search_movie(movie_name),
                              *Pelisplushd_scrapper().search_movie(movie_name),
                              *Pelisplus_scrapper().search_movie(movie_name)]:
                if movie_obj['title'].lower().replace(' ', '') in movie_name.lower().replace(' ',
                                                                                             ''): the_same_movie_links.append(
                    movie_obj['href'])

            for href in the_same_movie_links:
                for streaming_link in [*Cuevana_scrapper().scrape_movie(href), *Gnula_scrapper().scrape_movie(href),
                                       *Pelisplushd_scrapper().scrape_movie(href),
                                       *Pelisplus_scrapper().scrape_movie(href)]:
                    movie_stream_links.append(streaming_link)

            # check for broken link
            movie_stream_links = remove_unworked_links(movie_stream_links)

            if len(movie_stream_links) == 0:
                print('Program didn\'t find anything for this movie {}'.format(movie_name))
                continue

            # send request to wordpress site
            print(requests.post(self.url_site, headers=self.headers, data={
                'secret_key': self.secret_key,
                'wordpress_post_id': wordpress_post_id,
                'movie_stream_links': json.dumps(movie_stream_links),
                'movie_name': movie_name,
                'change_movie_stream_link': '1'
            }).text)

    def monitor_tvshows(self, tvshows):
        for tvshow_obj in tvshows:
            serie_name = tvshow_obj['title']
            id = tvshow_obj['ID']
            stream_links = tvshow_obj['stream_links']
            episode_num = tvshow_obj['episode_num']
            season_num = tvshow_obj['season_num']
            print('Trying to find the need streaming links for the {} season {} episode {}...'.format(serie_name,
                                                                                                      season_num,
                                                                                                      episode_num))

            serie_hrefs = []
            for serie_obj in [*Cuevana_scrapper().search_series(serie_name),
                              *Gnula_scrapper().search_series(serie_name),
                              *Pelisplushd_scrapper().search_series(serie_name),
                              *Pelisplus_scrapper().search_series(serie_name)]:
                if serie_obj['title'].lower().replace(' ', '') in serie_name.lower().replace(' ',
                                                                                             ''): serie_hrefs.append(
                    serie_obj['href'])

            # for different sites add streaming links for each episode
            streaming_links = {}
            for href in serie_hrefs:
                result = [Cuevana_scrapper().scrape_series(href), Gnula_scrapper().scrape_series(href),
                          Pelisplushd_scrapper().scrape_series(href), Pelisplus_scrapper().scrape_series(href)]
                # get the result of each site
                for result_site in result:
                    # if it empty skip
                    if not result_site: continue
                    streaming_links = result_site

            # if program find the serie get the stream links for need episode
            if streaming_links:
                try:
                    for stream_link in streaming_links[str(season_num)][int(episode_num) - 1]: stream_links.append(
                        stream_link)
                except:
                    pass

            stream_links = remove_unworked_links(stream_links)
            if not stream_links:
                print("Program didn't find anything for this {} serie".format(serie_name))
                continue

            # send request to wordpress site
            print(requests.post(self.url_site, headers=self.headers, data={
                'secret_key': self.secret_key,
                'wordpress_post_id': id,
                'movie_stream_links': json.dumps(stream_links),
                'movie_name': serie_name,
                'change_movie_stream_link': '1'
            }).text)


if __name__ == '__main__':
    # program will work until closed
    while True:
        Monitorer_Wordpress(wordpress_plugin_link, secret_key).monitor_site()
