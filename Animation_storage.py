class AnimationStorage:
    def __init__(self, animation=None):
        self.animation = animation.deepcopy() if animation else []

    def set_frames(self, id_frame, frames=None):
        if id_frame == 'all':
            for i in range(len(self.animation)):
                self.animation[i] = frames[i]
        elif isinstance(id_frame, (list, tuple)):
            for i, frame in enumerate(id_frame):
                self.animation[frame] = frames[i]
        else:
            self.animation[id_frame] = frames

    def set_points(self, id_frame, points=None):
        if id_frame == 'all':
            for i in range(len(self.animation)):
                self.animation[i]['points'] = points[i]
        elif isinstance(id_frame, (list, tuple)):
            i = 0
            for frame in id_frame:
                if isinstance(self.animation[frame], list):
                    for f in range(len(self.animation[frame])):
                        self.animation[frame][f]['points'] = points[i]
                        i += 1
                else:
                    print(self.animation[frame])
                    self.animation[frame]['points'] = points[i]
                    i += 1
        else:
            if isinstance(self.animation[id_frame], list):
                for f in range(len(self.animation[id_frame])):
                    self.animation[id_frame][f]['points'] = points
            else:
                self.animation[id_frame]['points'] = points

    def set_colors(self, id_frame, colors=None): # need recreate
        if id_frame == 'all':
            for i in range(len(self.animation)):
                self.animation[i] = frames[i]
        elif isinstance(id_frame, (list, tuple)):
            for i, frame in enumerate(id_frame):
                self.animation[frame] = frames[i]
        else:
            self.animation[id_frame] = frames

    def add_frame(self, frame):
        self.animation.append(frame)

    def get_points(self, id_frame):
        points = []
        if id_frame == 'all':
            for frame in self.animation:
                if isinstance(frame, list):
                    for figure in frame:
                        points.append(figure['points'])
                else:
                    points.append(frame['points'])
            return points
        elif isinstance(id_frame, (list, tuple)):
            for i in id_frame:
                frame = self.animation[i]
                if isinstance(frame, list):
                    for figure in frame:
                        points.append(figure['points'])
                else:
                    points.append(frame['points'])
            return points
        else:
            return self.animation[id_frame]['points']

    def get_colors(self, id_frame):
        colors = []
        if id_frame == 'all':
            for frame in self.animation:
                if isinstance(frame, list):
                    for figure in frame:
                        colors.append(figure.get('global_color', figure.get('ind_color')))
                else:
                    colors.append(frame.get('global_color', frame.get('ind_color')))
            return colors
        elif isinstance(id_frame, (list, tuple)):
            for i in id_frame:
                frame = self.animation[i]
                if isinstance(frame, list):
                    for figure in frame:
                        points.append(figure.get('global_color', figure.get('ind_color')))
                else:
                    points.append(frame.get('global_color', frame.get('ind_color')))
            return points
        else:
            return self.animation[id_frame].get('global_color', animation[id_frame].get('ind_color'))

    def get_frames(self, id_frame):
        if id_frame == 'all':
            return self.animation
        elif isinstance(id_frame, (list, tuple)):
            return [self.animation[i] for i in id_frame]
        else:
            return self.animation[id_frame]

    def get_animation(self):
        return self.animation

    def get_depth(self, data):
        if not isinstance(data, list):
            return 0
        if not data:
            return 1
        return 1 + max(self.get_depth(item) for item in data)
    
    def delete_frame(self, id_frame):
        if id_frame == 'all':
            self.clear_animation()
        elif isinstance(id_frame, (list, tuple)):
            for i in id_frame:
                self.animation.pop(i)
        else:
            self.animation.pop(id_frame)

    def clear_animation(self):
        self.animation.clear()



if  __name__ == '__main__':
    anim_storage = AnimationStorage()
    b = [(1, 1, 1), (2, 2, 2)]
    a = anim_storage.get_depth(b)
    print(a)