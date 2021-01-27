from bs4 import BeautifulSoup
import requests
import time
import random
import database
import datetime
import os

class MainFunc:
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

    def add_image_func(self, name, url, path='imagetemp'):
        """Method to add image into chaptertemp folder for default path and imagetemp folder for temp is True"""
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        if len(response.content) < 500:
            response = requests.get('http://static.mangahere.cc/v201906282/mangahere/images/nopicture.jpg', headers=headers)
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

    def check_name_len(self, name):
        """Method to check the name if exceed in 20 letters and Modified if exceed"""
        if len(name) > 23:
            name = name[:21] + '...'
            return name
        return name

    def url_name_check(self, name):
        """Method to check the url if valid and return a valid url"""
        if name[:4] != "http":
            name = "https:" + name
        return name

    def delete_manga(self, server, manga):
        """Method to delete manga in the database"""
        imagemanga = os.path.join('..', 'imagemanga', server)
        manga_list = database.TextFile(server, imagemanga)
        try:
            manga_list.del_manga(manga)
            print(f"Manga deleted {manga}")
        except:
            print("NO FILE")

class VersionCheck(MainFunc):
    """This class use to check the current version of the Manga Update"""
    def check(self):
        with open('version.txt', 'r') as file:
            current_version = file.read().strip()
            url = "https://play.google.com/store/apps/details?id=org.blufips.mangaupdate"
            user_agent = self.user_agents()
            headers = {'User-Agent': user_agent}
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'lxml')
            url_version = soup.find('div', text='Current Version').find_next_sibling('span').div.span.text
            if current_version != url_version:
                return True
            return False

