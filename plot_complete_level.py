import matplotlib.pyplot as plt
import numpy as np
from helper_functions import get_wall_positions, get_obstacles_lists, get_drift_ranges
from config import level_size_x


wall_list_file = 'walls_dict_8.csv'
wall_list = get_wall_positions(wall_list_file)

obstacles_lists_file = 'obstacles_list_8.csv'
obstacles_list, flag_multiple_obstacle_lists = get_obstacles_lists(obstacles_lists_file)

drift_ranges_file = 'drift_ranges_8.csv'
drift_ranges = get_drift_ranges(drift_ranges_file)

plt.figure(figsize=(3, 12), dpi=80)

plt.title('level setup')
plt.xlim(-10, level_size_x+10)
plt.xticks(np.arange(0, 41, step=20))

level_size_y = len(wall_list)
plt.ylim(0, level_size_y)
plt.yticks(np.arange(0, level_size_y+1, step=20))

for key in obstacles_list:
    plt.plot(key['x'], key['y'], color='green', marker='o', markersize=key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size

for i in range(1, len(wall_list) + 1):
    # left wall
    left_wall_x_pos = (wall_list[str(i)][0])
    plt.plot(left_wall_x_pos, i, color='black', marker='s', markersize=1)
    # i*scaling will result in the correct y-coord of the wall

    # right wall
    right_wall_x_pos = (wall_list[str(i)][1])
    plt.plot(right_wall_x_pos, i, color='black', marker='s', markersize=1)

for drift_info in drift_ranges:
    for i in range(drift_info[0], drift_info[1]+1):
        plt.plot(20 + drift_info[2]*12.5, i, color='red', marker='s', markersize=1)

ax = plt.gca()
ax.set_aspect('equal', adjustable='box')
ax.invert_yaxis()

# plt.grid(True)
plt.show()
