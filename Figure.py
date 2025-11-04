from math import cos, sin, pi, acos, sqrt, degrees
import numpy as np


class Figure:
    def __init__(self, storage, global_center=(0, 0, 0), length_num=3):
        self.global_center = global_center
        self.length_num = length_num
        self.storage = storage

    def line(self, point1=(0, 0, 0), point2=(1, 1, 1), step=1, name_figure='line'):
        key = self.storage.add_figure(name_figure)

        if step == 0:
            return key

        elif step == 1:
            x = round((point1[0] + point2[0]) / 2 + self.global_center[0], self.length_num)
            y = round((point1[1] + point2[1]) / 2 + self.global_center[1], self.length_num)
            z = round((point1[2] + point2[2]) / 2 + self.global_center[2], self.length_num)
            self.storage.add_points(key, (x, y, z))
            return key

        length_x = (point2[0] - point1[0]) / (step - 1)
        length_y = (point2[1] - point1[1]) / (step - 1)
        length_z = (point2[2] - point1[2]) / (step - 1)

        for i in range(step):
            x = round(length_x * i + point1[0] + self.global_center[0], self.length_num)
            y = round(length_y * i + point1[1] + self.global_center[1], self.length_num)
            z = round(length_z * i + point1[2] + self.global_center[2], self.length_num)
            self.storage.add_points(key, (x, y, z))
        return key

    def _line(self, point1=(0, 0, 0), point2=(1, 1, 1), step=1, move=(0, 0, 0), remove_point=(), key=None):
        if step == 0:
            return

        elif step == 1:
            x = round((point1[0] + point2[0]) / 2 + move[0] + self.global_center[0], self.length_num)
            y = round((point1[1] + point2[1]) / 2 + move[1] + self.global_center[1], self.length_num)
            z = round((point1[2] + point2[2]) / 2 + move[2] + self.global_center[2], self.length_num)
            self.storage.add_points(key, (x, y, z))
            return

        length_x = (point2[0] - point1[0]) / (step - 1)
        length_y = (point2[1] - point1[1]) / (step - 1)
        length_z = (point2[2] - point1[2]) / (step - 1)
        if isinstance(remove_point, int):
            remove_point = [remove_point]
        for i in range(step):
            if i in remove_point:
                continue
            x = round(length_x * i + point1[0] + move[0] + self.global_center[0], self.length_num)
            y = round(length_y * i + point1[1] + move[1] + self.global_center[1], self.length_num)
            z = round(length_z * i + point1[2] + move[2] + self.global_center[2], self.length_num)
            self.storage.add_points(key, (x, y, z))

    def circle(self, size=(1, 1, 1), step=1, move=(0, 0, 0), name_figure='circle'):
        key = self.storage.add_figure(name_figure)

        length = 2 * pi / step
        for i in range(step):
            sinus = sin(length * i)
            x = round(cos(length * i) * size[0] + self.global_center[0] + move[0], self.length_num)
            y = round(sinus * size[1] + self.global_center[1] + move[1], self.length_num)
            z = round(sinus * size[2] + self.global_center[2] + move[2], self.length_num)
            self.storage.add_points(key, (x, y, z))
        return key

    def triangle(self, size=(1, 1, 1), step=1, move=(0, 0, 0), name_figure='triangle'):
        key = self.storage.add_figure(name_figure)

        point1 = (-size[0], -size[1], -size[2])
        point2 = (0, size[1], 0)
        point3 = (size[0], -size[1], size[2])

        self._line(point3, point1, step, move, 0, key)
        self._line(point1, point2, step, move, 0, key)
        self._line(point2, point3, step, move, 0, key)
        return key

    def square(self, size=(1, 1, 1), step=1, move=(0, 0, 0), name_figure='square'):
        key = self.storage.add_figure(name_figure)

        point1 = (-size[0], -size[1], -size[2])
        point2 = (-size[0], size[1], -size[2])
        point3 = (size[0], size[1], size[2])
        point4 = (size[0], -size[1], size[2])

        self._line(point4, point1, step, move, 0, key)
        self._line(point1, point2, step, move, 0, key)
        self._line(point2, point3, step, move, 0, key)
        self._line(point3, point4, step, move, 0, key)
        return key

    def cube(self, size=(1, 1, 1), step=1, move=(0, 0, 0), name_figure='cube'):
        key = self.storage.add_figure(name_figure)

        point1 = (-size[0], -size[1], -size[2])
        point2 = (-size[0], size[1], -size[2])
        point3 = (-size[0], size[1], size[2])
        point4 = (-size[0], -size[1], size[2])
        point5 = (size[0], -size[1], -size[2])
        point6 = (size[0], size[1], -size[2])
        point7 = (size[0], size[1], size[2])
        point8 = (size[0], -size[1], size[2])

        self._line(point1, point2, step, move, 0, key)
        self._line(point2, point3, step, move, 0, key)
        self._line(point3, point4, step, move, 0, key)
        self._line(point4, point1, step, move, 0, key)
        self._line(point1, point5, step, move, 0, key)
        self._line(point2, point6, step, move, 0, key)
        self._line(point3, point7, step, move, 0, key)
        self._line(point4, point8, step, move, 0, key)
        self._line(point5, point6, step, move, 0, key)
        self._line(point6, point7, step, move, 0, key)
        self._line(point7, point8, step, move, 0, key)
        self._line(point8, point5, step, move, 0, key)
        return key

    def sphere(self, size=(1, 1, 1), step=100, move=(0, 0, 0), name_figure='sphere'):
        key = self.storage.add_figure(name_figure)

        # Рассчитываем золотой угол (правильная константа)
        golden_angle = np.pi * (3 - np.sqrt(5))

        # Создаем массив индексов
        i = np.arange(step, dtype=np.float32)

        # Вертикальная координата (равномерно распределена)
        z = 1 - (2 * i + 1) / step  # z ∈ [-1, 1]

        # Радиус проекции на XY-плоскость
        r = np.sqrt(1 - z ** 2)

        # Угол в плоскости XY (золотой угол)
        theta = golden_angle * i

        # Координаты точек
        x = np.cos(theta) * r * size[0] + move[0] + self.global_center[0]
        y = np.sin(theta) * r * size[1] + move[1] + self.global_center[1]
        z = z * size[2] + move[2] + self.global_center[2]

        # Добавляем точки в хранилище
        for i in range(step):
            point = (
                round(float(x[i]), self.length_num),
                round(float(y[i]), self.length_num),
                round(float(z[i]), self.length_num)
            )
            self.storage.add_points(key, point)

        return key

    def pyramid(self, size=(1, 1, 1), step=20, base_length=3, move=(0, 0, 0), name_figure='pyramid'):
        key = self.storage.add_figure(name_figure)

        point_up = (0, size[1], 0)

        angle_step = 2 * pi / base_length
        base_points = []
        for i in range(base_length):
            theta = i * angle_step
            x = round(+size[0] * cos(theta), self.length_num)
            y = round(-size[1], self.length_num)
            z = round(+size[2] * sin(theta), self.length_num)
            self._line(point_up, (x, y, z), step, move, 0, key)
            base_points.append((x, y, z))

        for i in range(-1, base_length - 1):
            self._line(base_points[i], base_points[i + 1], step, move, 0, key)
        return key

    def polygons(self, points=((0, 0, 0), (1, 1, 1)), step=1, end=False, name_figure='polygons'):
        key = self.storage.add_figure(name_figure)

        if len(points) == 0:
            return key
        elif len(points) == 1:
            self.storage.add_figure(key, points[0])
        elif len(points) == 2:
            self._line(points[0], points[1], step, key=key)
        else:
            for i in range(len(points) - 1):
                if i == 0:
                    self._line(points[i], points[i + 1], step, key=key)
                else:
                    self._line(points[i], points[i + 1], step, remove_point=0, key=key)
            if end:
                self._line(points[-1], points[0], step, remove_point=(0, step-1), key=key)
        return key

    def curved_line(self, points_list=((0, 0, 0), (1, 1, 1)), step=1, name_figure='curved_line'):
        key = self.storage.add_figure(name_figure)

        def _bezier(points, t):
            if len(points) == 1:
                return points[0]

            # Рекурсивно вычисляем соседние точки
            point1 = _bezier(points[:-1], t)
            point2 = _bezier(points[1:], t)

            # Линейная интерполяция между точками
            nt = 1.0 - t
            return tuple(round((nt * coord1 + t * coord2) + center, self.length_num) for coord1, coord2, center in
                         zip(point1, point2, self.global_center))

        for i in range(step + 1):
            t = i * (1 / step)
            self.storage.add_points(key, _bezier(points_list, t))

        return key

    def delete_duplicate(self, points):
        unique_list = []
        seen = set()
        for item in points:
            if item not in seen:
                unique_list.append(item)
                seen.add(item)
        return unique_list

    # def banana(self, step):
    #     print(f'pay {str(135 ** 9)}$ for banana')
    #     banana = r"""
    #            _
    #          //\
    #          V  \
    #           \  \_
    #            \,'.`-.
    #             |\ `. `.
    #             ( \  `. `-.                        _,.-:\
    #              \ \   `.  `-._             __..--' ,-';/
    #               \ `.   `-.   `-..___..---'   _.--' ,'/
    #                `. `-_   `._   `-`         /     ,'/'
    #                  \ `-._   `-._        _.-'     ,'/
    #                   `-._ `-.___ \     /` _.-'   ,,'
    #                        `-.__  `----'   _.',-'
    #                            `--..____..--'
    #         """
    #     print(banana)


if __name__ == '__main__':
    from Figure_Storage import FigureStorage

    storage = FigureStorage()
    figure = Figure(storage, (0, 0, 0))
    keys = []
    keys.append(figure.line(step=2))
    keys.append(figure.sphere(step=2))
    keys.append(figure.polygons(((0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)), step=2))
    keys.append(figure.pyramid(step=2))
    keys.append(figure.circle(step=2))
    keys.append(figure.triangle(step=2))
    keys.append(figure.square(step=2))
    keys.append(figure.cube(step=2))
    keys.append(figure.curved_line(((0, 0, 0), (1, 1, 1), (2, 2, 2)), step=2))

    print(storage.get_storage(), end='\n\n')
    for key in storage.get_keys():
        print(key, storage.get_figures(key))
    # from PointEngine import PointEngine
    # pikme = {'global_color': (1.0, 1.0, 1.0), 'points': points}
    # PointEngine(pikme)
