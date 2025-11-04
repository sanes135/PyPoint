# from Picture_Storage import PictureStorage
from math import cos, sin, pi, acos, sqrt
from PIL import Image
# Статус - Нет идей, заброшен
class Picture:
    def __init__(self, storage, global_center=(0, 0, 0), length_num=3):
        self.global_center = global_center
        self.length_num = length_num
        self.storage = storage




if __name__ == "__main__":
    picture = Picture()
    key = picture.image_to_points(r'C:\Users\79222\PycharmProjects\3d points\Not project\img_1.png')
    print(picture.storage.get_figure(key))