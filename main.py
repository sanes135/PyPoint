from pypoint import PyPoint
# from PointEngine import PointEngine
from time import time
from Minecraft import Minecraft
from random import randint

def main():
    ppg = PyPoint(global_center=(0, 0, 0))

    # pe = PointEngine(ppg.storage)
    # while pe.get_status():
    #     pe.update_window()

    # key = ppg.figure.pyramid((10, 10, 10), 100, 10)

    key1 = ppg.figure.cube((3, 3, 3), 20)
    key2 = ppg.figure.sphere((3, 3, 3), 19 * 12)
    figure = ppg.get_figures([key1, key2])
    ppg.animation.add_scale(figure, (0, 0, 0), 80)

    mine = Minecraft(global_particle='crit',
                     functions_path=r'C:\Users\79222\AppData\Roaming\PrismLauncher\instances\1.21.6(1)\.minecraft\saves\Новый мир\datapacks\math\data\math\function')
    mine.write_animated_function(ppg.get_animation(), 'two', 1)
    # mine.write_static_function(ppg.get_figures(key), 'test_pyramid')
    mine.move_file('two.mcfunction')


if __name__ == '__main__':
    main()
