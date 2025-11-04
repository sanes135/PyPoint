import cv2

class Video:
    def __init__(self, storage, global_center=(0, 0, 0), length_num=3):
        self.storage = storage
        self.global_center = global_center
        self.length_num = length_num




if __name__ == '__main__':
    video = Video([], (0, 0, 0))
    print(video.video_to_points('cat.mp4', skip_frames=29, resize_video=1))