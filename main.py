#!/usr/bin/env python
# -*- coding: utf-8 -*-
import kivy
kivy.require('1.11.1')

from kivmob import KivMob, TestIds

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image, AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.bubble import Bubble
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.utils import platform
from kivy.graphics.vertex_instructions import Rectangle, Line
from kivy.graphics.context_instructions import Color
from kivy.metrics import dp

from functools import partial
from settingsjson import settings_json
import threading
import requests
import os
import webbrowser
import database
import scrapper

def open_browser(link, *args):
    """Function when call it will open the default browser"""
    webbrowser.open(link)

class screen_tracker:
    """Class to track the screen for back click or escape.
        It Create a list of screen name"""
    def __init__(self):
        self.list_of_prev_screen = ['home']

    def add_track(self, name):
        """Method to add screen name"""
        self.list_of_prev_screen.append(name)


screen_track = screen_tracker()

class WrapButton(Button):
    """Class to use to Modified BUtton"""
    pass

class WrappedLabel(Label):
    """Class use to Modified Label"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x:
            self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


class add_view(Bubble):
    """Class for popup bubble in the search screen that add manga in storage or view the manga and switch to displaymanga screen"""
    pass


class view_delete(Bubble):
    """Class for popup bubble in the storage screen that delete the manga or view the manga and switch to displaymanga screen"""
    pass


class ImageButton(ButtonBehavior, AsyncImage):
    """Class to create Clickable Image or Image with button behaviors"""
    pass


class PopupLoading(Popup):
    """Class to create POPUP window for loading screen"""
    def __init__(self, **kwargs):
        super(PopupLoading, self).__init__(**kwargs)
        show_layout = FloatLayout()
        loading_path = os.path.join('icon', 'loading.zip')
        loading_label = Label(text="Please Wait\nGetting your Favorite\nManga", text_size=(Window.width*0.5,None), size_hint=(1,0.2), pos_hint={'x':0, 'top':0.7}, halign='center')
        loading_img = Image(source=loading_path, size_hint=(0.4,0.4), pos_hint={'center_x': 0.5, 'top':0.5}) # Loading Animation
        show_layout.add_widget(loading_label)
        show_layout.add_widget(loading_img)
        self.title = "Loading Screen"
        self.content = show_layout

class PopupUpdate(Popup):
    """Class to create POPUP window for Version Update screen"""
    def __init__(self, **kwargs):
        super(PopupUpdate, self).__init__(**kwargs)
        self.app = App.get_running_app()
        show_layout = FloatLayout()
        update_label = Label(text="New Update has Rlease", text_size=(Window.width*0.5,None), size_hint=(1,0.2), pos_hint={'x':0, 'top':0.7}, halign='center')
        update_button = Button(text='OK', size_hint=(0.2,0.1), pos_hint={'center_x': 0.5, 'top':0.5})
        update_button.bind(on_release=self.browser)
        show_layout.add_widget(update_label)
        show_layout.add_widget(update_button)
        self.title = "Version Check"
        self.content = show_layout

    def browser(self, *args):
        """Method to open browser and close the Popup"""
        url = "https://play.google.com/store/apps/details?id=org.blufips.mangaupdate"
        open_browser(url)
        self.app.phone.version_popup.dismiss()


class HomeWindow(Screen):
    """Class for Home Screen it has update button to check all the update of manga"""
    def __init__(self, **kwargs):
        super(HomeWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.my_popup = PopupLoading()
        self.thread_status = 'latest_release' # Show latest release on startup

    def callback(self):
        """Method for calling the thread and use to start threading"""
        Clock.schedule_once(self.call_thread, 0.6)

    def call_thread(self, *args):
        """Method to start the thread"""
        self.ids.home_grid.clear_widgets()
        self.thread_continue = False # Set the thread to false to start threading
        threading.Thread(target=self.manga_thread).start()

    def check_update(self):
        """Method to check all the update manga"""
        self.thread_status = 'check_update' # Set the thread status to check update
        self.thread_continue = True # Set the thread to true to stop threading
        if self.app.phone.manga_list.list_manga(): # Check if manga storage is empty
            self.callback()
            self.my_popup.open()

    def latest_release(self, *args):
        """Method to check latest release"""
        self.thread_continue = True # Set the thread to true to stop threading
        self.thread_status = 'latest_release' # Set the thread status to latest release
        self.callback()

    def manga_genres(self):
        """Method to get all manga genres"""
        self.thread_status = 'manga_genres' # Set the thread status to manga genres
        self.thread_continue = True # Set the thread to true to stop threading
        self.callback()
        self.my_popup.open()

    def manga_genres_display(self):
        """Method to display the list of manga genres in button"""
        layout = GridLayout(cols=3, size_hint_y=None, height=Window.height*0.1*len(self.list_genres)/3+Window.height*0.1)
        for genre in self.list_genres:
            button = WrapButton(text=genre[0], size_hint_y=None, height=Window.height*0.1)
            button.bind(on_press=partial(self.manga_genres_button, genre[1]))
            layout.add_widget(button)
        self.ids.home_grid.add_widget(layout)

    def manga_genres_button(self, link, *args):
        """Method to call for the manga genres button"""
        self.ids.home_grid.clear_widgets()
        self.thread_status = 'manga_genres_display' # Set the thread status to manga genres display
        threading.Thread(target=partial(self.manga_thread,link)).start()

    def add_page_nav(self):
        """This method add button for page nav in the bottom of home_grid"""
        layout = GridLayout(cols=5, size_hint_y=None, height=Window.height*0.1*len(self.page_list)/5+Window.height*0.1)
        for page in self.page_list:
            text, link = page
            if link: # Check if the button has link
                button = WrapButton(text=text, height=Window.height*0.1)
                button.bind(on_press=partial(self.manga_genres_button, link))
                layout.add_widget(button)
            else: # if the button dont have link it is the current page
                button = WrapButton(text=text, height=Window.height*0.1, background_color=(0.0, 0.0, 1.0, 1.0))
                layout.add_widget(button)
        self.ids.home_grid.add_widget(layout)

    def manga_thread(self, *args):
        """Method for threading"""
        if self.thread_status == 'latest_release': # Check if the threading is latest_release
            self.list_manga = self.app.phone.manga_scrap.release()
            for manga in self.list_manga:
                if self.thread_continue:
                    break
                self.app.phone.show_manga_list('home_window', 'home_grid', manga, 'imagerelease', rows=4)
        elif self.thread_status == 'check_update': # Check if the threading is check_update
            self.app.ads.show_interstitial() # Show interstitial Ads
            self.list_manga = self.app.phone.manga_scrap.update()
            for manga in self.list_manga:
                self.app.phone.show_manga_list('home_window', 'home_grid', manga, self.app.phone.imagemanga, rows=4, check_update=True)
            self.my_popup.dismiss()
        elif self.thread_status == 'manga_genres': # Check if the threading manga_genres
            self.list_genres = self.app.phone.manga_scrap.genres()
            self.manga_genres_display()
            self.my_popup.dismiss()
        elif self.thread_status == 'manga_genres_display': # Check if the threading manga_genres_display
            link = args[0]
            self.list_manga = self.app.phone.manga_scrap.manga_genres(link)
            pages = True
            for manga in self.list_manga:
                if self.thread_continue:
                    break
                if pages == True: # The generator 1st return the page list
                    self.page_list = manga
                    pages = False
                else: # The rest return by generator is the manga
                    self.app.phone.show_manga_list('home_window', 'home_grid', manga, 'imagerelease', rows=4)
            if not self.thread_continue:
                self.add_page_nav()

    def track_on(self, *args):
        """Method to add home screen to screen_track"""
        screen_track.add_track('home')


class SearchWindow(Screen):
    """Class for Search screen it has text input and ImageButton to search manga"""
    def __init__(self, **kwargs):
        super(SearchWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.my_popup = PopupLoading()

    def callback(self):
        """Method to call if the search button is press"""
        self.thread_continue = True # Signal to stop the current thread
        Clock.schedule_once(self.search, 0.6)

    def search(self, *args):
        """Method to search Manga in search screen"""
        self.ids.search_grid.clear_widgets()
        self.search_input = self.ids.search_input.text
        self.thread_continue = False
        threading.Thread(target=self.manga_thread).start()

    def manga_thread(self):
        """Method for threading"""
        self.list_manga = self.app.phone.manga_scrap.search(self.search_input)
        for manga in self.list_manga:
                self.app.phone.show_manga_list('search_window', 'search_grid', manga, 'imagetemp', rows=4)
                if self.thread_continue: # Check if the thread need to stop
                    break

    def track_on(self, *args):
        """Method to add search screen to screen_track"""
        screen_track.add_track('search')


class StorageWindow(Screen):
    """Class for Storage screen to display all favorite manga you can view and delete it"""
    def __init__(self, **kwargs):
        super(StorageWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self.callback)

    def callback(self, *args):
        """Method to callback at first instant of the App to load the list of manga"""
        self.ids.storage_grid.clear_widgets()
        self.list_manga = self.app.phone.manga_list.list_manga()
        for manga in self.list_manga:
            self.app.phone.show_manga_list('storage_window','storage_grid', manga, self.app.phone.imagemanga)

    def track_on(self, *args):
        """Method to add storage screen to screen_track"""
        screen_track.add_track('storage')


class DisplayMangaWindow(Screen):
    """Class for DisplayManga screen it will display list of manga chapters"""
    def __init__(self, **kwargs):
        super(DisplayMangaWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.my_popup = PopupLoading()

    def on_enter_screen(self, link, img_source):
        """Method to call when entering DisplayMangaWindow"""
        self.link = link
        self.img_source = img_source
        threading.Thread(target=self.manga_thread).start()
        self.my_popup.open()

    def manga_thread(self):
        self.my_manga = self.app.phone.manga_scrap.chapters(self.link)
        self.manga_view()
        self.my_popup.dismiss()

    def manga_view(self):
        """Method to display list of manga chapters by using recycleview"""
        self.ids['display_grid'].clear_widgets()
        title = self.my_manga[0]
        author = self.my_manga[3]
        rate = self.my_manga[4]
        updated = self.my_manga[5]
        chapter_list = self.my_manga[6]
        my_img = AsyncImage(source=self.img_source, nocache=True, size_hint_y=None, allow_stretch=True, keep_ratio=True, height=Window.height*0.3)
        self.ids['display_grid'].add_widget(my_img)
        my_grid1 = GridLayout(cols=1)
        my_grid1.add_widget(WrappedLabel(text='[b]'+title+'[/b]', font_size='15sp', color=self.app.manga_text_color, markup=True))
        my_grid1.add_widget(WrappedLabel(text='Author: '+author, font_size='12sp', color=self.app.manga_text_color))
        my_grid1.add_widget(WrappedLabel(text='Rate: '+rate, font_size='12sp', color=self.app.manga_text_color))
        my_grid1.add_widget(WrappedLabel(text='Updated: '+updated, font_size='12sp', color=self.app.manga_text_color))
        self.ids['display_grid'].add_widget(my_grid1)
        recycle_list = list()
        if chapter_list:
            for chapters in chapter_list:
                chapter = chapters[0].strip()
                chapter_edit = chapter[:20]
                link = chapters[1]
                date = chapters[2]
                if len(chapter_edit) == 20:
                    text = chapter_edit + '...' + ' '*10 + date
                else:
                    text = chapter_edit + ' '*(30-len(chapter_edit)) + ' '*10 + date
                recycle_list.append([text, link]) # Create list of data for recycleview
            self.ids['display_recycle'].data = [{'text': row[0], 'on_release': partial(open_browser, row[1])} for row in recycle_list]


class WindowManager(ScreenManager):
    """Class of ScreenManager to manage all of the screens"""
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.back_click) # Use to bind keyboard

    def back_click(self, windows, key, *args):
        """Method to bind esc or back button if return False the program will exit"""
        if key == 27:
            return self.go_back()
        return False # Return False to close the App

    def go_back(self):
        """Method to check the previous screen using screen_track"""
        if screen_track.list_of_prev_screen:
            screen_track.list_of_prev_screen.pop() # Remove the last added screen_track
            if screen_track.list_of_prev_screen: # Check if screen_track is not empty
                self.current = screen_track.list_of_prev_screen[-1] # Change the screen into privious visit screen
                return True # Return True to not close the App
        return False


class Phone(FloatLayout):

    stop = threading.Event() # Properties to stop all the thrading

    def __init__(self, **kwargs):
        super(Phone, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.bubb_addview_home = None
        self.bubb_addview_search = None
        self.bubb_viewdelete = None
        self.version_popup = PopupUpdate()
        Clock.schedule_once(self.version_check)

    def show_manga_list(self, id_window, id_grid, manga, imgfolder, rows=3, check_update=False):
        """Method to call to display list of manga with Image and Info"""
        title = manga[0][:25]
        link = manga[1]
        img = manga[2]
        author = manga[3]
        rate = manga[4]
        img_path = lambda img: os.path.join(imgfolder, img)
        img_source = img_path(img)
        my_img = ImageButton(source= img_source, nocache=True, size_hint_y=None, allow_stretch=True, keep_ratio=True, height=Window.height*0.25)
        self.check_update_bool = check_update
        if id_grid == 'home_grid' and self.check_update_bool == True: # Check if the show_manga_list will display on check update
            my_img.bind(on_release=partial(self.switch_display, link, img_source, 'home_window'))
        elif id_grid == 'home_grid':
            my_img.bind(on_release=partial(self.show_bubble_addview_home, link, img_source, manga))
        elif id_grid == 'search_grid':
            my_img.bind(on_release=partial(self.show_bubble_addview_search, link, img_source, manga))
        elif id_grid == 'storage_grid':
            my_img.bind(on_release=partial(self.show_bubble_viewdelete, link, img_source, manga))
        else:
            my_img.bind(on_release=partial(self.switch_display, link, img_source))
        my_grid1 = GridLayout(cols=2, size_hint_y=None, height=my_img.height)
        my_grid2 = GridLayout(rows=rows)
        my_grid2.add_widget(WrappedLabel(text='[b]'+title+'[/b]', font_size='15sp', color=self.app.manga_text_color, markup=True))
        my_grid2.add_widget(WrappedLabel(text='Author: '+author, font_size='12sp', color=self.app.manga_text_color))
        my_grid2.add_widget(WrappedLabel(text='Rate: '+rate, font_size='12sp', color=self.app.manga_text_color))
        if rows== 4:
            updated = manga[5]
            my_grid2.add_widget(WrappedLabel(text='Updated: '+updated, font_size='12sp', color=self.app.manga_text_color))
        my_grid1.add_widget(my_img)
        my_grid1.add_widget(my_grid2)
        self.ids[id_window].ids[id_grid].add_widget(my_grid1)

    def show_bubble_addview_home(self, link, img_source, manga, *args):
        """Method to show popup bubble of addview in the screen of HomeWindow it can view and add the selected manga"""
        self.bubb_addview_home = add_view()
        self.bubb_addview_home.x = self.on_touch_pos_x
        self.bubb_addview_home.y = self.on_touch_pos_y - self.bubb_addview_home.height*1.1
        self.ids['home_window'].add_widget(self.bubb_addview_home)
        self.bubb_addview_home.ids['view_search'].bind(on_release=partial(self.switch_display, link, img_source, 'home_window'))
        self.bubb_addview_home.ids['add_search'].bind(on_release=partial(self.search_add_manga, manga, 'home_window'))

    def show_bubble_addview_search(self, link, img_source, manga, *args):
        """Method to show popup bubble of addview in the screen of SearchWindow it can view and add the selected manga"""
        self.bubb_addview_search = add_view()
        self.bubb_addview_search.x = self.on_touch_pos_x
        self.bubb_addview_search.y = self.on_touch_pos_y - self.bubb_addview_search.height*1.1
        self.ids['search_window'].add_widget(self.bubb_addview_search)
        self.bubb_addview_search.ids['view_search'].bind(on_release=partial(self.switch_display, link, img_source, 'search_window'))
        self.bubb_addview_search.ids['add_search'].bind(on_release=partial(self.search_add_manga, manga, 'search_window'))

    def show_bubble_viewdelete(self, link, img_source, manga, *args):
        """Method to show popup bubble of view_delete in the StorageWindow it can view and delete the selected manga"""
        self.bubb_viewdelete = view_delete()
        self.bubb_viewdelete.x = self.on_touch_pos_x
        self.bubb_viewdelete.y = self.on_touch_pos_y - self.bubb_viewdelete.height*1.1
        self.ids['storage_window'].add_widget(self.bubb_viewdelete)
        self.bubb_viewdelete.ids['view_storage'].bind(on_release=partial(self.switch_display, link, img_source, 'storage_window'))
        self.bubb_viewdelete.ids['delete_storage'].bind(on_release=partial(self.storage_delete_manga, manga))

    def on_touch_down(self, touch):
        """Method to remove the popup bubble"""
        super().on_touch_down(touch)
        if self.bubb_addview_home != None: # Check for addview_home bubble
            if not Widget(pos=(self.bubb_addview_home.x, self.bubb_addview_home.y+self.bubb_addview_home.height*0.55), size=(self.bubb_addview_home.width, self.bubb_addview_home.height)).collide_point(*touch.pos):
                self.ids['home_window'].remove_widget(self.bubb_addview_home)
        if self.bubb_addview_search != None: # Check for addview_search bubble
            if not Widget(pos=(self.bubb_addview_search.x, self.bubb_addview_search.y+self.bubb_addview_search.height*0.55), size=(self.bubb_addview_search.width, self.bubb_addview_search.height)).collide_point(*touch.pos):
                self.ids['search_window'].remove_widget(self.bubb_addview_search)
        if self.bubb_viewdelete != None: # Check for viewdelete ubble
            if not Widget(pos=(self.bubb_viewdelete.x, self.bubb_viewdelete.y+self.bubb_viewdelete.height*0.55), size=(self.bubb_viewdelete.width, self.bubb_viewdelete.height)).collide_point(*touch.pos):
                self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        self.on_touch_pos_x = touch.x
        self.on_touch_pos_y = touch.y

    def switch_display(self, link, img_source, id, *args):
        """Method when call it will switch the screen into displaymanga on youre seleted manga"""
        if id == 'home_window' and self.check_update_bool == False:
            self.ids['home_window'].remove_widget(self.bubb_addview_home)
        elif id == 'search_window':
            self.ids['search_window'].remove_widget(self.bubb_addview_search)
        elif id == 'storage_window':
            self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        self.ids['_screen_manager'].current = 'displaymanga'
        self.ids['display_manga'].on_enter_screen(link, img_source)
        screen_track.add_track('displaymanga')

    def search_add_manga(self, manga, id, *args):
        """Method when call it will add the selected manga and update the StorageWindow"""
        if id == 'home_window':
            self.ids[id].remove_widget(self.bubb_addview_home)
        else:
            self.ids[id].remove_widget(self.bubb_addview_search)
        if not self.app.phone.manga_list.check_manga(manga[0]):
            self.app.phone.manga_list.add_manga(*manga[:5], id)
            self.ids['storage_window'].ids['storage_grid'].clear_widgets()
            self.ids['storage_window'].callback()

    def storage_delete_manga(self, manga, *args):
        """Method when call it will delete the selected manga and update the StorageWindow """
        self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        if self.app.phone.manga_list.check_manga(manga[0]):
            try:
                self.app.phone.manga_list.del_manga(manga[0])
            except:
                print('No file')
            self.ids['storage_window'].ids['storage_grid'].clear_widgets()
            self.ids['storage_window'].callback()

    def check_servers(self):
        """Method use to check the server in the settings"""
        server = self.app.config.get('basicsettings', 'Servers') # Get the value of config Servers option
        if server == 'Mangahub':
            self.imagemanga = os.path.join('..', 'imagemanga', 'mangahub')
            self.manga_list = database.TextFile('mangahub', self.imagemanga)
            self.manga_scrap = scrapper.MangahubScrap()
            self.restore_default() # To clear widget, go to home screen and show latest release
        # elif server == 'Mangareader':
        #     self.imagemanga = os.path.join('..', 'imagemanga', 'mangareader')
        #     self.manga_list = database.TextFile('mangareader', self.imagemanga)
        #     self.manga_scrap = scrapper.MangareaderScrap()
        #     self.restore_default()
        # elif server == "Mangapark":
        #     self.imagemanga = os.path.join('..', 'imagemanga', 'mangapark')
        #     self.manga_list = database.TextFile('mangapark', self.imagemanga)
        #     self.manga_scrap = scrapper.MangaParkScrap()
        #     self.restore_default()
    def restore_default(self):
        """Method to restore the default when changing the server"""
        self.ids['home_window'].ids['home_grid'].clear_widgets()
        self.ids['search_window'].ids['search_grid'].clear_widgets()
        self.ids['_screen_manager'].current = 'home'
        self.ids['home_window'].latest_release()
        self.ids.storage_window.callback() # To update storage screen

    def version_check(self, *args):
        """Method to check if the version is updated"""
        version_check = scrapper.VersionCheck()
        try:
            if version_check.check():
                self.version_popup.open()
        except:
            pass


class MyApp(App):
    def __init__(self, **kwargs):
        super(MyApp, self).__init__(**kwargs)
        app_id = 'ca-app-pub-8089433413136772~9573406997'
        # app_id = TestIds.APP
        self.ads = KivMob(app_id)
        banner_id = 'ca-app-pub-8089433413136772/5023610284'
        # banner_id = TestIds.BANNER
        interstitial_id = 'ca-app-pub-8089433413136772/8617959106'
        # interstitial_id = TestIds.INTERSTITIAL
        self.ads.new_banner(banner_id, top_pos=True)
        self.ads.new_interstitial(interstitial_id)
        self.show_ads()
        self.ads_created = True
        self.manga_text_color = (0, 0, 0, 1)
        self.start_up = True # Use in theme_color

    def build(self):
        self.title = "Manga Updates By Israel Quimson"
        self.phone = Phone()
        self.init_check_folder()
        self.use_kivy_settings = False # Disable kivy default settings
        self.phone.check_servers()
        self.theme_color()
        Clock.schedule_interval(self.check_internet, 30)
        return self.phone

    def show_ads(self):
        """Method to create ads"""
        self.ads.request_banner()
        self.ads.show_banner()

    def check_internet(self, *args):
        """Method to check internet"""
        url = 'https://1.1.1.1' # url to check
        timeout = 5 # timeout in seconds
        try:
            r = requests.head(url, timeout=timeout) # check the connection
            if not self.ads_created: # check if the ads is created
                self.show_ads() # Call this method to create ads
                self.ads_created = True # set the ads_created to true
        except:
            self.ads_created = False # If no internet set the ads created to false

    def build_config(self, config):
        """Method to define default values in Settings"""
        with open('version.txt', 'r') as file:
            version_num = file.read()
        config.setdefaults('basicsettings', {'Servers': 'Mangahub', 'Version': version_num, 'darkmode': False})

    def build_settings(self, settings):
        """Method to add Panel in the Settings using import file as data"""
        settings.add_json_panel('Settings', self.config, data=settings_json)

    def on_config_change(self, config, section, key, value):
        """Method on change config value in the Settings"""
        if key == 'Servers':
            self.phone.check_servers()
        if key == 'darkmode':
            self.theme_color()

    def theme_color(self):
        """Method to set the theme color and change the theme to dark mode"""
        mode = self.config.get('basicsettings', 'darkmode') # Get the value of config darkmode boolean
        if mode == '1': # Dark mode
            self.manga_text_color = (1, 1, 1, 1)
            self.nav_text_color = (1, 1, 1, 1)
            self.bg1_color = (68/255, 68/255, 68/255, 1)
            self.line_color = (0, 0, 0, 1)
            self.nav_bg_color = (51/255, 51/255, 51/255, 1)
            self.storage_line_color = (1, 1, 1, 1)
        else: # White mode
            self.manga_text_color = (0, 0, 0, 1)
            self.nav_text_color = (0, 0, 0, 1)
            self.bg1_color = (228/255, 241/255, 254/255, 1)
            self.line_color = (1, 1, 1, 1)
            self.nav_bg_color = (1, 1, 1, 1)
            self.storage_line_color = (0, 0, 0, 1)
        with self.phone.ids.phone_float.canvas.before:
            Color(self.bg1_color[0], self.bg1_color[1], self.bg1_color[2], self.bg1_color[3])
            Rectangle(size=Window.size)
        with self.phone.ids.phone_anchor.canvas.before:
            Color(self.line_color[0], self.line_color[1], self.line_color[2], self.line_color[3])
            Line(points=(0, Window.height*0.08, Window.width, Window.height*0.08))
        with self.phone.ids.phone_grid.canvas.before:
            Color(self.nav_bg_color[0], self.nav_bg_color[1], self.nav_bg_color[2], self.nav_bg_color[3])
            Rectangle(size=(Window.width, Window.height*0.08), pos=self.phone.pos)
        with self.phone.ids.home_window.ids.home_float.canvas.before:
            Color(self.bg1_color[0], self.bg1_color[1], self.bg1_color[2], self.bg1_color[3])
            Rectangle(size=Window.size)
        with self.phone.ids.search_window.ids.search_float.canvas.before:
            Color(self.bg1_color[0], self.bg1_color[1], self.bg1_color[2], self.bg1_color[3])
            Rectangle(size=Window.size)
        with self.phone.ids.storage_window.ids.storage_float.canvas.before:
            Color(self.bg1_color[0], self.bg1_color[1], self.bg1_color[2], self.bg1_color[3])
            Rectangle(size=Window.size)
        with self.phone.ids.storage_window.ids.storage_float.canvas:
            Color(self.storage_line_color[0], self.storage_line_color[1], self.storage_line_color[2], self.storage_line_color[3])
            height = (Window.height - dp(self.ads.determine_banner_height())) * 0.92 * 0.9
            Line(points=(0, height, Window.width, height))
        with self.phone.ids.display_manga.ids.displaymanga_float.canvas.before:
            Color(self.bg1_color[0], self.bg1_color[1], self.bg1_color[2], self.bg1_color[3])
            Rectangle(size=Window.size)
        self.phone.ids.storage_window.ids.storage_label.color = self.manga_text_color
        self.phone.ids.phone_home.color = self.nav_text_color
        self.phone.ids.phone_search.color = self.nav_text_color
        self.phone.ids.phone_favorite.color = self.nav_text_color
        self.phone.ids.phone_settings.color = self.nav_text_color
        if not self.start_up: # Check if startup
            self.phone.restore_default()
        else:
            self.start_up = False

    def close_settings(self, *settings):
        """Method fire when the close button in settings"""
        super(MyApp, self).close_settings(settings)
        self.ads.show_banner()

    def init_check_folder(self):
        """Method to check if the folder exist and create it if not"""
        if not os.path.exists('imagetemp'):
            os.mkdir('imagetemp')
        if not os.path.exists('imagerelease'):
            os.mkdir('imagerelease')
        if not os.path.exists(os.path.join('..', 'imagemanga', 'mangahub')):
            os.makedirs(os.path.join('..', 'imagemanga', 'mangahub'))
        # if not os.path.exists(os.path.join('..', 'imagemanga', 'mangareader')):
        #     os.makedirs(os.path.join('..', 'imagemanga', 'mangareader'))
        # if not os.path.exists(os.path.join('..', 'imagemanga', 'mangapark')):
        #     os.makedirs(os.path.join('..', 'imagemanga', 'mangapark'))

    def on_pause(self):
        return True # If True the App will not close when pause

    def on_stop(self):
        self.root.stop.set() # Set a stop signal for secondary python threads

    def on_resume(self):
        self.ads.request_interstitial()


if __name__ == '__main__':
    MyApp().run()
