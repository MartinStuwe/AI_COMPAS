# This file contains static variables that won't change in a single run

# how "far" is the agent able to see
observation_space_size_x, observation_space_size_y = 80, 60

# environment related parameters
fall_velocity = 1
level_size_x, level_size_y = observation_space_size_x, 400
wall_size = 1
drift_tile_x_size = 1

# drift mapping
# drift = 0: leftwards drift
# drift = 2: rightwards drift

# agent related parameters
agent_size_x, agent_size_y = 1, 1

# upscaling for visualization on screen
scaling = 16
scaling_tiny_vis = 2

# edge size for screen beyond walls
edge = 4
