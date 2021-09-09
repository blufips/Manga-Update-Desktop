MangaUpdate version 0.57
Change requests into cloudscraper to fix the cloudflare blocking the scrapper.py
Temporary remove other server except Mangahub (It's hard to maintain multiple manga server)

MangaUpdate version 0.56

This version is for Android APP using buildozer to make APK


The main function of this application is to check all the updates of your favorite manga from latest and then it can re direct the browser to the Manga Server
You can search your favorite manga in search button
You can check your favorite manga in storage button
You can view latest manga and genres
You can change Manga server in Settings (Currently Manganelo and Mangareader Server is available)

To go back to previous screen just click escape from your keyboard

Note: I add random delay (0.3-1seconds) for each manga to be check update, the reason is for the Manga server not be flooded of requests

If you have comments, suggestion or bug report kindly email me at israelquimson49056@yahoo.com

Have fun


**********
version 0.56
Fix the date_format method in mangahub scrap

version 0.55
Add server Mangahub(default Server)
Remove server Manganelo and Toonily

version 0.54
Temporary change the default server to MangaPark

version 0.53
Add delete_manga in class MainFunc scrapper.py
Add storage refresh every check manga_update
Fix server changing the link of manga (It will delete the manga in storage)

version 0.52
Change the check update method instead of showing add view bubble it will redirect to view the manga

version 0.51
Add server MangaPark
Fix mangareader bug on scrapper release img_link http
Add url_name_check method

version 0.41
change requirements kivy==1.11.1 to fix index error
add admob interstitial
add Dark mode
fix bug on scrappy manganelo title

version 0.36
adjust the position of admob banner
create check_internet for every 20secods

version 0.35
add admob banner

version 0.34
Change the storage Icon
Change the genre view
Add Toonily(Adult) Server

version 0.33
Instead of waiting for all the manga to display simultaniously
It will now display successively

version 0.32
Fix version check

version 0.31
Change log
Add genres
Change splash image
Automatic Check update
Keep Storage while upgrading
