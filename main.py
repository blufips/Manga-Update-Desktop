#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from kivy.properties import ObjectProperty
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.utils import platform

from functools import partial
from settingsjson import settings_json
import threading
import os
import webbrowser
import database
import scrapper


Window.size = (400, 700)


class screen_tracker:
    """Class to track the screen for back click or escape.
        It Create a list of screen name"""
    def __init__(self):
        self.list_of_prev_screen = ['home']

    def add_track(self, name):
        """Method to add screen name"""
        self.list_of_prev_screen.append(name)


screen_track = screen_tracker()

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
        loading_label = Label(text='Please Wait\nGetting your Favorite\nManga', text_size=(Window.width*0.5,None), size_hint=(1,0.2), pos_hint={'x':0, 'top':0.7}, halign='center')
        loading_img = Image(source=loading_path, size_hint=(0.4,0.4), pos_hint={'center_x': 0.5, 'top':0.5}) # Loading Animation
        show_layout.add_widget(loading_label)
        show_layout.add_widget(loading_img)
        self.title = 'Loading Screen'
        self.content = show_layout


class HomeWindow(Screen):
    """Class for Home Screen it has update button to check all the update of manga"""
    def __init__(self, **kwargs):
        super(HomeWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.my_popup = PopupLoading()

    def check_update(self):
        """Method to check all the update manga"""
        self.ids.home_grid.clear_widgets()
        if self.app.phone.manga_list.list_manga(): # Check if manga storage is empty
            threading.Thread(target=self.manga_thread).start()
            self.my_popup.open()

    def manga_thread(self):
        """Method for threading"""
        self.list_manga = self.app.phone.manga_scrap.update()
        for manga in self.list_manga:
            self.app.phone.show_manga_list('home_window', 'home_grid', manga, self.app.phone.imagemanga, rows=4)
        self.my_popup.dismiss()


    def track_on(self, *args):
        """Method to add home screen to screen_track"""
        screen_track.add_track('home')


class SearchWindow(Screen):
    """Class for Search screen it has text input and ImageButton to search manga"""
    def __init__(self, **kwargs):
        super(SearchWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        self.my_popup = PopupLoading()

    def search(self):
        """Method to search Manga in search screen"""
        self.ids.search_grid.clear_widgets()
        self.search_input = self.ids.search_input.text
        threading.Thread(target=self.manga_thread).start()
        self.my_popup.open()

    def manga_thread(self):
        """Method for threading"""
        self.list_manga = self.app.phone.manga_scrap.search(self.search_input)
        for manga in self.list_manga:
            self.app.phone.show_manga_list('search_window', 'search_grid', manga, 'imagetemp', rows=4)
        self.my_popup.dismiss()

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
        title = self.my_manga[0][:25]
        author = self.my_manga[3]
        rate = self.my_manga[4]
        updated = self.my_manga[5]
        chapter_list = self.my_manga[6]
        my_img = AsyncImage(source=self.img_source, nocache=True, size_hint_y=None, allow_stretch=True, keep_ratio=True, height=Window.height*0.3)
        self.ids['display_grid'].add_widget(my_img)
        my_grid1 = GridLayout(cols=1)
        my_grid1.add_widget(WrappedLabel(text='[b]'+title+'[/b]', font_size='20dp', color=(0,0,0,1), markup=True))
        my_grid1.add_widget(WrappedLabel(text=author, font_size='15dp', color=(0,0,0,1)))
        my_grid1.add_widget(WrappedLabel(text='Rate: '+rate, font_size='15dp', color=(0,0,0,1)))
        my_grid1.add_widget(WrappedLabel(text='Updated: '+updated, font_size='15dp', color=(0,0,0,1)))
        self.ids['display_grid'].add_widget(my_grid1)
        recycle_list = list()
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
        self.ids['display_recycle'].data = [{'text': row[0], 'on_release': partial(self.open_browser, row[1])} for row in recycle_list]


    def open_browser(self, link, *args):
        """Method when call it will open the default browser"""
        webbrowser.open(link)


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
        self.bubb_addview = None
        self.bubb_viewdelete = None

    def show_manga_list(self, id_window, id_grid, manga, imgfolder, rows=3):
        """Method to call to display list of manga with Image and Info"""
        title = manga[0][:25]
        link = manga[1]
        img = manga[2]
        author = manga[3]
        rate = manga[4]
        img_path = lambda img: os.path.join(imgfolder, img)
        img_source = img_path(img)
        my_img = ImageButton(source= img_source, nocache=True, size_hint_y=None, allow_stretch=True, keep_ratio=True, height=Window.height*0.3)
        if id_grid == 'search_grid':
            my_img.bind(on_release=partial(self.show_bubble_addview, link, img_source, manga))
        elif id_grid == 'storage_grid':
            my_img.bind(on_release=partial(self.show_bubble_viewdelete, link, img_source, manga))
        else:
            my_img.bind(on_release=partial(self.switch_display, link, img_source))
        self.ids[id_window].ids[id_grid].add_widget(my_img)
        my_grid = GridLayout(rows=rows)
        my_grid.add_widget(WrappedLabel(text='[b]'+title+'[/b]', font_size='20dp', color=(0,0,0,1), markup=True))
        my_grid.add_widget(WrappedLabel(text=author, font_size='15dp', color=(0,0,0,1)))
        my_grid.add_widget(WrappedLabel(text='Rate: '+rate, font_size='15dp', color=(0,0,0,1)))
        if rows== 4:
            updated = manga[5]
            my_grid.add_widget(WrappedLabel(text='Updated: '+updated, font_size='15dp', color=(0,0,0,1)))
        self.ids[id_window].ids[id_grid].add_widget(my_grid)

    def show_bubble_addview(self, link, img_source, manga, *args):
        """Method to show popup bubble of addview in the screen of SearchWindow it can view and add the selected manga"""
        self.bubb_addview = add_view()
        self.bubb_addview.x = self.on_touch_pos_x
        self.bubb_addview.y = self.on_touch_pos_y - self.bubb_addview.height*1.1
        self.ids['search_window'].add_widget(self.bubb_addview)
        self.bubb_addview.ids['view_search'].bind(on_release=partial(self.switch_display, link, img_source, 'search_window'))
        self.bubb_addview.ids['add_search'].bind(on_release=partial(self.search_add_manga, manga))

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
        if self.bubb_addview != None: # Check for addview bubble
            if not Widget(pos=(self.bubb_addview.x, self.bubb_addview.y+self.bubb_addview.height*0.55), size=(self.bubb_addview.width, self.bubb_addview.height)).collide_point(*touch.pos):
                self.ids['search_window'].remove_widget(self.bubb_addview)
        if self.bubb_viewdelete != None: # Check for viewdelete ubble
            if not Widget(pos=(self.bubb_viewdelete.x, self.bubb_viewdelete.y+self.bubb_viewdelete.height*0.55), size=(self.bubb_viewdelete.width, self.bubb_viewdelete.height)).collide_point(*touch.pos):
                self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        self.on_touch_pos_x = touch.x
        self.on_touch_pos_y = touch.y

    def switch_display(self, link, img_source, id, *args):
        """Method when call it will switch the screen into displaymanga on youre seleted manga"""
        if id == 'search_window':
            self.ids['search_window'].remove_widget(self.bubb_addview)
        elif id == 'storage_window':
            self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        self.ids['_screen_manager'].current = 'displaymanga'
        self.ids['display_manga'].on_enter_screen(link, img_source)
        screen_track.add_track('displaymanga')

    def search_add_manga(self, manga, *args):
        """Method when call it will add the selected manga and update the StorageWindow"""
        self.ids['search_window'].remove_widget(self.bubb_addview)
        if not self.app.phone.manga_list.check_manga(manga[0]):
            self.app.phone.manga_list.add_manga(*manga[:5])
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
        if server == 'Manganelo':
            self.imagemanga = os.path.join('imagemanga', 'manganelo')
            self.manga_list = database.TextFile('manganelo', self.imagemanga)
            self.manga_scrap = scrapper.ManganeloScrap()
        # elif server == 'Mangaowl':
        #     self.imagemanga = os.path.join('imagemanga', 'mangaowl')
        #     self.manga_list = database.TextFile('mangaowl', self.imagemanga)
        #     self.manga_scrap = scrapper.MangaowlScrap()
        self.ids.storage_window.callback() # To update storage screen


class MyApp(App):
    def build(self):
        self.title = "Manga Updates By Israel Quimson"
        self.phone = Phone()
        self.init_check_folder()
        self.use_kivy_settings = False # Disable kivy default settings
        self.phone.check_servers()
        return self.phone

    def build_config(self, config):
        """Method to define default values in Settings"""
        config.setdefaults('basicsettings', {'Servers': 'Manganelo'})

    def build_settings(self, settings):
        """Method to add Panel in the Settings using import file as data"""
        settings.add_json_panel('Settings', self.config, data=settings_json)

    def on_config_change(self, config, section, key, value):
        """Method on change config value in the Settings"""
        if key == 'Servers':
            self.phone.check_servers()

    def init_check_folder(self):
        """Method to check if the folder exist and create it if not"""
        if not os.path.exists('imagetemp'):
            os.mkdir('imagetemp')
        if not os.path.exists(os.path.join('imagemanga', 'manganelo')):
            os.makedirs(os.path.join('imagemanga', 'manganelo'))
        if not os.path.exists(os.path.join('imagemanga', 'mangaowl')):
            os.makedirs(os.path.join('imagemanga', 'mangaowl'))

    def on_pause(self):
        return True # If True the App will not close when pause

    def on_stop(self):
        self.root.stop.set() # Set a stop signal for secondary python threads

if __name__ == '__main__':
    MyApp().run()
