import os

import pygame
import matplotlib.pyplot as plt


def draw_particles(screen, particles, aspect_ratio):
    for point in particles:
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (point[0] * aspect_ratio, point[1] * aspect_ratio),
            radius=20,
        )


def get_dimensions(n):
    i = int(n ** 0.5)
    while n % i != 0:
        i -= 1
    return i, n // i


def save_snapshot(filename, particles, width, height, aspect_ratio):
    dir = "snapshots"
    if not os.path.exists(dir):
        os.makedirs(dir)
    fig, ax = plt.subplots()
    for point in zip(*particles):
        ax.add_patch(plt.Circle(point, radius=0.1, color='blue'))
    ax.set_aspect('equal')
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    plt.savefig(f'{dir}/{filename}')
    plt.close(fig)
