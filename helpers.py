import pygame


def draw_particles(screen, particles, aspect_ration):
    for point in particles:
        pygame.draw.circle(
            screen,
            (255, 255, 0),
            (point[0]*aspect_ration, point[1]*aspect_ration),
            radius=20,
        )


def snapshot(screen, x, y, N, Lx, Ly, r):
    # Очищення екрану
    screen.fill((0, 0, 0))

    # Малювання частинок
    for i in range(N):
        pygame.draw.circle(screen, (0, 255, 255), (int(x[i]), int(y[i])), int(r))

    # Малювання рамки
    pygame.draw.rect(screen, (255, 0, 255), (0, 0, Lx, Ly), 1)

    # Оновлення екрану
    pygame.display.flip()


def get_dimensions(n):
    i = int(n ** 0.5)
    while n % i != 0:
        i -= 1
    return i, n // i
