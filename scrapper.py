from bs4 import BeautifulSoup
import requests
import time
import random
import database
import datetime
import os

class UserAgentAddImage:
    def user_agents(self):
        """This method select random user agents from the list and return it as a header"""
        user_agent_list = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        user_agent = random.choice(user_agent_list)
        return user_agent

    def add_image_func(self, name, url, path='chaptertemp', temp=False):
        """Method to add image into chaptertemp folder for default path and imagetemp folder for temp is True"""
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        if temp:
            imgpath = os.path.join('imagetemp', name + '.jpg')
        else:
            imgpath = os.path.join(path, name + '.jpg')
        try:
            with open(imgpath, 'wb') as img:
                img.write(response.content)
        except:
            pass

class ManganeloScrap(UserAgentAddImage):
    """This class use to scrap Manganelo website"""

    def search(self, manga):
        """This method search for manga in mangelo website and return a list of manga title, link, img, author and rating.
        It store all the search img into the imagetemp folded then delete it before search again"""
        image_temp_list = [f for f in os.listdir('imagetemp')]
        for f in image_temp_list:
            os.remove(os.path.join('imagetemp', f))
        manga = '_'.join(manga.split())
        url = 'https://manganelo.com/search/story/' + manga
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        search_panel = soup.find('div', {'class': 'panel-search-story'})
        for story_item in search_panel.find_all('div',{'class': 'search-story-item'}):
            manga = story_item.find('a', {'class': 'item-img'})
            title = manga.get('title')
            link = manga.get('href')
            img_link = story_item.find('img', {'class': 'img-loading'}).get('src')
            self.add_image_func(title, img_link, temp=True)
            img = title + '.jpg'
            author = story_item.find('span', {'class': 'text-nowrap item-author'}).text
            updated = story_item.find('span', {'class': 'text-nowrap item-time'}).text[10:21]
            rate = story_item.find('em', {'class': 'item-rate'}).text
            yield [title, link, img, author, rate, updated]

    def chapter_view(self, link):
        """This method accept link as argument and return a generator of manga image"""
        image_temp_list = [f for f in os.listdir('chaptertemp')]
        for f in image_temp_list:
            os.remove(os.path.join('chaptertemp', f))
        url = link
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        chapter_container = soup.find('div', {'class': 'container-chapter-reader'})
        link_list = list()
        for img in chapter_container.find_all('img'):
            link_list.append(img.get('src'))
        return link_list

    def chapters(self, link):
        """This method accept link as argument and return a dictionary of manga title, chapters link, img, author and rating  """
        url = link
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        panel_story_left = soup.find('div', {'class': 'story-info-left'})
        img_link = panel_story_left.span.img.get('src')
        panel_story_right = soup.find('div', {'class': 'story-info-right'})
        title = panel_story_right.h1.text
        img = title + '.jpg'
        author = panel_story_right.table.find('a', {'class': 'a-h'}).text
        updated = panel_story_right.div.p.find('span', {'class': 'stre-value'}).text[:11]
        rate = panel_story_right.div.find(attrs={'property': 'v:average'}).text
        # description = soup.find('div', {'class': 'panel-story-info-description'}).text
        panel_story_chapter = soup.find('div', {'class': 'panel-story-chapter-list'})
        chapter_list = list()
        for li in panel_story_chapter.find_all('li'):
            link = li.a.get('href')
            chapter_title = li.a.text
            #date = li.a.next_sibling.next_sibling.next_sibling.next_sibling.text
            date = li.find('span', {'class': 'chapter-time text-nowrap'}).get('title')[:11]
            chapter_list.append([chapter_title, link, date])
        manga_list = [title, url, img, author, rate, updated, chapter_list]
        return manga_list

    def date_format(self, date_str):
        """This method change the format of date in manganelo example from  Jun 19,2020 into 20200619"""
        date_time_obj = datetime.datetime.strptime(date_str, '%b %d,%Y')
        datestamps = int(''.join(str(date_time_obj.date()).split('-')))
        return datestamps

    def update(self):
        """Method to update all the mangalist for manganelo website"""
        manga_list = list()
        with open('manganelo.txt', 'r') as file:
            for line in file.readlines():
                url = line.split(',,')[1].strip()
                manga = self.chapters(url)
                date_formated = self.date_format(manga[5])
                manga_list.append([manga, date_formated])
                random_time = round(random.uniform(0.5, 1.5), 2)
                time.sleep(random_time)
            sorted_list = list()
            for manga in sorted(manga_list, key=lambda date: date[1], reverse=True):
                sorted_list.append(manga[0])
        return sorted_list


