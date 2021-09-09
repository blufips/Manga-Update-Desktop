from bs4 import BeautifulSoup, element
import cloudscraper
import time
import random
import database
import datetime
import os

scraper = cloudscraper.create_scraper()

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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        if len(response.content) < 500:
            response = scraper.get('http://static.mangahere.cc/v201906282/mangahere/images/nopicture.jpg')
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
            #user_agent = self.user_agents()
            #headers = {'User-Agent': user_agent}
            response = scraper.get(url)
            soup = BeautifulSoup(response.text, 'lxml')
            url_version = soup.find('div', text='Current Version').find_next_sibling('span').div.span.text
            if current_version != url_version:
                return True
            return False


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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        latest_manga_list = soup.find_all('div', {'class': 'd47'})
        for num in range(8):
            try:
                title = latest_manga_list[num].find('div', {'class': 'd53'}).text
                link = "https://www.mangareader.net/" + latest_manga_list[num].find('div', {'class': 'd53'}).a.get('href')
                updated = latest_manga_list[num].find('ul', {'class': 'd56'}).li.a.text
                response = scraper.get(link)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        manga_list = soup.find('div', {'class':'manga-list'})
        try:
            for item in manga_list.find_all('div', {'class':'item'}):
                title = item.table.tr.td.find_next_sibling('td').h2.a.get('title')
                link = "https://mangapark.net" + item.table.tr.td.find_next_sibling('td').h2.a.get('href')
                img_link = item.table.tr.td.a.img.get('src')
                img_link = self.url_name_check(img_link)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        """This method change the format of date in mangapark example from 1 hours ago into 20200619"""
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
        """Method to update all the mangalist for mangapark website"""
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
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


