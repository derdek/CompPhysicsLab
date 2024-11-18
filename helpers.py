import pygame
import matplotlib.pyplot as plt
import os


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


def save_snapshot(filename, particles, width, height):
    output_dir = "snapshots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    fig, ax = plt.subplots()
    for point in zip(*particles):
        ax.add_patch(plt.Circle(point, radius=0.1, color='blue'))
    ax.set_aspect('equal')
    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    plt.savefig(f'{output_dir}/{filename}')
    plt.close(fig)


def load_equilibrium_config(filename):
    x, y, vx, vy = [], [], [], []
    with open(filename, "r") as f:
        for line in f:
            values = line.split()
            x.append(float(values[0]))
            y.append(float(values[1]))
            vx.append(float(values[2]))
            vy.append(float(values[3]))
    return x, y, vx, vy
