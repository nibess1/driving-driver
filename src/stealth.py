#stealth.py
from scipy import interpolate
from playwright.sync_api import Page
import numpy as np

import math
import random
import time


def point_dist(x1,y1,x2,y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    
def bezier_curve_move(page, x1, y1, x2, y2, duration):

    cp = random.randint(2, 5)  # Number of control points. Must be at least 2.

    # Distribute control points between start and destination evenly.
    x = np.linspace(x1, x2, num=cp, dtype='int')
    y = np.linspace(y1, y2, num=cp, dtype='int')

    # Randomise inner points a bit (+-RND at most).
    RND = 5
    xr = [random.randint(-RND, RND) for _ in range(cp)]
    yr = [random.randint(-RND, RND) for _ in range(cp)]
    xr[0] = yr[0] = xr[-1] = yr[-1] = 0
    x += xr
    y += yr

    # Approximate using Bezier spline.
    degree = 3 if cp > 3 else cp - 1  # Degree of b-spline. 3 is recommended.
                                    # Must be less than number of control points.
    tck, u = interpolate.splprep([x, y], k=degree)
    # Move upto a certain number of points
    u = np.linspace(0, 1, num=2+int(point_dist(x1,y1,x2,y2)/50.0))
    points = interpolate.splev(u, tck)

    # Move mouse.
    timeout = duration / len(points[0])
    point_list=zip(*(i.astype(int) for i in points))
    for point in point_list:
        page.mouse.move(*point)
        time.sleep(timeout)


def human_mouse_move(
    page: Page,
    start: tuple[float, float],
    end: tuple[float, float],
    duration: float = 0.2
) -> None:
    """
    Move the mouse from `start` to `end` over `duration` seconds,
    using ease-in/out timing and small random jitters to mimic human movement.
    
    :param page: Playwright Page object.
    :param start: (x0, y0) starting coordinates.
    :param end: (x1, y1) ending coordinates.
    :param duration: Total time in seconds for the movement.
    """
    x1, y1 = start
    x2, y2 = end
    bezier_curve_move(page, x1, y1, x2, y2, duration)



# Example usage:
# 1. Determine start and end points (e.g., from a button's center).
# 2. Call human_mouse_move before clicking.
#
# Example:
# button = page.query_selector("button.login")
# box = button.bounding_box()
# if box:
#     start_pos = (100, 100)
#     end_pos = (box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
#     human_mouse_move(page, start_pos, end_pos, duration=0.8)
#     page.mouse.click(end_pos[0], end_pos[1])

def human_wait(page, duration, current_pos, max_jitter=3, jitter_frequency=0.2):
    """
    Wait for `duration` seconds while occasionally moving the mouse by a small jitter
    to mimic natural cursor drift.

    :param page: Playwright Page object.
    :param duration: Total wait time in seconds.
    :param current_pos: Tuple (x, y) representing the mouse’s starting position.
    :param max_jitter: Maximum pixels to move in any direction.
    :param jitter_frequency: Approximate jitters per second (e.g., 0.2 → ~1 jitter every 5s).
    :return: Tuple (x, y) of the updated mouse position.
    """
    end_time = time.time() + duration
    x, y = current_pos

    while time.time() < end_time:
        # brief pause to simulate thinking/reading
        sleep_time = random.uniform(0.1, 0.3)
        time.sleep(sleep_time)

        # decide if we should jitter this interval
        if random.random() < jitter_frequency * sleep_time:
            dx = random.uniform(-max_jitter, max_jitter)
            dy = random.uniform(-max_jitter, max_jitter)
            x += dx
            y += dy
            page.mouse.move(x, y)

    return (x, y)

