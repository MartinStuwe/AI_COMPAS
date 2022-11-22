import pygame


def malignant_drift(player, visible_obstacles, scaling):

    drift_x = 0

    target_obstacle = None  # [x , y]
    for visible_obstacle in visible_obstacles:
        if visible_obstacle[1] > player.rect.bottom:
            target_obstacle = visible_obstacle
            if target_obstacle is not None:
                break

    if target_obstacle is not None:
        if target_obstacle[0] + scaling < player.rect.left:
            drift_x = 1 / 2
        elif target_obstacle[0] + 2 * scaling > player.rect.right:
            drift_x = - 1 / 2
        else:
            drift_x = 0

    return drift_x


def benevolent_drift(player, visible_obstacles, scaling):

    drift_x = 0

    target_obstacle = None  # [x , y]
    for visible_obstacle in visible_obstacles:
        if visible_obstacle[1] > player.rect.bottom:
            target_obstacle = visible_obstacle
            if target_obstacle is not None:
                break

    if target_obstacle is not None:
        if target_obstacle[0] + scaling < player.rect.left:  # wall_x - target_obstacle[0] + 2 * scaling = perfect line where drift is pushing towards
    return drift_x