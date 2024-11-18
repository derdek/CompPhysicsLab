import math
import pygame
import random
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

    # Надання випадкових швидкостей
    for i in range(particles_count):
        mol.vx[i] = random.uniform(-0.1, 0.1)
        mol.vy[i] = random.uniform(-0.1, 0.1)

    running = True
    snapshots = []
    temperatures = []
    pressures = []
    snapshot_interval = 25
    equilibrium_steps = 50
    averaging_steps = 100

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
        if len(snapshots) < 10 and mol.step_count % snapshot_interval == 0:
            snapshots.append((mol.x.copy(), mol.y.copy()))

        # Збереження температури та тиску
        if mol.step_count >= equilibrium_steps and mol.step_count < equilibrium_steps + averaging_steps:
            temperatures.append(mol.temperature())
            pressures.append(mol.pressure())

        # Перевірка кінця симуляції
        if mol.step_count >= equilibrium_steps + averaging_steps:
            running = False

    pygame.quit()

    # Збереження знімків у файл
    for i, snapshot in enumerate(snapshots):
        save_snapshot(
            f"snapshot_{i}.png",
            snapshot,
            container_width,
            container_height
        )

    # Виведення повної енергії системи
    total_energy = mol.pe + mol.ke
    print(f"Total energy of the system: {total_energy}")

    # Усереднення температури та тиску
    average_temperature = sum(temperatures) / len(temperatures)
    average_pressure = sum(pressures) / len(pressures)
    print(f"Average temperature: {average_temperature}")
    print(f"Average pressure: {average_pressure}")

    # Збереження рівноважної конфігурації
    equilibrium_config = (mol.x.copy(), mol.y.copy(), mol.vx.copy(), mol.vy.copy())
    with open("equilibrium_config.txt", "w") as f:
        for x, y, vx, vy in zip(*equilibrium_config):
            f.write(f"{x} {y} {vx} {vy}\n")


if __name__ == "__main__":
    main()
