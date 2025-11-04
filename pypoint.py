from Figure_Storage import FigureStorage
from Figure import Figure
from Picture import Picture
from Animation import Animation
from Video import Video
from Minecraft import Minecraft
from Animation_storage import AnimationStorage


class PyPoint:
    def __init__(self, storage=None, anim_storage=None, global_center=(0, 0, 0), length_num=3):
        self.storage = FigureStorage(storage)
        self.anim_storage = AnimationStorage(anim_storage)
        self.figure = Figure(self.storage, global_center, length_num)
        self.picture = Picture(self.storage, global_center, length_num)
        self.animation = Animation(self.anim_storage, global_center, length_num)
        self.video = Video(self.storage, global_center, length_num)

    def set_global_center(self, type='all', global_center=(0, 0, 0)):
        if type.lower() == 'all':
            self.figure.global_center = global_center
            self.picture.global_center = global_center
            self.animation.global_center = global_center
            self.video.global_center = global_center
        elif type.lower() == 'figure':
            self.figure.global_center = global_center
        elif type.lower() == 'picture':
            self.picture.global_center = global_center
        elif type.lower() == 'animation':
            self.animation.global_center = global_center
        elif type.lower() == 'video':
            self.video.global_center = global_center

    def set_length_num(self, type='all', length_num=3):
        if type.lower() == 'all':
            self.figure.length_num = length_num
            self.picture.length_num = length_num
            self.animation.length_num = length_num
            self.video.length_num = length_num
        elif type.lower() == 'figure':
            self.figure.length_num = length_num
        elif type.lower() == 'picture':
            self.picture.length_num = length_num
        elif type.lower() == 'animation':
            self.animation.length_num = length_num
        elif type.lower() == 'video':
            self.video.length_num = length_num

    # Animation
    def get_animation(self):
        return self.anim_storage.get_animation()

    def get_animation_points(self, id_frame='all'):
        return self.anim_storage.get_points(id_frame)

    def get_animation_colors(self, id_frame='all'):
        return self.anim_storage.get_colors(id_frame)

    def get_animation_frames(self, id_frame='all'):
        return self.anim_storage.get_frames(id_frame)

    # Storage
    def get_storage(self):
        return self.storage.get_storage()

    def get_keys(self, points=None, colors=None):
        return self.storage.get_keys(points, colors)

    def get_figures(self, keys='all'):
        return self.storage.get_figures(keys)

    def get_points(self, keys='all'):
        return self.storage.get_points(keys)

    def get_colors(self, keys='all'):
        return self.storage.get_colors(keys)