# class MangaowlScrap(UserAgentAddImage):
#     """This class is use to scrap Funmanga website"""
#
#     def search(self, manga):
#         """This method search for manga in Funmanga website and return a list of manga title, link, img, author and rating
#         It store all the search img into the imagetemp folded then delete it before search again"""
#         image_temp_list = [f for f in os.listdir('imagetemp')]
#         for f in image_temp_list:
#             os.remove(os.path.join('imagetemp', f))
#         url = f'https://mangaowl.net/search/{manga}/1'
#         user_agent = self.user_agents()
#         headers = {'User-Agents': user_agent}
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'lxml')
#         flexislider_grids = soup.find('div', {'class':'agileinfo_flexislider_grids'})
#         for comic_view in flexislider_grids.find_all('div', {'class':'col-md-2 w3l-movie-gride-agile comicView'}):
#             title = comic_view.get('data-title')
#             link = comic_view.a.get('href')
#             img_link = comic_view.find('div', {'class':'img-responsive lazy lozad comic_thumbnail div-hover-zoom'}).get('data-background-image')
#             self.add_image_func(title, img_link, temp=True)
#             img = title + '.jpg'
#             author = ' '
#             updated = comic_view.find('span', {'class':'tray-item'}).text.strip()
#             rate = comic_view.find('ul', {'class':'w3l-ratings'}).li.font.text
#             yield [title, link, img, author, rate, updated]
#
#     def chapter_view(self, link):
#         """This method accept link as argument and return a list of manga image"""
#         image_temp_list = [f for f in os.listdir('chaptertemp')]
#         for f in image_temp_list:
#             os.remove(os.path.join('chaptertemp', f))
#         url = link
#         user_agent = self.user_agents()
#         headers = {'User-Agent': user_agent}
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'lxml')
#         link_list = list()
#         for img in soup.find_all('img', {'class':'owl-lazy'}):
#             img_link = img.get('data-src')
#             link_list.append(img_link)
#         return link_list
#
#
#     def chapters(self, link):
#         """This method accept link as argument and return a dictionary of manga title, chpaters link, img , author and rating"""
#         url = link
#         user_agent = self.user_agents()
#         headers = {'User-Agent': user_agent}
#         response = requests.get(url, headers=headers)
#         soup = BeautifulSoup(response.text, 'lxml')
#         right_grids = soup.find('div', {'class':'col-xs-12 col-md-8 single-right-grid-right'})
#         title = right_grids.h2.text.strip()
#         img = title + '.jpg'
#         author = right_grids.find('a', {'class':'author_link'}).text.strip()
#         try:
#             rate = right_grids.find('font', {'class':'rating_scored'}).text
#         except:
#             rate = ' '
#         table_chapter_list = soup.find('div', {'class':'table table-chapter-list'})
#         chapter_list = list()
#         for list_group_item in table_chapter_list.find_all('li',{'class':'list-group-item chapter_list'}):
#             link = list_group_item.find('a', {'class':'chapter-url'}).get('href')
#             chapter_title = list_group_item.find('label', {'class':'chapter-title'}).text
#             chapter_title = ' '.join(chapter_title.split())
#             date = list_group_item.small.text
#             chapter_list.append([chapter_title, link, date])
#         updated = chapter_list[0][2]
#         manga_list = [title, url, img, author, rate, updated, chapter_list]
#         return manga_list
#
#     def date_format(self, date_str):
#         """This method change the format of date in manganelo example from  Jun 19,2020 into 20200619"""
#         date_time_obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')
#         datestamps = int(''.join(str(date_time_obj.date()).split('-')))
#         return datestamps
#
#     def update(self):
#         """Method to update all the mangalist for manganelo website"""
#         manga_list = list()
#         with open('mangaowl.txt', 'r') as file:
#             for line in file.readlines():
#                 url = line.split(',,')[1].strip()
#                 manga = self.chapters(url)
#                 date_formated = self.date_format(manga[5])
#                 manga_list.append([manga, date_formated])
#                 random_time = round(random.uniform(0.5, 1.5), 2)
#                 time.sleep(random_time)
#             sorted_list = list()
#             for manga in sorted(manga_list, key=lambda date: date[1], reverse=True):
#                 sorted_list.append(manga[0])
#         return sorted_list
#
#

if __name__ == '__main__':
    manga = ManganeloScrap()
    # for i in manga.search('one piece'):
    #     print(i)
    # print(manga.user_agents())
    # manga.test_request()
    # print(manga.manganelo_chapters('https://manganelo.com/manga/ilsi12001567132882'))
    # for _ in manga.chapters('https://manganelo.com/manga/ilsi12001567132882'):
    #     print(_)
    # print(manga.update())
    # manga.add_image('berserk', 'http://i998.imggur.net/one-piece/983/one-piece-13676137.jpg', temp=True)
    # manga.manganelo_chapter_view('https://manganelo.com/chapter/ilsi12001567132882/chapter_360')

    # manga = MangaowlScrap()
    # for i in manga.search('berserk'):
    #     print(i)
    # manga.chapters('https://mangaowl.net/single/51/berserk')
    # print(manga.update())