class ManganeloScrap(MainFunc):
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
        try:
            for story_item in search_panel.find_all('div',{'class': 'search-story-item'}):
                title = story_item.find('a',{'class': 'item-title'}).text
                link = story_item.find('a', {'class': 'item-img'}).get('href')
                img_link = story_item.find('img', {'class': 'img-loading'}).get('src')
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link)
                img = img_title + '.jpg'
                author = story_item.find('span', {'class': 'text-nowrap item-author'}).text
                updated = story_item.find('span', {'class': 'text-nowrap item-time'}).text[10:21]
                rate = story_item.find('em', {'class': 'item-rate'}).text
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
        except GeneratorExit:
            return
        except AttributeError:
            pass

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
        img_title = self.check_filename_func(title)
        img = img_title + '.jpg'
        author = panel_story_right.table.find('a', {'class': 'a-h'}).text
        updated = panel_story_right.div.p.find('span', {'class': 'stre-value'}).text[:11]
        rate = panel_story_right.div.find(attrs={'property': 'v:average'}).text
        panel_story_chapter = soup.find('div', {'class': 'panel-story-chapter-list'})
        chapter_list = list()
        try:
            for li in panel_story_chapter.find_all('li'):
                link = li.a.get('href')
                chapter_title = li.a.text
                date = li.find('span', {'class': 'chapter-time text-nowrap'}).get('title')[:11]
                chapter_list.append([chapter_title, link, date])
        except AttributeError:
            chapter_list = None
        manga_list = list(map(self.check_name_len, [title, author, rate, updated]))
        manga_list.insert(1, url)
        manga_list.insert(2, img)
        manga_list.append(chapter_list)
        return manga_list

    def date_format(self, date_str):
        """This method change the format of date in manganelo example from  Jun 19,2020 into 20200619"""
        date_time_obj = datetime.datetime.strptime(date_str, '%b %d,%Y')
        datestamps = int(''.join(str(date_time_obj.date()).split('-')))
        return datestamps

    def update(self):
        """Method to update all the mangalist for manganelo website"""
        manga_list = list()
        file_path = os.path.join('..', 'manganelo.txt')
        with open(file_path, 'rb') as file:
            for line in file.readlines():
                line = line.decode('utf-8')
                url = line.split(',,')[1].strip()
                try:
                    manga = self.chapters(url)
                except AttributeError:
                    manga_name = line.split(',,')[0].strip()
                    print(manga_name)
                    self.delete_manga('manganelo', manga_name)
                    continue
                date_formated = self.date_format(manga[5])
                manga_list.append([manga, date_formated])
                random_time = round(random.uniform(0.1, .5), 2) # Add Random Delay from .1 to .5 sec
                time.sleep(random_time)
            sorted_list = list()
            for manga in sorted(manga_list, key=lambda date: date[1], reverse=True):
                sorted_list.append(manga[0])
        return sorted_list

    def release(self):
        """Method to check latest release for manganelo website"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        url = 'https://manganelo.com/'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        homepage = soup.find('div', {'class': 'panel-content-homepage'})
        latest_manga_list = homepage.find_all('div', {'class': 'content-homepage-item'})
        for num in range(10):
            try:
                item_right = latest_manga_list[num].find('div', {'class' : 'content-homepage-item-right'})
                title = item_right.h3.a.text
                link = item_right.h3.a.get('href')
                img_link = latest_manga_list[num].find('img', {'class': 'img-loading'}).get('src')
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link, path='imagerelease')
                img = img_title + '.jpg'
                author = item_right.span.text
                rate = latest_manga_list[num].find('em', {'class': 'item-rate'}).text
                try:
                    updated = item_right.p.text.strip()
                    chapter, time = updated.split('\n')
                    chapter = self.check_name_len(chapter)
                    updated = f"{chapter}\n{time}"
                except AttributeError:
                    updated = 'N/A'
                checked_names = list(map(self.check_name_len, [title, author, rate]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                checked_names.append(updated)
                yield checked_names
            except GeneratorExit:
                return
            except AttributeError:
                pass

    def genres(self):
        """Method to get all the manga genres and its corresponding link and return a list of it"""
        url = 'https://manganelo.com/'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        panel_category = soup.find('div', {'class': 'panel-category'})
        genres_list = list()
        for p_tag in panel_category.find_all('p', {'class', 'pn-category-row'}):
            try:
                for a_tag in p_tag.find_all('a'):
                    genre = a_tag.text
                    link = a_tag.get('href')
                    genres_list.append([genre, link])
            except:
                print("Genre Error")
        return genres_list

    def manga_genres(self, url):
        """This method is to get all the manga in the genre list"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        page_list = list()
        try:
            panel_content_genres = soup.find('div', {'class': 'panel-content-genres'})
            group_page = soup.find('div', {'class': 'group-page'})
        except AttributeError:
            group_page = list()
            yield group_page
        try:
            for a in group_page.find_all('a'):
                text = a.text
                link = a.get('href')
                page_list.append([text, link])
            yield page_list
        except GeneratorExit:
            return
        except AttributeError:
            pass
        panel_content_genres = soup.find('div', {'class': 'panel-content-genres'})
        for content_genres_item in panel_content_genres.find_all('div', {'class', 'content-genres-item'}):
            try:
                title = content_genres_item.find('a', {'class': 'genres-item-name'}).text
                link = content_genres_item.find('a', {'class': 'genres-item-name'}).get('href')
                img_link = content_genres_item.find('a', {'class': 'genres-item-img'}).img.get('src')
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link, path='imagerelease')
                img = img_title + '.jpg'
                author = content_genres_item.find('span', {'class': 'genres-item-author'}).text
                rate = content_genres_item.find('em', {'class': 'genres-item-rate'}).text
                updated = content_genres_item.find('a', {'class': 'genres-item-chap'}).text
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
            except GeneratorExit:
                return
            except AttributeError:
                pass


