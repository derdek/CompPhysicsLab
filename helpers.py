import pygame


def draw_particles(screen, particles, aspect_ration):
    for point in particles:
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (point[0]*aspect_ration, point[1]*aspect_ration),
            radius=20,
        )


def get_dimensions(n):
    i = int(n ** 0.5)
    while n % i != 0:
        i -= 1
    return i, n // i
