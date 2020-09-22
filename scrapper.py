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
        if len(response.content) < 500:
            response = requests.get('http://static.mangahere.cc/v201906282/mangahere/images/nopicture.jpg', headers=headers)
        if temp:
            imgpath = os.path.join('imagetemp', name + '.jpg')
        else:
            imgpath = os.path.join(path, name + '.jpg')
        try:
            with open(imgpath, 'wb') as img:
                img.write(response.content)
        except:
            pass

    def check_filename_func(self, name):
        """Method to check the file name if has invalid special character
           It will remove the invalid special character and return the new file name"""
        invalid_chars = set('<>:"/\\|?*')
        new_name = ''
        for c in name:
            if c not in invalid_chars:
                new_name += c
        return new_name

class ManganeloScrap(UserAgentAddImage):
    """This class use to scrap Manganelo website"""

    def search(self, manga):
        """This method search for manga in mangelo website and return a generator of manga title, link, img, author and rating.
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
            img_title = self.check_filename_func(title)
            self.add_image_func(img_title, img_link, temp=True)
            img = img_title + '.jpg'
            author = story_item.find('span', {'class': 'text-nowrap item-author'}).text
            updated = story_item.find('span', {'class': 'text-nowrap item-time'}).text[10:21]
            rate = story_item.find('em', {'class': 'item-rate'}).text
            yield [title, link, img, author, rate, updated]

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


class MangareaderScrap(UserAgentAddImage):
    """This class use to scrap Mangareader website"""

    def search(self, manga):
        """This method search for manga in manghere website and return a generator of manga title, link, img, author and rating.
        It store all the search img into the imagetemp folded then delete it before search again"""
        image_temp_list = [f for f in os.listdir('imagetemp')]
        for f in image_temp_list:
            os.remove(os.path.join('imagetemp', f))
        manga = '+'.join(manga.split())
        url = "https://www.mangareader.net/search/?w=" + manga + "&rd=0&status=0&order=0&genre=0000000000000000000000000000000000000&p=0"
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        id_ares = soup.find('div', {'class', 'd52'})
        for d54 in id_ares.find_all('div', {'class', 'd54'}):
            title = d54.find('div', {'class', 'd57'}).a.text
            link = "https://www.mangareader.net" + d54.find('div', {'class', 'd57'}).a.get('href')
            img_link = "https:" + d54.find('div', {'class', 'd56'}).get('data-src')
            img_title = self.check_filename_func(title)
            self.add_image_func(img_title, img_link, temp=True)
            img = img_title + '.jpg'
            author = ''
            updated = d54.find('div', {'class', 'd58'}).text
            rate = ''
            yield [title, link, img, author, rate, updated]

    def chapters(self, link):
        """This method accept link as argument and return a dictionary of manga title, chapters link, img, author and rating  """
        url = link
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        d37_class = soup.find('div', {'class': 'd37'})
        title = d37_class.find('table', {'class': 'd41'}).find('span', {'class': 'name'}).text
        img_title = self.check_filename_func(title)
        img = img_title + '.jpg'
        author = d37_class.find('td', text="Author :").find_next_sibling('td').text
        rate = ''
        # updated = d37_class.find('ul', {'class': 'd44'}).li.a.text
        d48_class = soup.find('table', {'class': 'd48'})
        first_tr = True
        chapter_list = list()
        for tr in d48_class.find_all('tr'):
            if first_tr:
                first_tr = False
            else:
                link = "https://www.mangareader.net" + tr.td.a.get('href')
                chapter_title = tr.td.a.text
                date = tr.td.find_next_sibling('td').text
                chapter_list.append([chapter_title, link, date])
        chapter_list = chapter_list[::-1]
        updated = chapter_list[0][-1]
        manga_list = [title, url, img, author, rate, updated, chapter_list]
        return manga_list

    def date_format(self, date_str):
        """This method change the format of date in mangareader example from  07/19/2020 into 20200619"""
        date_time_obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        datestamps = int(''.join(str(date_time_obj.date()).split('-')))
        return datestamps

    def update(self):
        """Method to update all the mangalist for mangareader website"""
        manga_list = list()
        with open('mangareader.txt', 'r') as file:
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

if __name__ == '__main__':
    manga = ManganeloScrap()
    # for i in manga.search('one piece'):
    #     print(i)
    for _ in manga.chapters('https://manganelo.com/manga/ilsi12001567132882'):
        print(_)
    # print(manga.update())
    # manga.add_image('berserk', 'http://i998.imggur.net/one-piece/983/one-piece-13676137.jpg', temp=True)
    # manga.manganelo_chapter_view('https://manganelo.com/chapter/ilsi12001567132882/chapter_360')

    manga = MangareaderScrap()
    # for i in manga.search('berserk'):
    #     print(i)
    for _ in manga.chapters('https://www.mangareader.net/berserk'):
        print(_)