class MangahubScrap(MainFunc):
    """This class use to scrap Mangahub website"""

    def search(self, manga):
        """This method search for manga in mangahub website and return a generator of manga title, link, img, author and rating.
        It store all the search img into the imagetemp folded then delete it before search again"""
        image_temp_list = [f for f in os.listdir('imagetemp')]
        for f in image_temp_list:
            os.remove(os.path.join('imagetemp', f))
        manga = "%20".join(manga.split())
        url = 'https://mangahub.io/search?q=' + manga
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        manga_list = soup.find(id='mangalist')
        try:
            for media_manga in manga_list.find_all('div', {'class':'media-manga'}):
                title = media_manga.find('h4', {'class':'media-heading'}).a.text
                link = media_manga.find('h4', {'class':'media-heading'}).a.get("href")
                img_link = media_manga.find('div', {'class':'media-left'}).a.img.get('src')
                img_link = self.url_name_check(img_link)
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link)
                img = img_title + '.jpg'
                try:
                    author = media_manga.find('h4', {'class':'media-heading'}).small.text
                except AttributeError:
                    author = "N/A"
                updated = media_manga.find('div', {'class':'media-body'}).p.a.text
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
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        container_fluid = soup.find('div', {'class':'container-fluid'})
        title_elem = container_fluid.find('h1', {'class':'_3xnDj'})
        title = list()
        for elem in title_elem:
            if isinstance(elem, element.NavigableString):
                title.append(elem.strip())
        title = " ".join(title)
        img_title = self.check_filename_func(title)
        img = img_title + '.jpg'
        author = container_fluid.find('span', text="Author").find_next_sibling('span').text
        rate = "N/A"
        # updated = container_fluid.find('span', text="Latest").find_next_sibling('span').a.text
        noanim_content_tab = soup.find('div', id='noanim-content-tab')
        chapter_list = list()
        try:
            for li in noanim_content_tab.find_all('li', {'class':'_287KE'}):
                chapter_title = li.a.find('span', {'class':'_2IG5P'}).text
                link = li.a.get("href")
                date = li.a.find('small', {'class':'UovLc'}).text
                chapter_list.append([chapter_title, link, date])
            if not chapter_list:
                chapter_title = container_fluid.find('span', text="Latest").find_next_sibling('span').a.text
                link = container_fluid.find('span', text="Latest").find_next_sibling('span').a.get("href")
                date = datetime.datetime.now() - datetime.timedelta(days=1)
                date = date.strftime("%m-%d-%Y")
                chapter_list.append([chapter_title, link, date])
        except AttributeError:
            chapter_list = None
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
        """This method change the format of date in mangahub example from  1 hour ago or 10-31-2020 into 20200619"""
        if "just" in time:
            time = datetime.datetime.now().strftime("%Y%m%d")
        elif "less than an hour" in time:
            time = datetime.datetime.now() - datetime.timedelta(seconds=50)
            time = time.strftime("%Y%m%d")
        elif "hour ago" in time:
            time = datetime.datetime.now() - datetime.timedelta(hours=1)
            time = time.strftime("%Y%m%d")
        elif "hours ago" in time:
            hour = int(time[:time.find("hours ago")].strip())
            time = datetime.datetime.now() - datetime.timedelta(hours=hour)
            time = time.strftime("%Y%m%d")
        elif "Yesterday" in time:
            time = datetime.datetime.now() - datetime.timedelta(days=1)
            time = time.strftime("%Y%m%d")
        elif "days ago" in time:
            day = int(time[:time.find("days ago")].strip())
            time = datetime.datetime.now() - datetime.timedelta(days=day)
            time = time.strftime("%Y%m%d")
        elif "weeks ago" in time:
            week = int(time[:time.find("weeks ago")].strip())
            time = datetime.datetime.now() - datetime.timedelta(weeks=week)
            time = time.strftime("%Y%m%d")
        else:
            time = time.split("-")
            time = time[2]+time[0]+time[1]
        return int(time)

    def update(self):
        """Method to update all the mangalist for mangahub website"""
        manga_list = list()
        file_path = os.path.join('..', 'mangahub.txt')
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
        """Method to check latest release for mangahub website"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        url = 'https://mangahub.io'
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        count = 10
        ul_all = soup.find_all('ul', {'class':'_2FkQT'})
        for ul in ul_all:
            try:
                li = ul.find_all('li', {'class':'iqzwK'})
                for num in range(10):
                    if count > 0:
                        try:
                            title = li[num].find('h4', {'class':'media-heading'}).a.text
                            link = li[num].find('h4', {'class':'media-heading'}).a.get('href')
                            img_link = li[num].find('div', {'class':'media-left'}).a.img.get('src')
                            img_link = self.url_name_check(img_link)
                            img_title = self.check_filename_func(title)
                            self.add_image_func(img_title, img_link, path='imagerelease')
                            img = img_title + '.jpg'
                            author = "N/A"
                            rate = "N/A"
                            updated = li[num].find('h4', {'class':'media-heading'}).small.text
                            checked_names = list(map(self.check_name_len, [title, author, rate]))
                            checked_names.insert(1, link)
                            checked_names.insert(2, img)
                            checked_names.append(updated)
                            count -= 1
                            yield checked_names
                        except GeneratorExit:
                            return
                        except AttributeError:
                            pass
            except IndexError:
                print("Next UL")

    def genres(self):
        """Method to get all the manga genres and its corresponding link and return a list of it"""
        url = "https://mangahub.io/search"
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        genres_list = list()
        for item in soup.find_all('a', {'class':'genre-label'}):
            try:
                genre = item.text
                link = item.get('href')
                if [genre, link] not in genres_list:
                    genres_list.append([genre, link])
            except:
                print("Genre Error")
        return genres_list

    def manga_genres(self, url):
        """This method is to get all the manga in the genre list"""
        image_release_list = [f for f in os.listdir('imagerelease')]
        for f in image_release_list:
            os.remove(os.path.join('imagerelease', f))
        #user_agent = self.user_agents()
        #headers = {'User-Agent': user_agent}
        response = scraper.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        ul_pager = soup.find('ul',{'class':'pager'})
        page_list = list()
        try:
            for li in ul_pager.find_all('li'):
                text = li.a.text
                link = li.a.get('href')
                page_list.append([text, link])
            yield page_list
        except GeneratorExit:
            return
        except AttributeError:
            pass
        mangalist = soup.find('div', id='mangalist')
        try:
            for item in mangalist.find_all('div',{'class':'_1KYcM'}):
                title = item.find('h4',{'class':'media-heading'}).a.text
                link = item.find('h4',{'class':'media-heading'}).a.get('href')
                img_link = item.find('div',{'class':'media-left'}).a.img.get('src')
                img_link = self.url_name_check(img_link)
                img_title = self.check_filename_func(title)
                self.add_image_func(img_title, img_link, path='imagerelease')
                img = img_title + '.jpg'
                updated = item.find('div', {'class':'media-body'}).p.a.text
                try:
                    author = item.find('h4', {'class':'media-heading'}).small.text
                except AttributeError:
                    author = "N/A"
                rate = 'N/A'
                checked_names = list(map(self.check_name_len, [title, author, rate]))
                checked_names.insert(1, link)
                checked_names.insert(2, img)
                checked_names.append(updated)
                yield checked_names
        except GeneratorExit:
            return
        except AttributeError:
            pass


if __name__ == '__main__':
    # manga = MangareaderScrap()
    # for i in manga.search('berserk'):
    #     print(i)
    # for _ in manga.chapters('https://www.mangareader.net/berserk'):
    #     print(_)
    # for _ in manga.release():
    #     print(_)

    # manga = MangaParkScrap()
    # for i in manga.search('one piece'):
    #     print(i)
    # for _ in manga.chapters('https://mangapark.net/manga/martial-peak'):
    #     print(_)
    # for _ in manga.release():
    #     print(_)
    # print(manga.genres())
    # for _ in manga.manga_genres("https://mangapark.net/genre/demons"):
    #     print(_)

    manga = MangahubScrap()
    # for i in manga.search('record of the war god'):
    #     print(i)
    # for _ in manga.chapters('https://mangahub.io/manga/record-of-the-war-god'):
    #     print(_)
    # for _ in manga.update():
    #     print(_)
    for _ in manga.release():
        print(_)
    # print(manga.genres())
    # for _ in manga.manga_genres("https://mangahub.io/genre/adult/page/2"):
    #     print(_)

    # versioncheck = VersionCheck()
    # print(versioncheck.check())