class MangareaderScrap(MainFunc):
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
            try:
                title = d54.find('div', {'class', 'd57'}).a.text
                link = "https://www.mangareader.net" + d54.find('div', {'class', 'd57'}).a.get('href')
                img_link = "https:" + d54.find('div', {'class', 'd56'}).get('data-src')
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link)
                img = img_title + '.jpg'
                author = 'N/A'
                updated = d54.find('div', {'class', 'd58'}).text
                rate = 'N/A'
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
            except GeneratorExit:
                return
            except AttributeError:
                pass

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
        rate = 'N/A'
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
        manga_list = list(map(self.check_name_len, [title, author, rate, updated]))
        manga_list.insert(1, url)
        manga_list.insert(2, img)
        manga_list.append(chapter_list)
        return manga_list

    def date_format(self, date_str):
        """This method change the format of date in mangareader example from  07/19/2020 into 20200619"""
        date_time_obj = datetime.datetime.strptime(date_str, '%m/%d/%Y')
        datestamps = int(''.join(str(date_time_obj.date()).split('-')))
        return datestamps

    def update(self):
        """Method to update all the mangalist for mangareader website"""
        manga_list = list()
        file_path = os.path.join('..', 'mangareader.txt')
        with open(file_path, 'rb') as file:
            for line in file.readlines():
                line = line.decode('utf-8')
                url = line.split(',,')[1].strip()
                try:
                    manga = self.chapters(url)
                except AttributeError:
                    manga_name = line.split(',,')[0].strip()
                    print(manga_name)
                    self.delete_manga('manganelo', manga_name)
                    continue
                date_formated = self.date_format(manga[5])
                manga_list.append([manga, date_formated])
                random_time = round(random.uniform(0.1, .5), 2) # Add Random Delay from .1 to .5 sec
                time.sleep(random_time)
            sorted_list = list()
            for manga in sorted(manga_list, key=lambda date: date[1], reverse=True):
                sorted_list.append(manga[0])
        return sorted_list

    def release(self):
        """Method to check latest release for mangareader website"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        url = 'https://www.mangareader.net/'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        latest_manga_list = soup.find_all('div', {'class': 'd47'})
        for num in range(8):
            try:
                title = latest_manga_list[num].find('div', {'class': 'd53'}).text
                link = "https://www.mangareader.net/" + latest_manga_list[num].find('div', {'class': 'd53'}).a.get('href')
                updated = latest_manga_list[num].find('ul', {'class': 'd56'}).li.a.text
                response = requests.get(link, headers=headers)
                soup = BeautifulSoup(response.text, 'lxml')
                img_link = soup.find('div', {'class': 'd38'}).img.get('src')
                img_link = self.url_name_check(img_link)
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link, path='imagerelease')
                img = img_title + '.jpg'
                author = soup.find('table', {'class': 'd41'}).find('td', text="Author :").find_next_sibling('td').text
                rate = 'N/A'
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
            except GeneratorExit:
                return
            except AttributeError:
                pass
            except:
                print("ERROR")

    def genres(self):
        """Method to get all the manga genres and its corresponding link and return a list of it"""
        url = 'https://www.mangareader.net/popular'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        ul = soup.find('ul', {'class': 'd50'})
        genres_list = list()
        for li in ul.find_all('li'):
            try:
                genre = li.a.text
                link = "https://www.mangareader.net" + li.a.get('href')
                genres_list.append([genre, link])
            except:
                print("Genre Error")
        return genres_list

    def manga_genres(self, url):
        """This method is to get all the manga in the genre list"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        page_list = list()
        try:
            d53_class = soup.find('ul', {'class':'d53'})
        except AttributeError:
            d53_class = None
        for li in d53_class.find_all('li'):
            try:
                text = li.a.text
                link = "https://www.mangareader.net" + li.a.get('href')
                page_list.append([text, link])
            except AttributeError:
                text = li.span.text
                link = None
                page_list.append([text, link])
            except GeneratorExit:
                return
            except AttributeError:
                pass
        yield page_list
        d38_class = soup.find('div', {'class': 'd38'})
        for d39_class in d38_class.find_all('div', {'class': 'd39'}):
            try:
                title = d39_class.find('div', {'class': 'd42'}).a.text
                link = "https://www.mangareader.net" + d39_class.find('div', {'class': 'd42'}).a.get('href')
                img_link = "https:" + d39_class.find('div', {'class': 'd41'}).get('data-src')
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link, path='imagerelease')
                img = img_title + '.jpg'
                author = d39_class.find('div', {'class': 'd43'}).text
                rate = 'N/A'
                updated = d39_class.find('div', {'class': 'd44'}).text
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
            except AttributeError:
                pass
            except GeneratorExit:
                return


