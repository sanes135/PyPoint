import numpy as np
from Animation_storage import AnimationStorage
class Animation:
    def __init__(self, anim_storage=None, global_center=(0, 0, 0), length_num=3):
        self.animation = anim_storage if anim_storage is not None else AnimationStorage()
        self.global_center = global_center
        self.length_num = length_num

    def add_static(self, figures, num_frames=1):
        if num_frames <= 0:
            return
        for i in range(num_frames):
            self.animation.add_frame(figures)

    def add_move(self, figures, end_point=(0, 0, 0), num_frames=1, center=None):
        points, colors = self._get_points(figures), self._get_colors(figures)

        if center is None:
            center = self._get_center(points)

        if num_frames <= 0:
            return

        elif num_frames == 1:
            frame = []
            for point in points:
                if isinstance(point, list):
                    dframe = []
                    for p in point:
                        x = round(p[0] + end_point[0] - center[0], self.length_num)
                        y = round(p[1] + end_point[1] - center[1], self.length_num)
                        z = round(p[2] + end_point[2] - center[2], self.length_num)
                        dframe.append((x, y, z))
                    frame.append(dframe)
                else:
                    x = round(point[0] + end_point[0] - center[0], self.length_num)
                    y = round(point[1] + end_point[1] - center[1], self.length_num)
                    z = round(point[2] + end_point[2] - center[2], self.length_num)
                    frame.append((x, y, z))

            self.animation.add_frame(self._group_figure(frame, colors))

        else:
            dx = round((end_point[0] - center[0]) / (num_frames - 1), self.length_num)
            dy = round((end_point[1] - center[1]) / (num_frames - 1), self.length_num)
            dz = round((end_point[2] - center[2]) / (num_frames - 1), self.length_num)
            for i in range(num_frames):
                frame = []
                for point in points:
                    if isinstance(point, list):
                        dframe = []
                        for p in point:
                            x = round(p[0] + dx * i, self.length_num)
                            y = round(p[1] + dy * i, self.length_num)
                            z = round(p[2] + dz * i, self.length_num)
                            dframe.append((x, y, z))
                        frame.append(dframe)
                    else:
                        x = round(point[0] + dx * i, self.length_num)
                        y = round(point[1] + dy * i, self.length_num)
                        z = round(point[2] + dz * i, self.length_num)
                        frame.append((x, y, z))

                self.animation.add_frame(self._group_figure(frame, colors))

    def add_coordinate_move(self, figures, add_cord=(1, 1, 1), num_frames=1):
        points, colors = self._get_points(figures), self._get_colors(figures)

        if num_frames <= 0:
            return

        elif num_frames == 1:
            frame = []
            for point in points:
                if isinstance(point, list):
                    dframe = []
                    for p in point:
                        x = round(p[0] + add_cord[0], self.length_num)
                        y = round(p[1] + add_cord[1], self.length_num)
                        z = round(p[2] + add_cord[2], self.length_num)
                        dframe.append((x, y, z))
                    frame.append(dframe)
                else:
                    x = round(point[0] + add_cord[0], self.length_num)
                    y = round(point[1] + add_cord[1], self.length_num)
                    z = round(point[2] + add_cord[2], self.length_num)
                    frame.append((x, y, z))

            self.animation.add_frame(self._group_figure(frame, colors))
        else:
            dx = round(add_cord[0] / (num_frames - 1), self.length_num)
            dy = round(add_cord[1] / (num_frames - 1), self.length_num)
            dz = round(add_cord[2] / (num_frames - 1), self.length_num)
            for i in range(num_frames):
                frame = []
                for point in points:
                    if isinstance(point, list):
                        dframe = []
                        for p in point:
                            x = round(p[0] + dx * i, self.length_num)
                            y = round(p[1] + dy * i, self.length_num)
                            z = round(p[2] + dz * i, self.length_num)
                            dframe.append((x, y, z))
                        frame.append(dframe)
                    else:
                        x = round(point[0] + dx * i, self.length_num)
                        y = round(point[1] + dy * i, self.length_num)
                        z = round(point[2] + dz * i, self.length_num)
                        frame.append((x, y, z))

                self.animation.add_frame(self._group_figure(frame, colors))

    def add_transform(self, start_figures, end_figures, num_frames=1):
        start_points, start_colors = self._get_points(start_figures), self._get_colors(start_figures)
        end_points = self._flatten_list(self._get_points(end_figures))

        if len(self._flatten_list(start_points)) != len(self._flatten_list(end_points)):
            raise ValueError(f"The figures must contain the same number of points."
                             f"\n(start_figures = {len(self._flatten_list(start_points))}"
                             f"\nend_figures = {len(self._flatten_list(end_points))}")
        elif num_frames <= 0:
            return
        elif num_frames == 1:
            self.animation.add_frame(end_figures)
        else:
            for step in range(num_frames):
                frame = []
                t = step / (num_frames - 1) if num_frames > 1 else 0

                if self.animation.get_depth(start_points) == 2:
                    i = 0
                    end_points = self._flatten_list(end_points)
                    for point in start_points:
                        dframe = []
                        for p in point:
                            x = round(p[0] + (end_points[i][0] - p[0]) * t, self.length_num)
                            y = round(p[1] + (end_points[i][1] - p[1]) * t, self.length_num)
                            z = round(p[2] + (end_points[i][2] - p[2]) * t, self.length_num)
                            dframe.append((x, y, z))
                            i += 1
                        frame.append(dframe)
                    self.animation.add_frame(self._group_figure(frame, start_colors))
                else:
                    for i in range(len(start_points)):
                        x = round(start_points[i][0] + (end_points[i][0] - start_points[i][0]) * t, self.length_num)
                        y = round(start_points[i][1] + (end_points[i][1] - start_points[i][1]) * t, self.length_num)
                        z = round(start_points[i][2] + (end_points[i][2] - start_points[i][2]) * t, self.length_num)
                        frame.append((x, y, z))
                    self.animation.add_frame(self._group_figure(frame, start_colors))

    def add_rotation(self, figures, degrees=(0, 0, 0), num_frames=1, rotation_center=None):
        points, colors = self._get_points(figures), self._get_colors(figures)
        if rotation_center is not None:
            points = np.array(points)
            points -= rotation_center
            if self.animation.get_depth(points.tolist()) == 3:
                lst = []
                for row in points.tolist():
                    lst.append([tuple(point) for point in row])
                points = lst
            else:
                points = [tuple(row) for row in points.tolist()]

        if num_frames <= 0:
            return
        elif num_frames == 1:
            degrees = np.deg2rad(degrees)
            matrix_x = np.array([[1, 0, 0],
                                 [0, np.cos(degrees[0]), -np.sin(degrees[0])],
                                 [0, np.sin(degrees[0]), np.cos(degrees[0])]])
            matrix_y = np.array([[np.cos(degrees[1]), 0, np.sin(degrees[1])],
                                 [0, 1, 0],
                                 [-np.sin(degrees[1]), 0, np.cos(degrees[1])]])
            matrix_z = np.array([[np.cos(degrees[2]), -np.sin(degrees[2]), 0],
                                 [np.sin(degrees[2]), np.cos(degrees[2]), 0],
                                 [0, 0, 1]])

            rotated_points = np.dot(points, matrix_x)
            rotated_points = np.dot(rotated_points, matrix_y)
            rotated_points = np.dot(rotated_points, matrix_z)
            frame = []
            if self.animation.get_depth(points) == 2:
                for point in rotated_points:
                    for p in point:
                        x = round(float(p[0]), self.length_num)
                        y = round(float(p[1]), self.length_num)
                        z = round(float(p[2]), self.length_num)
                        frame.append((x, y, z))
            else:
                for point in rotated_points:
                    x = round(float(point[0]), self.length_num)
                    y = round(float(point[1]), self.length_num)
                    z = round(float(point[2]), self.length_num)
                    frame.append((x, y, z))
            self.animation.add_frame(self._group_figure(frame, colors))
        else:
            changes_degrees = (degrees[0] / (num_frames - 1), degrees[1] / (num_frames - 1), degrees[2] / (num_frames - 1))
            for i in range(num_frames):
                degrees = (changes_degrees[0] * i, changes_degrees[1] * i, changes_degrees[2] * i)
                degrees = np.deg2rad(degrees)
                matrix_x = np.array([
                    [1, 0, 0],
                    [0, np.cos(degrees[0]), np.sin(degrees[0])],
                    [0, -np.sin(degrees[0]), np.cos(degrees[0])]
                ])

                matrix_y = np.array([
                    [np.cos(degrees[1]), 0, -np.sin(degrees[1])],
                    [0, 1, 0],
                    [np.sin(degrees[1]), 0, np.cos(degrees[1])]
                ])

                matrix_z = np.array([
                    [np.cos(degrees[2]), np.sin(degrees[2]), 0],
                    [-np.sin(degrees[2]), np.cos(degrees[2]), 0],
                    [0, 0, 1]
                ])

                rotated_points = np.dot(points, matrix_x)
                rotated_points = np.dot(rotated_points, matrix_y)
                rotated_points = np.dot(rotated_points, matrix_z)
                frame = []
                if self.animation.get_depth(points) == 2:
                    for point in rotated_points:
                        for p in point:
                            x = round(float(p[0]), self.length_num)
                            y = round(float(p[1]), self.length_num)
                            z = round(float(p[2]), self.length_num)
                            frame.append((x, y, z))
                else:
                    for point in rotated_points:
                        x = round(float(point[0]), self.length_num)
                        y = round(float(point[1]), self.length_num)
                        z = round(float(point[2]), self.length_num)
                        frame.append((x, y, z))
                self.animation.add_frame(self._group_figure(frame, colors))

    def add_flip(self, figures, reflection_point=(0, 0, 0), num_frames=1, applicable_cord=(True, True, True)):
        points, colors = self._get_points(figures), self._get_colors(figures)

        if num_frames <= 0:
            return
        elif num_frames == 1:
            frame = []
            for point in points:
                if isinstance(point, list):
                    dframe = []
                    for p in point:
                        dframe.append((
                            2 * reflection_point[0] - p[0] if applicable_cord[0] else p[0],
                            2 * reflection_point[1] - p[1] if applicable_cord[1] else p[1],
                            2 * reflection_point[2] - p[2] if applicable_cord[2] else p[2]))
                    frame.append(dframe)
                else:
                    frame.append((
                        2 * reflection_point[0] - point[0] if applicable_cord[0] else point[0],
                        2 * reflection_point[1] - point[1] if applicable_cord[1] else point[1],
                        2 * reflection_point[2] - point[2] if applicable_cord[2] else point[2]))
            self.animation.add_frame(self._group_figure(frame, colors))
        else:
            x, y, z = reflection_point
            dx = round(x / (num_frames - 1), self.length_num)
            dy = round(y / (num_frames - 1), self.length_num)
            dz = round(z / (num_frames - 1), self.length_num)
            for i in range(num_frames):
                frame = []
                for point in points:
                    if isinstance(point, list):
                        dframe = []
                        for p in point:
                            dframe.append((
                                2 * dx * i - p[0] if applicable_cord[0] else p[0],
                                2 * dy * i - p[1] if applicable_cord[1] else p[1],
                                2 * dz * i - p[2] if applicable_cord[2] else p[2]))
                        frame.append(dframe)
                    else:
                        frame.append((
                            2 * dx * i - point[0] if applicable_cord[0] else point[0],
                            2 * dy * i - point[1] if applicable_cord[1] else point[1],
                            2 * dz * i - point[2] if applicable_cord[2] else point[2]))
                self.animation.add_frame(self._group_figure(frame, colors))

    def add_scale(self, figures, size=(2, 2, 2), num_frames=1):
        points, colors = self._get_points(figures), self._get_colors(figures)

        resized_points = np.array(points, dtype=np.float64)
        size = np.array(size, dtype=np.float64)
        resized_points *= size
        if self.animation.get_depth(resized_points.tolist()) == 3:
            lst = []
            for row in resized_points.tolist():
                lst.append([tuple(point) for point in row])
            resized_points = lst
        else:
            resized_points = [tuple(row) for row in resized_points.tolist()]

        self.add_transform(figures, self._group_figure(resized_points, colors), num_frames)

    def change_move(self, id_frame, end_point=(0, 0, 0), center=None):
        if id_frame == 'all':
            ids = range(len(self.animation.get_animation()))
        elif isinstance(id_frame, int):
            ids = [id_frame]
        else:
            ids = id_frame

        for i in ids:
            figures = self.animation.get_frames(i)
            points, colors = self._get_points(figures), self._get_colors(figures)
            if center is None:
                center = self._get_center(points)

            frame = []
            for point in points:
                if isinstance(point, list):
                    dframe = []
                    for p in point:
                        x = round(p[0] + end_point[0] - center[0], self.length_num)
                        y = round(p[1] + end_point[1] - center[1], self.length_num)
                        z = round(p[2] + end_point[2] - center[2], self.length_num)
                        dframe.append((x, y, z))
                    frame.append(dframe)
                else:
                    x = round(point[0] + end_point[0] - center[0], self.length_num)
                    y = round(point[1] + end_point[1] - center[1], self.length_num)
                    z = round(point[2] + end_point[2] - center[2], self.length_num)
                    frame.append((x, y, z))

            self.animation.set_points(i, frame)

    def change_coordinate_move(self, id_frame, add_cord=(1, 1, 1)):
        if id_frame == 'all':
            ids = range(len(self.animation.get_animation()))
        elif isinstance(id_frame, int):
            ids = [id_frame]
        else:
            ids = id_frame

        for i in ids:
            figures = self.animation.get_frames(i)
            points, colors = self._get_points(figures), self._get_colors(figures)
            frame = []
            for point in points:
                if isinstance(point, list):
                    dframe = []
                    for p in point:
                        x = round(p[0] + add_cord[0], self.length_num)
                        y = round(p[1] + add_cord[1], self.length_num)
                        z = round(p[2] + add_cord[2], self.length_num)
                        dframe.append((x, y, z))
                    frame.append(dframe)
                else:
                    x = round(point[0] + add_cord[0], self.length_num)
                    y = round(point[1] + add_cord[1], self.length_num)
                    z = round(point[2] + add_cord[2], self.length_num)
                    frame.append((x, y, z))

            self.animation.set_points(i, frame)

    def change_rotation(self, id_frame, degrees=(0, 0, 0), rotation_center=None):
        if id_frame == 'all':
            ids = range(len(self.animation.get_animation()))
        elif isinstance(id_frame, int):
            ids = [id_frame]
        else:
            ids = id_frame

        for i in ids:
            figures = self.animation.get_frames(i)
            points, colors = self._get_points(figures), self._get_colors(figures)
            if rotation_center is not None:
                points = np.array(points)
                points -= rotation_center
                if self.animation.get_depth(points.tolist()) == 3:
                    lst = []
                    for row in points.tolist():
                        lst.append([tuple(point) for point in row])
                    points = lst
                else:
                    points = [tuple(row) for row in points.tolist()]

            degrees = np.deg2rad(degrees)
            matrix_x = np.array([
                [1, 0, 0],
                [0, np.cos(degrees[0]), np.sin(degrees[0])],
                [0, -np.sin(degrees[0]), np.cos(degrees[0])]
            ])

            matrix_y = np.array([
                [np.cos(degrees[1]), 0, -np.sin(degrees[1])],
                [0, 1, 0],
                [np.sin(degrees[1]), 0, np.cos(degrees[1])]
            ])

            matrix_z = np.array([
                [np.cos(degrees[2]), np.sin(degrees[2]), 0],
                [-np.sin(degrees[2]), np.cos(degrees[2]), 0],
                [0, 0, 1]
            ])

            rotated_points = np.dot(points, matrix_x)
            rotated_points = np.dot(rotated_points, matrix_y)
            rotated_points = np.dot(rotated_points, matrix_z)
            frame = []
            if self.animation.get_depth(points) == 2:
                for point in rotated_points:
                    for p in point:
                        x = round(float(p[0]), self.length_num)
                        y = round(float(p[1]), self.length_num)
                        z = round(float(p[2]), self.length_num)
                        frame.append((x, y, z))
            else:
                for point in rotated_points:
                    x = round(float(point[0]), self.length_num)
                    y = round(float(point[1]), self.length_num)
                    z = round(float(point[2]), self.length_num)
                    frame.append((x, y, z))

            self.animation.set_points(i, frame)

    def change_flip(self, id_frame, reflection_point=(0, 0, 0), applicable_cord=(True, True, True)):
        if id_frame == 'all':
            ids = range(len(self.animation.get_animation()))
        elif isinstance(id_frame, int):
            ids = [id_frame]
        else:
            ids = id_frame

        for i in ids:
            figures = self.animation.get_frames(i)
            points, colors = self._get_points(figures), self._get_colors(figures)
            frame = []
            for point in points:
                if isinstance(point, list):
                    dframe = []
                    for p in point:
                        dframe.append((
                            2 * reflection_point[0] - p[0] if applicable_cord[0] else p[0],
                            2 * reflection_point[1] - p[1] if applicable_cord[1] else p[1],
                            2 * reflection_point[2] - p[2] if applicable_cord[2] else p[2]))
                    frame.append(dframe)
                else:
                    frame.append((
                        2 * reflection_point[0] - point[0] if applicable_cord[0] else point[0],
                        2 * reflection_point[1] - point[1] if applicable_cord[1] else point[1],
                        2 * reflection_point[2] - point[2] if applicable_cord[2] else point[2]))

            self.animation.set_points(i, frame)

    def change_scale(self, id_frame, size=(2, 2, 2)):
        if id_frame == 'all':
            ids = range(len(self.animation.get_animation()))
        elif isinstance(id_frame, int):
            ids = [id_frame]
        else:
            ids = id_frame

        for i in ids:
            figures = self.animation.get_frames(i)
            points, colors = self._get_points(figures), self._get_colors(figures)
            resized_points = np.array(points, dtype=np.float64)
            size = np.array(size, dtype=np.float64)
            resized_points *= size
            if self.animation.get_depth(resized_points.tolist()) == 3:
                lst = []
                for row in resized_points.tolist():
                    lst.append([tuple(point) for point in row])
                resized_points = lst
            else:
                resized_points = [tuple(row) for row in resized_points.tolist()]

            self.animation.set_points(i, resized_points)

    def change_frames(self, id_frame, frames): # need recreate
        self.animation.set_frames(id_frame, frames)

    def replace_frame(self, id_frame, a): # need recreate
        pass

    def delete_frame(self, id_frame):
        self.animation.delete_frame(id_frame)

    def add_frame(self, frames):
        self.animation.add_frame(frames)

    def get_frame(self, id_frame):
        return self.animation.get_frames(id_frame)

    def get_animation(self):
        return self.animation.get_animation()

    def clear_animation(self):
        self.animation.clear_animation()

    def optimization(self): # maybe create?
        pass

    def _get_center(self, points):
        points = self._flatten_list(points)
        n = len(points)
        if n == 0:
            return (0, 0, 0)

        x = 0
        y = 0
        z = 0
        for point in points:
            x += point[0]
            y += point[1]
            z += point[2]

        x = round(x / n, self.length_num)
        y = round(y / n, self.length_num)
        z = round(z / n, self.length_num)
        return (x, y, z)

    def _get_points(self, figures):
        if self.animation.get_depth(figures) == 0:
            return figures.get('points')
        else:
            return [figure.get('points') for figure in figures]

    def _get_colors(self, figures):
        if self.animation.get_depth(figures) == 0:
            return figures.get('ind_color', figures.get('global_color'))
        else:
            return [figure.get('ind_color', figure.get('global_color')) for figure in figures]

    def _group_figure(self, points, colors):
        if self.animation.get_depth(points) == 2:
            figure = []
            for i in range(len(points)):
                if isinstance(colors[i], list):
                    figure.append({'ind_color': colors[i], 'points': points[i]})
                else:
                    figure.append({'global_color': colors[i], 'points': points[i]})
            return figure
        else:
            if isinstance(colors, list):
                return {'ind_color': colors, 'points': points}
            else:
                return {'global_color': colors, 'points': points}

    def _flatten_list(self, data):
        flat_list = []
        for item in data:
            if isinstance(item, list):
                flat_list.extend(item)
            else:
                flat_list.append(item)
        return flat_list


if __name__ == '__main__':
    animation = Animation()
    print('*********************START DATA*****************', end='\n\n')

    figure1 = [{'global_color': (0, 0, 0), 'points': [(1, 0, 0), (1, 1, 1)]},
              {'global_color': (1, 1, 1), 'points': [(2, 2, 2), (1, 1, 1)]}]
    figure2 = {'global_color': (123, 0, 0), 'points': [(0, 0, 0), (1, 1, 1), (2, 2, 2), (1, 1, 1)]}

    data = figure1
    print(data)
    # add
    print('\n*********************TEST ADD*******************', end='\n\n')
    animation.add_scale(figure1, 2, 2)
    animation.add_scale(figure2, 2, 2)

    print(animation.get_animation(), end='\n\n')
    for frame in animation.get_animation():
        print(frame)
        p = animation._flatten_list(animation._get_points(frame))

        print("Point:", p)
    #
    # # CHANGE
    # print("\n********************TEST CHANGE*****************", end='\n\n')
    # animation.change_scale("all", (2, 100, 0))
    #
    # print(animation.get_animation(), end='\n\n')
    # for frame in animation.get_animation():
    #     print(frame)