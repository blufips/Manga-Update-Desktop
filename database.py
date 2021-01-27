import os
import shutil

class TextFile:
    """This class create, add and delete maga list as text file"""
    def __init__(self, file_name, imagemanga):
        """Initialize to create text file if not exist"""
        self.file_name = file_name + '.txt'
        self.file_name_path = os.path.join('..', self.file_name)
        self.img_temp = lambda img: os.path.join('imagetemp', img)
        self.img_release = lambda img: os.path.join('imagerelease', img)
        self.img_manga = lambda img: os.path.join(imagemanga, img)
        with open(self.file_name_path, 'ab') as file:
            pass

    def add_manga(self, title, link, img, author, rate, window):
        """Function to add the manga to the text file and move its image from imagetemp fold to imagemanga folder"""
        with open(self.file_name_path, 'ab') as file:
            file.write(f"{title},,{link},,{img},,{author},,{rate}\n".encode('utf-8'))
        if window == 'home_window':
            shutil.copy(self.img_release(img), self.img_manga(img))
        else:
            shutil.copy(self.img_temp(img), self.img_manga(img))

    def del_manga(self, manga):
        """Function to delete the manga to the text file and delete its image to the imagefolder"""
        lines = list()
        success = False
        with open(self.file_name_path, 'rb') as file:
            read_lines = file.readlines()
            for line in read_lines:
                line = line.decode('utf-8')
                if line.split(',,')[0] != manga:
                    lines.append(line.encode('utf-8'))
                else:
                    success = True
                    img = line.split(',,')[2]
        with open(self.file_name_path, 'wb') as file:
            file.writelines(lines)
        os.remove(self.img_manga(img))

    def check_manga(self, manga):
        """Function to check if the manga is already in the text file"""
        with open(self.file_name_path, 'rb') as file:
            read_lines = file.readlines()
            for line in read_lines:
                line = line.decode('utf-8')
                if line.split(',,')[0] == manga:
                    return True
            return False

    def list_manga(self):
        """Function to return a list of mangga"""
        with open(self.file_name_path, 'rb') as file:
            manga_list = list()
            for line in file.readlines():
                line = line.decode('utf-8')
                title, link, img, author, rate = line.split(',,')
                manga_list.append([title, link, img, author, rate.strip()])
            return sorted(manga_list)

    def del_folder_download(self, path, chapter):
        """Function to delete folder directory and sub-directories recursively in download"""
        folder_path = os.path.join(path, chapter)
        shutil.rmtree(folder_path)



if __name__ == '__main__':
    imagemanga = os.path.join('imagemanga', 'manganelo')
    manga_list = TextFile('manganelo', imagemanga)
    # manga_list.add_manga('Berserk', 'https://manganelo.com/manga/ilsi12001567132882', 'Berserk.jpg', 'Miura Kentaro', '4.8')
    manga_list.add_manga('One Piece', 'https://manganelo.com/manga/read_one_piece_manga_online_free4', 'One Piece.jpg', 'Oda Eiichiro', '4.1')
    # print(manga_list.list_manga())
    # print(manga_list.check_manga('One Piece'))
    # manga_list.del_manga('Berserk')
