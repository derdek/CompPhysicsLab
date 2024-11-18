import math
import pygame
from helpers import draw_particles, save_snapshot
from molecular_dynamics import MolecularDynamics


def main():
    fps = 30
    delay = 1000 // fps

    particles_count = 16
    container_width = 4
    container_height = 2 * math.sqrt(3)
    nsnap = 5  # кількість кроків між малюванням
    max_speed = 0.2
    dt = 0.01

    aspect_ratio = 300

    # Ініціалізація Pygame
    pygame.init()
    screen = pygame.display.set_mode((container_width * aspect_ratio, container_height * aspect_ratio))
    pygame.display.set_caption("Molecular dynamics")

    mol = MolecularDynamics(particles_count, container_width, container_height, max_speed, dt)

    running = True
    snapshots = []
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("The simulation was interrupted by the user.")
                running = False

        # Обчислення прискорень і інтегрування
        mol.accel()
        for _ in range(nsnap):
            mol.verlet()

        # Візуалізація
        screen.fill((0, 0, 0))  # Очищення екрану
        draw_particles(screen, zip(mol.x, mol.y), aspect_ratio)
        pygame.display.flip()
        pygame.time.delay(delay)

        # Збереження знімків
        if len(snapshots) < 10:
            snapshots.append((mol.x.copy(), mol.y.copy()))

    pygame.quit()

    # Збереження знімків у файл
    for i, snapshot in enumerate(snapshots):
        save_snapshot(
            f"snapshot_{i}.png",
            snapshot,
            container_width,
            container_height,
            aspect_ratio
        )

    # Виведення повної енергії системи
    total_energy = mol.pe + mol.ke
    print(f"Total energy of the system: {total_energy}")

    # Перевірка стану системи
    if mol.is_solid():
        print("The system remains in the solid state.")
    else:
        print("The system is not in the solid state.")


if __name__ == "__main__":
    main()