class ToonilyScrap(MainFunc):
    """This class use to scrap Toonily website"""

    def search(self, manga):
        """This method search for manga in toonily website and return a generator of manga title, link, img, author and rating.
        It store all the search img into the imagetemp folded then delete it before search again"""
        image_temp_list = [f for f in os.listdir('imagetemp')]
        for f in image_temp_list:
            os.remove(os.path.join('imagetemp', f))
        manga = '+'.join(manga.split())
        url = 'https://toonily.com/?s=' + manga + '&post_type=wp-manga'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        c_tab_items = soup.find('div', {'class': 'c-tabs-item'})
        try:
            for content in c_tab_items.find_all('div', {'class': 'c-tabs-item__content'}):
                title = content.find('div', {'class': 'post-title'}).h3.a.text
                link = content.find('div', {'class': 'post-title'}).h3.a.get('href')
                img_link = content.find('div', {'class': 'c-image-hover'}).a.img.get('data-src')
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link)
                img = img_title + '.jpg'
                author = content.find('div', {'class': 'mg_author'}).find('div', {'class': 'summary-content'}).a.text
                updated = content.find('div', {'class': 'latest-chap'}).find('span', {'class': 'chapter'}).a.text
                rate = content.find('div', {'class': 'post-total-rating'}).find('span', {'class': 'score'}).text
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
        except GeneratorExit:
            return
        except AttributeError:
            pass

    def chapters(self, link):
        """This method accept link as argument and return a dictionary of manga title, chapters link, img, author and rating  """
        url = link
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        img_link = soup.find('div', {'class': 'summary_image'}).a.img.get('data-src')
        title = soup.find('div', {'class': 'post-title'}).h1.text.strip().split('\n')
        if len(title) > 1:
            title = title[1]
        else:
            title = title[0]
        img_title = self.check_filename_func(title)
        img = img_title + '.jpg'
        post_content = soup.find('div', {'class': 'post-content'})
        author = post_content.find('div', {'class': 'author-content'}).a.text
        rate = post_content.find('div', {'class': 'post-total-rating'}).find('span', {'class': 'score'}).text
        ul_version_chap = soup.find('ul', {'class': 'version-chap'})
        chapter_list = list()
        try:
            for li in ul_version_chap.find_all('li', {'class': 'wp-manga-chapter'}):
                link = li.a.get('href')
                chapter_title = li.a.text.strip()
                try:
                    date = li.find('span', {'class': 'chapter-release-date'}).i.text
                except AttributeError:
                    date_now = datetime.datetime.now()
                    date = date_now.strftime("%B %d, %Y")
                chapter_list.append([chapter_title, link, date])
            updated = chapter_list[0][2]
        except AttributeError:
            chapter_list = None
            updated = 'N/A'
        manga_list = list(map(self.check_name_len, [title, author, rate, updated]))
        manga_list.insert(1, url)
        manga_list.insert(2, img)
        manga_list.append(chapter_list)
        return manga_list

    def date_format(self, date_str):
        """This method change the format of date in toonily example from  April 19, 2020 into 20200619"""
        date_time_obj = datetime.datetime.strptime(date_str, '%B %d, %Y')
        datestamps = int(''.join(str(date_time_obj.date()).split('-')))
        return datestamps

    def update(self):
        """Method to update all the mangalist for toonily website"""
        manga_list = list()
        file_path = os.path.join('..', 'toonily.txt')
        with open(file_path, 'rb') as file:
            for line in file.readlines():
                line = line.decode('utf-8')
                url = line.split(',,')[1].strip()
                try:
                    manga = self.chapters(url)
                except AttributeError:
                    manga_name = line.split(',,')[0].strip()
                    print(manga_name)
                    self.delete_manga('manganelo', manga_name)
                    continue
                date_formated = self.date_format(manga[5])
                manga_list.append([manga, date_formated])
                random_time = round(random.uniform(0.1, .5), 2) # Add Random Delay from .1 to .5 sec
                time.sleep(random_time)
            sorted_list = list()
            for manga in sorted(manga_list, key=lambda date: date[1], reverse=True):
                sorted_list.append(manga[0])
        return sorted_list

    def release(self):
        """Method to check latest release for toonily website"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        url = 'https://toonily.com/'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        page_content_listing = soup.find('div', {'class': 'page-content-listing'})
        page_listing = page_content_listing.find_all('div', {'class': 'page-listing-item'})
        for num in range(2):
            for col_6 in page_listing[num].find_all('div', {'class': 'col-6'}):
                try:
                    title = col_6.find('div', {'class': 'post-title'}).h3.a.text
                    link = col_6.find('div', {'class': 'post-title'}).h3.a.get('href')
                    img_link = col_6.find('div', {'class': 'item-thumb'}).a.img.get('data-src')
                    img_title = self.check_filename_func(title)
                    self.add_image_func(img_title, img_link, path='imagerelease')
                    img = img_title + '.jpg'
                    author = 'N/A'
                    rate = col_6.find('span', {'class': 'score'}).text
                    updated = col_6.find('div', {'class': 'chapter-item'}).span.a.text.strip()
                    checked_names = list(map(self.check_name_len, [title, author, rate]))
                    checked_names.insert(1, link)
                    checked_names.insert(2, img)
                    checked_names.append(updated)
                    yield checked_names
                except GeneratorExit:
                    return
                except AttributeError:
                    pass

    def genres(self):
        """Method to get all the manga genres and its corresponding link and return a list of it"""
        url = 'https://toonily.com/webtoon-tag/completed-webtoon/'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        genres_collapse = soup.find('div', {'class', 'genres__collapse'})
        genres_list = list()
        for col_6 in genres_collapse.find('ul', {'class', 'list-unstyled'}).find_all('li', {'class', 'col-6'}):
            try:
                genre = ''.join(col_6.a.text.strip().split('\n'))
                link = col_6.a.get('href')
                genres_list.append([genre, link])
            except:
                print("Genre Error")
        return genres_list

    def manga_genres(self, url):
        """This method is to get all the manga in the genre list"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        try:
            wp_pagenavi = soup.find('div', {'class', 'wp-pagenavi'})
            children = wp_pagenavi.findChildren()
        except AttributeError:
            children = list()
        page_list = list()
        try:
            for child in children:
                text = child.text
                link = child.get('href')
                page_list.append([text, link])
            yield page_list
        except GeneratorExit:
            return
        except AttributeError:
            pass
        page_content_listing = soup.find('div', {'class', 'page-content-listing'})
        try:
            for page_listing_item in page_content_listing.find_all('div', {'class', 'page-listing-item'}):
                for col_6 in page_listing_item.find_all('div', {'class': 'col-6'}):
                    try:
                        title = col_6.find('div', {'class': 'post-title'}).h3.a.text
                        link = col_6.find('div', {'class': 'post-title'}).h3.a.get('href')
                        img_link = col_6.find('div', {'class': 'item-thumb'}).a.img.get('data-src')
                        img_title = self.check_filename_func(title)
                        self.add_image_func(img_title, img_link, path='imagerelease')
                        img = img_title + '.jpg'
                        author = 'N/A'
                        rate = col_6.find('span', {'class': 'score'}).text
                        updated = col_6.find('div', {'class': 'chapter-item'}).span.a.text.strip()
                        checked_names = list(map(self.check_name_len, [title, author, rate]))
                        checked_names.insert(1, link)
                        checked_names.insert(2, img)
                        checked_names.append(updated)
                        yield checked_names
                    except GeneratorExit:
                        return
                    except AttributeError:
                        pass
        except AttributeError:
            pass

