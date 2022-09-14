from scrapper import *
import requests
import json


# this subprogram asking the user for update his movie/series directly what's movie he want to update the links
class Monitorer_directly:
    def __init__(self, url_site, secret_key):
        self.url_site = url_site
        self.headers = {
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"}
        self.secret_key = secret_key

    def main(self):
        print(
            'Please type there the link of post (in your wp site) that you want to update (for example: https://siteDomain/movies/tom-clancy-sin-remordimientos-2021/)')
        link = input()
        print('Is it movie? (y/n)')
        movie = input()
        if movie != 'y' and movie != 'n': return
        if movie == 'y':
            movie = True
        else:
            movie = False

        response = json.loads(requests.post(self.url_site, headers=self.headers, data={
            'secret_key': self.secret_key,
            'get_id_by_link': 1,
            'link': link
        }).text)

        if response['id'] == 'null':
            print("post hasn't found by this link: {} ".format(link))
            input('Type enter to exit')
            return

        post_id, post_title, season_num, episode_num = response['id'], response['title'], response['season_num'], \
                                                       response['episode_num']

        # parse as movie
        if movie:
            movie_name = post_title
            movie_stream_links = []

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

            movie_stream_links = remove_unworked_links(movie_stream_links)
            if len(movie_stream_links) == 0:
                print('Program didn\'t find anything for this movie {}'.format(movie_name))
                input('Type enter to exit')
                return

            # send request to wordpress site
            print(requests.post(self.url_site, headers=self.headers, data={
                'secret_key': self.secret_key,
                'wordpress_post_id': post_id,
                'movie_stream_links': json.dumps(movie_stream_links),
                'movie_name': movie_name,
                'change_movie_stream_link': '1'
            }).text)

        else:

            serie_name = post_title
            id = post_id
            stream_links = []
            episode_num = episode_num
            season_num = season_num
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

            serie_hrefs = serie_hrefs[0:1]
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
                input('type enter to exit')
                return

            # send request to wordpress site
            print(requests.post(self.url_site, headers=self.headers, data={
                'secret_key': self.secret_key,
                'wordpress_post_id': id,
                'movie_stream_links': json.dumps(stream_links),
                'movie_name': serie_name,
                'change_movie_stream_link': '1'
            }).text)

        print('type enter to exit')
        input()


Monitorer_directly(wordpress_plugin_link, secret_key).main()
