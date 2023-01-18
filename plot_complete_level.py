import matplotlib.pyplot as plt
import numpy as np
from helper_functions import get_wall_positions, get_player_positions, get_obstacles_lists, get_drift_ranges
from config import scaling, level_size_x


trial = 6

pixel_move_y_direction = 5
FPS = 60
time_step = 1000/FPS

player_starting_pos = get_player_positions('0_vis.csv')[0]

wall_list_file = f'walls_dict_{trial}.csv'
wall_list = get_wall_positions(wall_list_file)

distance = len(wall_list)*scaling - player_starting_pos[1]*scaling
steps = distance / pixel_move_y_direction
time_complete_in_s = (steps*time_step) / 1000

obstacles_lists_file = f'obstacles_list_{trial}.csv'
obstacles_list, flag_multiple_obstacle_lists = get_obstacles_lists(obstacles_lists_file)

drift_ranges_file = f'drift_ranges_{trial}.csv'
drift_ranges = get_drift_ranges(drift_ranges_file)

fig, ax = plt.subplots(figsize=(3, 12), dpi=80)

ax.set_title('level setup')
ax.set_xlim(-10, level_size_x+10)
ax.set_xticks(np.arange(0, 41, step=20))

level_size_y = len(wall_list)
ax.set_ylim(0, level_size_y)
ax.set_yticks(np.arange(0, level_size_y+1, step=50))

for key in obstacles_list:
    plt.plot(key['x'], key['y'], color='green', marker='o', markersize=key['size'])  # arguments in Comet(): x-pos, y-pos, tile_size

for i in range(1, len(wall_list) + 1):
    # left wall
    left_wall_x_pos = (wall_list[str(i)][0])
    ax.plot(left_wall_x_pos, i, color='black', marker='s', markersize=1)
    # i*scaling will result in the correct y-coord of the wall

    # right wall
    right_wall_x_pos = (wall_list[str(i)][1])
    ax.plot(right_wall_x_pos, i, color='black', marker='s', markersize=1)

for drift_info in drift_ranges:
    for i in range(drift_info[0], drift_info[1]+1):
        ax.plot(20 + drift_info[2]*12.5, i, color='red', marker='s', markersize=1)

# scale and invert axes
ax = plt.gca()
ax.set_aspect('equal', adjustable='box')
ax.invert_yaxis()

# add time axis
sec_y_axis = ax.secondary_yaxis('right', functions=(lambda x: x/(level_size_y/time_complete_in_s), lambda x: x/(level_size_y/time_complete_in_s)))
sec_y_axis.set_ylabel('time in seconds')
sec_y_axis.set_yticks(np.arange(0, time_complete_in_s, step=2))
sec_y_axis.invert_yaxis()

# plt.grid(True)

plt.savefig(f'complete_design_level_{trial}.png')
plt.show()
