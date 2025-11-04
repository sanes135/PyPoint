class Minecraft:
    def __init__(self, global_center=(0, 0, 0), length_num=3, file_name='file', functions_path='',
                 global_particle='flame', coordinate_mode='~', size_particle=1, color_particle=1):
        self.global_center = global_center
        self.length_num = length_num
        self.file_name = file_name
        # this path for replace the function file
        self.function_path = functions_path
        self.global_particle = global_particle
        self.coordinate_mode = coordinate_mode
        # its need for unique type of particle
        self.size_particle = size_particle
        self.color_particle = color_particle

    def write_static_function(self, figures, file_name='file', colored=False, optimization=False):
        if optimization:
            pass
        with open(f'{file_name}.mcfunction', 'w+') as file:
            if colored:
                if isinstance(figures, list):
                    for figure in figures:
                        self._static_dust_function(figure, file)
                else:
                    self._static_dust_function(figures, file)
            else:
                if isinstance(figures, list):
                    for figure in figures:
                        self._static_point_function(figure, file)
                else:
                    self._static_point_function(figures, file)

    def _static_point_function(self, figure, file):
        for point in figure['points']:
            x = round(point[0] + self.global_center[0], self.length_num)
            y = round(point[1] + self.global_center[1], self.length_num)
            z = round(point[2] + self.global_center[2], self.length_num)
            file.write(f'particle {self.global_particle} '
                       f'{self.coordinate_mode}{x} {self.coordinate_mode}{y} {self.coordinate_mode}{z} 0 0 0 0 1 force @a\n')

    def _static_dust_function(self, figure, file):
        if 'global_color' in figure:
            global_color = figure['global_color']
            color = (round(global_color[0] / 255, self.length_num),
                     round(global_color[1] / 255, self.length_num),
                     round(global_color[2] / 255, self.length_num))
            for point in figure['points']:
                x = round(point[0] + self.global_center[0], self.length_num)
                y = round(point[1] + self.global_center[1], self.length_num)
                z = round(point[2] + self.global_center[2], self.length_num)
                file.write('particle dust{' + f'color:[{color[0]},{color[0]},{color[0]}],scale:{size}' + '}'
                f' {self.coordinate_mode}{x} {self.coordinate_mode}{y} {self.coordinate_mode}{z} 0 0 0 0 1 force @a')
        else:
            for i in range(len(figure['points'])):
                ind_color = figure['ind_color'][i]
                color = (round(ind_color[0] / 255, self.length_num),
                         round(ind_color[1] / 255, self.length_num),
                         round(ind_color[2] / 255, self.length_num))
                point = figure['points'][i]
                x = round(point[0] + self.global_center[0], self.length_num)
                y = round(point[1] + self.global_center[1], self.length_num)
                z = round(point[2] + self.global_center[2], self.length_num)
                file.write('particle dust{' + f'color:[{color[0]},{color[0]},{color[0]}],scale:{size}' + '}'
                f' {self.coordinate_mode}{x} {self.coordinate_mode}{y} {self.coordinate_mode}{z} 0 0 0 0 1 force @a')

    def write_animated_function(self, animation, file_name='file', delay=0, colored=False, optimization=False):
        with open(f'{file_name}.mcfunction', 'w+') as file:
            if optimization: # Not right now
                if colored:
                    self._write_colored_opt_animation(file, animation, delay)
                else:
                    self._write_opt_animation(file, animation, delay)
            else:
                if colored:
                    self._write_colored_animation(file, animation, delay)
                else:
                    self._write_animation(file, animation, delay)

    def _write_colored_animation(self, file, animation, delay):
        pass

    def _write_animation(self, file, animation, delay):
        file.write(f'scoreboard players add {file_name} anim 1\n')
        for i, frame in enumerate(animation):
            points = self._flatten_list(self._get_points(frame))
            for point in points:
                x = round(point[0] + self.global_center[0], self.length_num)
                y = round(point[1] + self.global_center[1], self.length_num)
                z = round(point[2] + self.global_center[2], self.length_num)
                file.write(f'execute if score {file_name} anim matches {(i * delay) + 1}..{(i + 1) * delay} run '           
                f'particle {self.global_particle} {self.coordinate_mode}{x} {self.coordinate_mode}{y} {self.coordinate_mode}{z} 0 0 0 0 1 force @a\n')

        file.write(f'execute if score {file_name} anim matches {(i + 1) * delay + 1}.. run scoreboard players set {file_name} anim 0\n')

    def write_code_function(self):
        # talk with deepseek
        """
        this function for write a file in a real time with your commands (in a code)
        example:
        write_add_function(points, "particle flame x y z 0 0 0 0 1")
        """
        pass

    def check_light(self, points):
        if len(points) > 16384:
            print('!!!A lot of points!!!')

    def remove_duplicate_points(self, points=None, frames=None):
        if points is None:
            cleaned_frames = []
            for frame in frames:
                unique_points = []
                for point in frame:
                    if point not in unique_points:
                        unique_points.append(point)
                cleaned_frames.append(unique_points)
            return cleaned_frames

        if frames is None:
            cleaned_points = []
            for point in points:
                if point not in cleaned_points:
                    cleaned_points.append(point)
            return cleaned_points

    def group_points_by_frames(self, frames, start_index=1):
        """
        :return: Отсортированный список в формате [[point, [frame_indices]], ...]
        """
        point_frames_map = {}

        for frame_idx, frame in enumerate(frames, start=start_index):
            unique_points = set(frame)
            for point in unique_points:
                if point not in point_frames_map:
                    point_frames_map[point] = []
                point_frames_map[point].append(frame_idx)

        result = []
        for point, frames_list in point_frames_map.items():
            result.append((point, tuple(sorted(frames_list))))

        # Сортируем по точке (лексикографический порядок)
        result.sort(key=lambda x: x[0])

        return result

    def move_file(self):
        import os
        copy = fr"{self.function_path}\{self.file_name}"
        cwd = os.getcwd()
        file = fr'{cwd}\{self.file_name}'
        where = fr'{self.function_path}'

        if os.path.exists(copy):
            shutil.copy(file, where)
            print('Complite rewrite file')
            os.remove(file)
        else:
            shutil.move(file, where)
            print('Complite move file')

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

    def _flatten_list(self, data):
        flat_list = []
        for item in data:
            if isinstance(item, list):
                flat_list.extend(item)
            else:
                flat_list.append(item)
        return flat_list
