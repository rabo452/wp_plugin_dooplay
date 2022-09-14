# this module add movies/series into WordPress
from WordpressSaver import *
# this module scrape all sites
from scrapper import *
import os


class Program:
    def main(self):
        print("Movie/Series Links Finder")
        print("Make a Choice:")
        print("1. Movie")
        print("2. Series")

        choice = input('Choose one, type 1 or 2: ')
        while choice != '1' and choice != '2':
            print('Please choose correct number')
            choice = input('Choose one, type 1 or 2: ')

        if choice == '1':
            print("Enter the Movie name (Spelling must be correct): ")
            requested_movie = input()
            answer = input('Are you sure to go with {} Type(y/n):  '.format(requested_movie)).replace(' ', '')
            while answer != 'y' and answer != 'n':
                print('please indicate correct answer')
                answer = input('Are you sure to go with {} Type(y/n): '.format(requested_movie)).replace(' ', '')

            if answer == 'y':
                self.find_the_movie(requested_movie)
            else:
                self.try_to_start_program_again()
        else:
            print("Enter the Serie name (Spelling must be correct): ")
            requested_serie = input()
            answer = input('Are you sure to go with {} Type(y/n): '.format(requested_serie)).replace(' ', '')
            while answer != 'y' and answer != 'n':
                print('please indicate correct answer')
                answer = input('Are you sure to go with {} Type(y/n):'.format(requested_serie)).replace(' ', '')

            if answer == 'y':
                self.find_the_serie(requested_serie)
            else:
                self.try_to_start_program_again()

    # functions for scrape the movies
    def find_the_movie(self, movie_name):
        print('Program is finding your movies... Please wait')

        all_movies = {}
        for movie_obj in [*Cuevana_scrapper().search_movie(movie_name), *Gnula_scrapper().search_movie(movie_name),
                          *Pelisplushd_scrapper().search_movie(movie_name),
                          *Pelisplus_scrapper().search_movie(movie_name)]:
            # for the same name of movie from different sites add to one array
            try:
                all_movies[movie_obj['title'].lower()].append(movie_obj['href'])
            except:
                all_movies[movie_obj['title'].lower()] = [movie_obj['href']]
        self.user_choose_movie(all_movies)

    def user_choose_movie(self, movies):
        if len(movies) == 0:
            print('Program didn\'t find any movie with need name')
            self.try_to_start_program_again()
            return

        print('--Choose your movie-- \n')

        index = 0
        movies_names = []
        movies_hrefs = []  # this array need for scrape the links by index
        for movie_title in movies:
            movie_hrefs = movies[movie_title]
            movie_scrapped_sites = self.get_scraped_sites(movie_hrefs)
            print("{}.     {}     ({})  \n".format(index + 1, movie_title.title(), movie_scrapped_sites))
            movies_hrefs.append(movie_hrefs)
            movies_names.append(movie_title.title())
            index += 1

        while True:
            try:
                movie_index = int(input('Provide the number of movie that you want to scrape: '))
                if movie_index <= (index) and movie_index > 0:
                    breaking = True
                    while True:
                        answer = input('Are you sure that you want to go with {}? (Type y/n): '.format(
                            movies_names[movie_index - 1]))
                        if answer == 'y':
                            break
                        if answer == 'n':
                            breaking = False
                            break
                    if breaking: break
            except:
                pass

        self.download_movie_to_wp(movies_names[movie_index - 1], movies_hrefs[movie_index - 1])

        answer = input('Do you want to get another movie from this list?(Type y/n): ')
        while answer != 'y' and answer != 'n':
            answer = input('Do you want to get another movie from this list?(Type y/n): ')
        if answer == 'y':
            self.user_choose_movie(movies)
        else:
            self.try_to_start_program_again()

    def download_movie_to_wp(self, movie_name, movie_hrefs):
        streaming_links = []
        for href in movie_hrefs:
            for streaming_link in [*Cuevana_scrapper().scrape_movie(href), *Gnula_scrapper().scrape_movie(href),
                                   *Pelisplushd_scrapper().scrape_movie(href),
                                   *Pelisplus_scrapper().scrape_movie(href)]:
                streaming_links.append(streaming_link)
        send_movie_to_wordpress(streaming_links, movie_name)

    # functions for scrape the series
    def find_the_serie(self, serie_name):
        print('Program is finding your serie... Please wait')

        all_series = {}
        for serie_obj in [*Cuevana_scrapper().search_series(serie_name), *Gnula_scrapper().search_series(serie_name),
                          *Pelisplushd_scrapper().search_series(serie_name),
                          *Pelisplus_scrapper().search_series(serie_name)]:
            # for the same name of movie from different sites add to one array
            try:
                all_series[serie_obj['title'].lower()].append(serie_obj['href'])
            except:
                all_series[serie_obj['title'].lower()] = [serie_obj['href']]
        self.user_choose_serie(all_series)

    def user_choose_serie(self, series):
        if len(series) == 0:
            print('Program didn\'t find any serie with need name')
            self.try_to_start_program_again()
            return

        print('--Choose your serie-- \n')

        index = 0
        series_names = []
        series_hrefs = []  # this array need for scrape the links by index
        for series_title in series:
            series_href = series[series_title]
            series_scrapped_sites = self.get_scraped_sites(series_href)
            print("{}.     {}     ({})  \n".format(index + 1, series_title.title(), series_scrapped_sites))
            series_hrefs.append(series_href)
            series_names.append(series_title.title())
            index += 1

        while True:
            try:
                series_index = int(input('Provide the number of serie that you want to scrape: '))
                if series_index <= (index) and series_index > 0:
                    breaking = True
                    while True:
                        answer = input('Are you sure that you want to go with {}? (Type y/n): '.format(
                            series_names[series_index - 1]))
                        if answer == 'y':
                            break
                        if answer == 'n':
                            breaking = False
                            break
                    if breaking: break
            except:
                pass

        self.download_serie_to_wp(series_names[series_index - 1], series_hrefs[series_index - 1])

        answer = input('Do you want to get another movie from this list?(Type y/n): ')
        while answer != 'y' and answer != 'n':
            answer = input('Do you want to get another movie from this list?(Type y/n): ')
        if answer == 'y':
            self.user_choose_serie(series)
        else:
            self.try_to_start_program_again()

    def download_serie_to_wp(self, serie_name, serie_hrefs):
        # for different sites add streaming links for each episode
        streaming_links = {}
        for href in serie_hrefs:
            result = [Cuevana_scrapper().scrape_series(href), Gnula_scrapper().scrape_series(href),
                      Pelisplushd_scrapper().scrape_series(href), Pelisplus_scrapper().scrape_series(href)]
            # get the result of each site
            for result_site in result:
                # if it empty skip
                if not result_site: continue
                for season in result_site:
                    try:
                        streaming_links[season]
                    except:
                        streaming_links[season] = []

                    for episode_num in range(len(result_site[season])):
                        for streaming_link in result_site[season][episode_num]:
                            try:
                                streaming_links[season][episode_num].append(streaming_link)
                            except:
                                streaming_links[season].append([streaming_link])

        send_series_to_wordpress(streaming_links, serie_name)

    # additional functions
    def try_to_start_program_again(self):
        again = input("Want to search again? (y/n):")
        while again != 'y' and again != 'n':
            print('Please indicate correct answer')
            again = input('Want to search again? (y/n):')
        if again == 'y':
            os.system('cls')
            self.main()

    def get_scraped_sites(self, arr_href):
        sites = ""
        for href in arr_href: sites += href.split('/')[2] + ' '  # get domain
        return sites


if __name__ == '__main__':
    Program().main()
