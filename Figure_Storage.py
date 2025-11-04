import numpy as np


class FigureStorage:
    def __init__(self, storage=None):
        self.storage = storage.deepcopy() if storage else {}

        # Переменные для add_figure
        self.max_nums = {'line': 0, 'sphere': 0, 'square': 0, 'triangle': 0,
                         'circle': 0,
                         'pyramid': 0, 'polygons': 0, 'cube': 0,
                         'curved-line': 0,
                         'banana': 0}

    # add
    def add_figure(self, name_figure):
        if name_figure not in self.max_nums:
            self.max_nums[name_figure] = 0
        self.max_nums[name_figure] += 1
        key = f"{name_figure}_{self.max_nums[name_figure]}"
        self.storage[key] = {'global_color': (0, 0, 0), 'points': []}
        return key

    def add_points(self, key, points):
        if 'points' in self.storage[key].keys():
            self.storage[key]['points'].append(points)

    # set
    def set_points(self, keys='all', points=()):
        if keys == 'all':
            if len(self.storage.keys()) != len(points):
                raise ValueError("Not enough points to set!")
            for i, key in enumerate(self.storage.keys()):
                self.storage[key]['points'] = points[i]
        elif isinstance(keys, (list, tuple)):
            if len(keys) != len(points):
                raise ValueError("Not enough points to set!")
            for i, key in enumerate(keys):
                self.storage[key]['points'] = points[i]
        else:
            self.storage[keys]['points'] = points

    # def set_color(self, keys='all', colors=()):
    #     if keys == 'all':
    #         if len(self.storage.keys()) != len(colors):
    #             raise ValueError("Not enough points to set!")
    #         for i, key in enumerate(self.storage.keys()):
    #             if self.get_depth(colors[i]) == 0:  # global_color
    #                 if 'ind_color' in self.storage[key]:
    #                     self.storage[key].pop('ind_color')
    #                 self.storage[key]['global_color'] = colors[i]
    #             else:  # ind_color
    #                 if 'global_color' in self.storage[key]:
    #                     self.storage[key].pop('global_color')
    #                 self.storage[key]['ind_color'] = colors[i]
    #     elif isinstance(keys, (list, tuple)):
    #         if len(keys) != len(colors):
    #             raise ValueError("Not enough points to set!")
    #         for i, key in enumerate(keys):
    #             if self.get_depth(colors[i]) == 0:  # global_color
    #                 if 'ind_color' in self.storage[key]:
    #                     self.storage[key].pop('ind_color')
    #                 self.storage[key]['global_color'] = colors[i]
    #             else:  # ind_color
    #                 if 'global_color' in self.storage[key]:
    #                     self.storage[key].pop('global_color')
    #                 self.storage[key]['ind_color'] = colors[i]
    #     else:
    #         if self.get_depth(colors) == 0:  # global_color
    #             if 'ind_color' in self.storage[keys]:
    #                 self.storage[keys].pop('ind_color')
    #             self.storage[keys]['global_color'] = colors
    #         else:  # ind_color
    #             if 'global_color' in self.storage[keys]:
    #                 self.storage[keys].pop('global_color')
    #             self.storage[keys]['ind_color'] = colors

    def set_figure(self, key, figure):
        self.storage[key] = figure

    # delete
    def delete_figure(self, key):
        self.storage.pop(key)

    def clear_storage(self):
        self.storage.clear()

    def delete_points_duplicate(self, keys='all'):
        points = self._delete_points_duplicate(self.get_points(keys))
        self.set_points(keys, points)

    def _delete_points_duplicate(self, points):
        unique_list = []
        seen = set()
        if self.get_depth(points) == 1:
            for item in points:
                if item not in seen:
                    unique_list.append(item)
                    seen.add(item)
        else:
            for items in points:
                unique_items = []
                seen = set()
                for item in items:
                    if item not in seen:
                        unique_items.append(item)
                        seen.add(item)
                unique_list.append(unique_items)
        return unique_list

    # get
    def get_figures(self, keys):
        if keys == 'all':
            return list(self.storage.values())
        elif isinstance(keys, (list, tuple)):
            return [self.storage.get(k) for k in keys]
        return self.storage.get(keys)

    def get_storage(self):
        return self.storage

    def get_keys(self, points=None, color=None):
        keys = []
        if points is not None:
            for i, p in enumerate(self.get_points('all')):
                if point == p:
                    keys.append(self.storage.keys()[i])
        if color is not None:
            for i, c in enumerate(self.get_colors('all')):
                if color == c:
                    keys.append(self.storage.keys()[i])

        if points is None and color is None:
            return list(self.storage.keys())
        else:
            return keys

    def get_points(self, keys):
        if keys == 'all':
            return [self.storage.get(k)['points'] for k in self.storage]
        elif isinstance(keys, (list, tuple)):
            return [self.storage.get(k)['points'] for k in keys]
        return self.storage.get(keys)['points']

    def get_colors(self, keys):
        if keys == 'all':
            return [self.storage.get(k).get('ind_color', self.storage.get(k)['global_color']) for k in self.storage]
        elif isinstance(keys, (list, tuple)):
            return [self.storage.get(k).get('ind_color', self.storage.get(k)['global_color']) for k in keys]
        return self.storage.get(keys).get('ind_color', self.storage.get(keys)['global_color'])

    def get_depth(self, data):
        if not isinstance(data, list):
            return 0
        if not data:
            return 1
        return 1 + max(self.get_depth(item) for item in data)

    # def _flatten(self, data):
    #     flat = []
    #     for item in data:
    #         if isinstance(item, list):
    #             flat.extend(self._flatten(item))
    #         else:
    #             flat.append(item)
    #     return flat
    #
    # def prepare_for_rendering(self):
    #     clear_list = self.clear_list
    #     np_array = np.array
    #     float32 = np.float32
    #
    #     for key, values in self.storage.items():
    #         if 'frames' in values:
    #             frames = values['frames']
    #             for f_i, frame in enumerate(frames):
    #                 if 'global_color' in frame:
    #                     points = np_array(clear_list(frame['points']), dtype=float32)
    #                     frames[f_i] = {"points": points, 'global_color': frame['global_color']}
    #                 else:
    #                     points = np_array(clear_list(frame['points']), dtype=float32)
    #                     colors = np_array(clear_list(frame['individual_color']), dtype=float32)
    #                     frames[f_i] = {
    #                         "points": np.hstack((
    #                             points.reshape(-1, 3),
    #                             colors.reshape(-1, 3)
    #                         )).flatten()
    #                     }
    #             values['frames'] = frames
    #         else:
    #             if 'global_color' in values:
    #                 values['points'] = np_array(clear_list(values['points']), dtype=float32)
    #             else:
    #                 points = np_array(clear_list(values['points']), dtype=float32)
    #                 colors = np_array(clear_list(values['individual_color']), dtype=float32)
    #                 values = np.hstack((
    #                     points.reshape(-1, 3),
    #                     colors.reshape(-1, 3)
    #                 )).flatten()
    #
    #         self.storage[key] = values
    #
    # def _clear_list(self, data):
    #     flat = []
    #     stack = []
    #     current = iter(data)
    #     while True:
    #         try:
    #             item = next(current)
    #         except StopIteration:
    #             if not stack:
    #                 break
    #             current = stack.pop()
    #             continue
    #         if isinstance(item, (list, tuple)):
    #             stack.append(current)
    #             current = iter(item)
    #         else:
    #             flat.append(item)
    #     return flat
    #
    #
    # def _create_for_test(self):
    #     self.storage = {'{name}_{num}': {'global_color': (1.0, 1.0, 1.0),
    #                                             'points': [(0, 0, 0), (1, 1, 1)]},
    #
    #                     'picture_{num}': {'points': [(1, 1, 1), (2, 2, 2)],
    #                                       'ind_color': [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]},
    #
    #                     'animation_{num}': {'global_color': (1.0, 1.0, 1.0),
    #                                         'frames': {
    #                                             'points': [(1, 1, 1), (2, 2, 2)],
    #                                             'global_color': (1.0, 1.0, 1.0)}},
    #
    #                     'video_{num}': {'delay': 1,
    #                                     'frames': {
    #                                         'points': [(1, 1, 1), (2, 2, 2)],
    #                                         'ind_color': [(1.0, 1.0, 1.0), (1.0, 1.0, 1.0)]}},
    #
    #                     'special_{num}': "dont understand whats types"}


if __name__ == "__main__":
    print("Run Storage")
    storage = Storage()
    # for i in range(11):
    #     key = storage.add_figure('figure', 'line')
    #     l = [(0, 0, 0), (1, 1, 1)]
    #     storage.add_points(key, l)
    # print(storage.get_storage())
    # storage.set_points(key, [(12, 12, 12)])
    # print(storage.get_storage())
    a = [[(0, 0, 0), (0, 0, 0)]]
    print(storage._delete_duplicate(a))