class MangaParkScrap(MainFunc):
    """This class use to scrap MangaPark website"""

    def search(self, manga):
        """This method search for manga in mangapark website and return a generator of manga title, link, img, author and rating.
        It store all the search img into the imagetemp folded then delete it before search again"""
        image_temp_list = [f for f in os.listdir('imagetemp')]
        for f in image_temp_list:
            os.remove(os.path.join('imagetemp', f))
        manga = '+'.join(manga.split())
        url = 'https://mangapark.net/search?q=' + manga
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        manga_list = soup.find('div', {'class':'manga-list'})
        try:
            for item in manga_list.find_all('div', {'class':'item'}):
                title = item.table.tr.td.find_next_sibling('td').h2.a.get('title')
                link = "https://mangapark.net" + item.table.tr.td.find_next_sibling('td').h2.a.get('href')
                img_link = item.table.tr.td.a.img.get('src')
                img_title = self.check_filename_func(title)
                try:
                    self.add_image_func(img_title, img_link)
                except:
                    img_link = "https://static.mangapark.net/img/no-cover.jpg"
                    self.add_image_func(img_title, img_link)
                img = img_title + '.jpg'
                author = item.find('b', text="Authors/Artists:").find_next_sibling('a').text
                updated = item.find('a', {'class':'visited'}).b.text
                rate = item.find('div', {'class':'rate'}).i.text
                checked_names = list(map(self.check_name_len, [title, author, rate, updated]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                yield checked_names
        except GeneratorExit:
            return
        except AttributeError:
            pass

    def chapters(self, link):
        """This method accept link as argument and return a dictionary of manga title, chapters link, img, author and rating  """
        url = link
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('section', {'class':'manga'}).div.div.h2.a.text
        img_title = self.check_filename_func(title)
        if "Manga" == img_title[-5:]:
            img = img_title[:-5].strip() + '.jpg'
        elif "Webtoon" == img_title[-7:]:
            img = img_title[:-7].strip() + '.jpg'
        elif "Manhwa" == img_title[-6:]:
            img = img_title[:-6].strip() + '.jpg'
        row = soup.find('div', {'class':'row'})
        author = row.find('table', {'class':'attr'}).find('th', text="Author(s)").find_next_sibling('td').a.text
        rate = row.find('div', {'id':'rating'}).i.text
        book_list = soup.find('div', {'class':'book-list-1'})
        stream_dict = dict()
        for streams in book_list.find_all('div', {'class':'stream'}):
            stream = streams.get('id')
            time = streams.find('ul', {'class':'chapter'}).li.find('span', {'class':'time'}).text.strip()
            time = self.date_format(time)
            stream_dict.update({stream : time})
        stream_id = min(stream_dict.keys(), key=(lambda k: stream_dict[k]))
        stream = soup.find('div', {'id':stream_id})
        chapter_list = list()
        if stream.find('div', {'class':'volume'}):
            try:
                for volume in stream.find_all('div', {'class':'volume'}):
                    ul_chapter = volume.find('ul', {'class':'chapter'})
                    for li in ul_chapter.find_all('li', {'class':'item'}):
                        link = "https://mangapark.net/" + li.find('a', {'class':'ch'}).get('href')
                        chapter_title = li.find('a', {'class':'ch'}).text
                        date = li.find('span', {'class':'time'}).text.strip()
                        chapter_list.append([chapter_title, link, date])
            except AttributeError:
                pass
        else:
            ul_chapter = stream.find('ul', {'class':'chapter'})
            try:
                for li in ul_chapter.find_all('li', {'class':'item'}):
                    link = "https://mangapark.net/" + li.find('a', {'class':'ch'}).get('href')
                    chapter_title = li.find('a', {'class':'ch'}).text
                    date = li.find('span', {'class':'time'}).text.strip()
                    chapter_list.append([chapter_title, link, date])
            except AttributeError:
                pass
        try:
            updated = chapter_list[0][2]
        except:
            updated = 'N/A'
        manga_list = list(map(self.check_name_len, [title, author, rate, updated]))
        manga_list.insert(1, url)
        manga_list.insert(2, img)
        manga_list.append(chapter_list)
        return manga_list

    def date_format(self, time):
        """This method change the format of date in mangapark example from  April 19, 2020 into 20200619"""
        if "minutes ago" in time:
            time = int(time[:time.find("minutes ago")].strip()) / 1440
        elif "an hour ago" in time:
            time = 1 / 24
        elif "hours ago" in time:
            time = int(time[:time.find("hours ago")].strip()) / 24
        elif "days ago" in time:
            time = int(time[:time.find("days ago")].strip())
        elif "years ago" in time:
            time = int(time[:time.find("years ago")].strip()) * 365
        elif "a year ago" == time:
            time = 365
        return time

    def update(self):
        """Method to update all the mangalist for toonily website"""
        manga_list = list()
        file_path = os.path.join('..', 'mangapark.txt')
        with open(file_path, 'rb') as file:
            for line in file.readlines():
                line = line.decode('utf-8')
                url = line.split(',,')[1].strip()
                try:
                    manga = self.chapters(url)
                except AttributeError:
                    manga_name = line.split(',,')[0].strip()
                    print(manga_name)
                    self.delete_manga('manganelo', manga_name)
                    continue
                date_formated = self.date_format(manga[5])
                manga_list.append([manga, date_formated])
                random_time = round(random.uniform(0.1, .5), 2) # Add Random Delay from .1 to .5 sec
                time.sleep(random_time)
            sorted_list = list()
            for manga in sorted(manga_list, key=lambda date: date[1], reverse=False):
                sorted_list.append(manga[0])
        return sorted_list

    def release(self):
        """Method to check latest release for mangapark website"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        url = 'https://mangapark.net/'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        ls1 = soup.find('div', {'class': 'ls1'})
        item = ls1.find_all('div', {'class': 'item'})
        for num in range(10):
            try:
                title = item[num].ul.h3.a.text
                link = "https://mangapark.net" + item[num].ul.h3.a.get('href')
                img_link = item[num].a.img.get('src')
                img_link = self.url_name_check(img_link)
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link, path='imagerelease')
                img = img_title + '.jpg'
                author = 'N/A'
                rate = 'N/A'
                updated = item[num].ul.li.span.find_next_sibling('i').text
                checked_names = list(map(self.check_name_len, [title, author, rate]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                checked_names.append(updated)
                yield checked_names
            except GeneratorExit:
                return
            except AttributeError:
                pass

    def genres(self):
        """Method to get all the manga genres and its corresponding link and return a list of it"""
        url = 'https://mangapark.net/genre'
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        genres_list = list()
        items = soup.find('div', {'class': 'items'})
        for item in items.find_all('div', {'class': 'item'}):
            try:
                genre = item.a.text
                link = "https://mangapark.net" + item.a.get('href')
                genres_list.append([genre, link])
            except:
                print("Genre Error")
        return genres_list

    def manga_genres(self, url):
        """This method is to get all the manga in the genre list"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        user_agent = self.user_agents()
        headers = {'User-Agent': user_agent}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        pager = soup.find('ul', {'class':'pager'})
        page_list = list()
        try:
            for li in pager.find_all('li'):
                try:
                    if li.findChild().findChild().get("onchange"):
                        continue
                except AttributeError:
                    pass
                text = li.findChild().text
                if li.findChild().get('href'):
                    link = 'https://mangapark.net' + li.findChild().get('href')
                else:
                    link = li.findChild().get('href')
                page_list.append([text, link])
            yield page_list
        except GeneratorExit:
            return
        except AttributeError:
            pass
        ls1 = soup.find('div', {'class':'ls1'})
        try:
            try:
                for item in ls1.find_all('div', {'class':'item'}):
                    title = item.div.h3.a.text
                    link = 'https://mangapark.net' + item.div.h3.a.get("href")
                    img_link = item.a.img.get('src')
                    img_link = self.url_name_check(img_link)
                    img_title = self.check_filename_func(title)
                    self.add_image_func(img_title, img_link, path='imagerelease')
                    img = img_title + '.jpg'
                    author = 'N/A'
                    rate = item.div.span.small.text
                    updated = item.div.div.find_next_sibling('span').text
                    checked_names = list(map(self.check_name_len, [title, author, rate]))
                    checked_names.insert(1, link)
                    checked_names.insert(2, img)
                    checked_names.append(updated)
                    yield checked_names
            except GeneratorExit:
                return
            except AttributeError:
                pass
        except AttributeError:
            pass


if __name__ == '__main__':
    # manga = ManganeloScrap()
    # for i in manga.search('one piece'):
    #     print(i)
    # for _ in manga.chapters('https://manganelo.com/manga/ilsi12001567132882'):
    #     print(_)
    # print(manga.update())
    # manga.add_image('berserk', 'http://i998.imggur.net/one-piece/983/one-piece-13676137.jpg', temp=True)
    # manga.manganelo_chapter_view('https://manganelo.com/chapter/ilsi12001567132882/chapter_360')

    # manga = MangareaderScrap()
    # for i in manga.search('berserk'):
    #     print(i)
    # for _ in manga.chapters('https://www.mangareader.net/berserk'):
    #     print(_)
    # for _ in manga.release():
    #     print(_)

    # manga = ToonilyScrap()
    # for i in manga.search('sweet guy'):
    #     print(i)
    # for _ in manga.chapters('https://toonily.com/webtoon/sweet-guy/'):
    #     print(_)
    # for _ in manga.release():
    #     print(_)
    # print(manga.genres())
    # for _ in manga.manga_genres("https://toonily.com/webtoon-genre/action-webtoon/page/3/"):
    #     print(_)

    manga = MangaParkScrap()
    # for i in manga.search('one piece'):
    #     print(i)
    # for _ in manga.chapters('https://mangapark.net/manga/martial-peak'):
    #     print(_)
    # for _ in manga.release():
    #     print(_)
    # print(manga.genres())
    for _ in manga.manga_genres("https://mangapark.net/genre/demons"):
        print(_)

    # versioncheck = VersionCheck()
    # print(versioncheck.check())
