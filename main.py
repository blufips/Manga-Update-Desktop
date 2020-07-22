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
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import platform

from functools import partial
import threading
import os
import webbrowser
import database
import scrapper


imagemanga = os.path.join('imagemanga', 'manganelo')
manga_list = database.TextFile('manganelo', imagemanga)
manga_scrap = scrapper.ManganeloScrap()

Window.size = (400, 700)

class screen_tracker:
    """Class to track the screen.
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
    pass


class view_delete(Bubble):
    pass


class ImageButton(ButtonBehavior, AsyncImage):
    """Class to create Clickable Image or Image with button behaviors"""
    pass


class HomeWindow(Screen):
    """Class for Home Screen it has update button to check all the update of manga"""
    def __init__(self, **kwargs):
        super(HomeWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def check_update(self):
        """Method to check all the update manga"""
        self.ids.home_grid.clear_widgets()
        if manga_list.list_manga(): # Check if manga storage is empty
            threading.Thread(target=self.manga_thread).start()
            Clock.schedule_once(self.show_popup_loading)

    def manga_thread(self):
        """Method for threading"""
        self.list_manga = manga_scrap.update()
        for manga in self.list_manga:
            self.app.phone.show_manga_list('home_window', 'home_grid', manga, rows=4)
        self.my_popup.dismiss()

    def show_popup_loading(self, *args):
        """Method to create POPUP window for loading screen"""
        self.show_layout = FloatLayout()
        loading_path = os.path.join('icon', 'loading.zip')
        self.loading_label = Label(text='Please Wait', text_size=(Window.width*0.5,None), size_hint=(1,0.2), pos_hint={'x':0, 'top':0.7}, halign='center', color=(0,0,0,1))
        self.loading_img = Image(source=loading_path, size_hint=(0.1,0.1), pos_hint={'center_x': 0.5, 'top':0.5})
        self.show_layout.add_widget(self.loading_label)
        self.show_layout.add_widget(self.loading_img)
        self.my_popup = Popup(title='Loading Screen', content=self.show_layout)
        self.my_popup.open()

    def track_on(self, *args):
        """Method to add home screen to screen_track"""
        screen_track.add_track('home')


class SearchWindow(Screen):
    def __init__(self, **kwargs):
        super(SearchWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def search(self):
        """Method to search Manga in search screen"""
        self.ids.search_grid.clear_widgets()
        self.search_input = self.ids.search_input.text
        threading.Thread(target=self.manga_thread).start()

    def manga_thread(self):
        """Method for threading"""
        self.list_manga = manga_scrap.search(self.search_input)
        for manga in self.list_manga:
            self.app.phone.show_manga_list('search_window', 'search_grid', manga, rows=4, imgfolder='imagetemp')

    def track_on(self, *args):
        """Method to add search screen to screen_track"""
        screen_track.add_track('search')


class StorageWindow(Screen):
    def __init__(self, **kwargs):
        super(StorageWindow, self).__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self.callback)

    def callback(self, *args):
        """Method to callback at first instant of the App to load the list of manga"""
        self.ids.storage_grid.clear_widgets()
        self.list_manga = manga_list.list_manga()
        for manga in self.list_manga:
            self.app.phone.show_manga_list('storage_window','storage_grid', manga)

    def track_on(self, *args):
        """Method to add storage screen to screen_track"""
        screen_track.add_track('storage')


class SettingsWindow(Screen):
    pass


class DisplayMangaWindow(Screen):
    def manga_view(self, link, img_source):
        self.ids['display_grid'].clear_widgets()
        self.ids['display_box'].clear_widgets()
        self.my_manga = manga_scrap.chapters(link)
        title = self.my_manga[0][:25]
        author = self.my_manga[3]
        rate = self.my_manga[4]
        updated = self.my_manga[5]
        chapter_list = self.my_manga[6]
        my_img = Image(source=img_source, size_hint_y=None, allow_stretch=True, keep_ratio=True, height=Window.height*0.3)
        self.ids['display_grid'].add_widget(my_img)
        my_grid1 = GridLayout(cols=1)
        my_grid1.add_widget(WrappedLabel(text='[b]'+title+'[/b]', font_size=20, color=(0,0,0,1), markup=True))
        my_grid1.add_widget(WrappedLabel(text=author, font_size=15, color=(0,0,0,1)))
        my_grid1.add_widget(WrappedLabel(text='Rate: '+rate, font_size=15, color=(0,0,0,1)))
        my_grid1.add_widget(WrappedLabel(text='Updated: '+updated, font_size=15, color=(0,0,0,1)))
        self.ids['display_grid'].add_widget(my_grid1)
        for chapters in chapter_list:
            chapter = chapters[0].strip()
            chapter_edit = chapter[:30]
            link = chapters[1]
            date = chapters[2]
            if len(chapter_edit) == 30:
                text = chapter_edit + '...' + ' '*10 + date
            else:
                text = chapter_edit + ' '*(45-len(chapter_edit)) + ' '*10 + date
            my_button = Button(text=text, size_hint_y=None, height=Window.height*0.1)
            my_button.bind(on_release=partial(self.open_browser, link))
            self.ids['display_box'].add_widget(my_button)

    def open_browser(self, link, *args):
        screen_track.add_track('displaymanga')
        webbrowser.open(link)



class WindowManager(ScreenManager):
    def __init__(self, **kwargs):
        super(WindowManager, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.back_click) # Use to bind keyboard

    def back_click(self, windows, key, *args):
        """Method to bind esc or back button if return False the program will exit"""
        if key == 27:
            return self.go_back()
        return False

    def go_back(self):
        """Method to check the previous screen using screen_track"""
        if screen_track.list_of_prev_screen:
            screen_track.list_of_prev_screen.pop()
            if screen_track.list_of_prev_screen: # Check if screen_track is not empty
                self.current = screen_track.list_of_prev_screen[-1]
                return True
        return False

class Phone(FloatLayout):
    def __init__(self, **kwargs):
        super(Phone, self).__init__(**kwargs)
        self.bubb_addview = None
        self.bubb_viewdelete = None

    def show_manga_list(self, id_window, id_grid, manga, rows=3, imgfolder=imagemanga):
        """Method to call to display list of manga with Image and Info"""
        title = manga[0][:25]
        link = manga[1]
        img = manga[2]
        author = manga[3]
        rate = manga[4]
        img_path = lambda img: os.path.join(imgfolder, img)
        img_source = img_path(img)
        my_img = ImageButton(source= img_source, size_hint_y=None, allow_stretch=True, keep_ratio=True, height=Window.height*0.3)
        if id_grid == 'search_grid':
            my_img.bind(on_release=partial(self.show_bubble_addview, link, img_source, manga))
        elif id_grid == 'storage_grid':
            my_img.bind(on_release=partial(self.show_bubble_viewdelete, link, img_source, manga))
        else:
            my_img.bind(on_release=partial(self.switch_display, link, img_source))
        self.ids[id_window].ids[id_grid].add_widget(my_img)
        my_grid = GridLayout(rows=rows)
        my_grid.add_widget(WrappedLabel(text='[b]'+title+'[/b]', font_size=20, color=(0,0,0,1), markup=True))
        my_grid.add_widget(WrappedLabel(text=author, font_size=15, color=(0,0,0,1)))
        my_grid.add_widget(WrappedLabel(text='Rate: '+rate, font_size=15, color=(0,0,0,1)))
        if rows== 4:
            updated = manga[5]
            my_grid.add_widget(WrappedLabel(text='Updated: '+updated, font_size=15, color=(0,0,0,1)))
        self.ids[id_window].ids[id_grid].add_widget(my_grid)

    def show_bubble_addview(self, link, img_source, manga, *args):
        self.bubb_addview = add_view()
        self.bubb_addview.x = self.on_touch_pos_x
        self.bubb_addview.y = self.on_touch_pos_y - self.bubb_addview.height*1.1
        self.ids['search_window'].add_widget(self.bubb_addview)
        self.bubb_addview.ids['view_search'].bind(on_release=partial(self.switch_display, link, img_source, 'search_window'))
        self.bubb_addview.ids['add_search'].bind(on_release=partial(self.search_add_manga, manga))

    def show_bubble_viewdelete(self, link, img_source, manga, *args):
        self.bubb_viewdelete = view_delete()
        self.bubb_viewdelete.x = self.on_touch_pos_x
        self.bubb_viewdelete.y = self.on_touch_pos_y - self.bubb_viewdelete.height*1.1
        self.ids['storage_window'].add_widget(self.bubb_viewdelete)
        self.bubb_viewdelete.ids['view_storage'].bind(on_release=partial(self.switch_display, link, img_source, 'storage_window'))
        self.bubb_viewdelete.ids['delete_storage'].bind(on_release=partial(self.storage_delete_manga, manga))

    def on_touch_down(self, touch):
        super().on_touch_down(touch)
        if self.bubb_addview != None:
            if not Widget(pos=(self.bubb_addview.x, self.bubb_addview.y+self.bubb_addview.height*0.55), size=(self.bubb_addview.width, self.bubb_addview.height)).collide_point(*touch.pos):
                self.ids['search_window'].remove_widget(self.bubb_addview)
        if self.bubb_viewdelete != None:
            if not Widget(pos=(self.bubb_viewdelete.x, self.bubb_viewdelete.y+self.bubb_viewdelete.height*0.55), size=(self.bubb_viewdelete.width, self.bubb_viewdelete.height)).collide_point(*touch.pos):
                self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        self.on_touch_pos_x = touch.x
        self.on_touch_pos_y = touch.y

    def switch_display(self, link, img_source, id, *args):
        if id == 'search_window':
            self.ids['search_window'].remove_widget(self.bubb_addview)
        elif id == 'storage_window':
            self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        self.ids['_screen_manager'].current = 'displaymanga'
        self.ids['display_manga'].manga_view(link, img_source)

    def search_add_manga(self, manga, *args):
        self.ids['search_window'].remove_widget(self.bubb_addview)
        if not manga_list.check_manga(manga[0]):
            manga_list.add_manga(*manga[:5])
            self.ids['storage_window'].ids['storage_grid'].clear_widgets()
            self.ids['storage_window'].callback()

    def storage_delete_manga(self, manga, *args):
        self.ids['storage_window'].remove_widget(self.bubb_viewdelete)
        if manga_list.check_manga(manga[0]):
            try:
                manga_list.del_manga(manga[0])
            except:
                print('No file')
            self.ids['storage_window'].ids['storage_grid'].clear_widgets()
            self.ids['storage_window'].callback()


class MyApp(App):
    def build(self):
        self.title = "Manga Updates By Israel Quimson"
        self.phone = Phone()
        self.init_check_folder()
        return self.phone

    def init_check_folder(self):
        if not os.path.exists('imagetemp'):
            os.mkdir('imagetemp')
        if not os.path.exists(os.path.join('imagemanga', 'manganelo')):
            os.makedirs(os.path.join('imagemanga', 'manganelo'))
        if not os.path.exists(os.path.join('imagemanga', 'mangaowl')):
            os.makedirs(os.path.join('imagemanga', 'mangaowl'))

    def on_pause(self):
        return True



if __name__ == '__main__':
    MyApp().run()
