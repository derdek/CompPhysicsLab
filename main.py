import math
import pygame
from helpers import draw_particles, save_snapshot, load_equilibrium_config
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

    # Завантаження рівноважної конфігурації
    x, y, vx, vy = load_equilibrium_config("equilibrium_config.txt")

    mol = MolecularDynamics(particles_count, container_width, container_height, max_speed, dt)
    mol.x = x
    mol.y = y
    mol.vx = [v * 2 for v in vx]  # Збільшення швидкостей вдвічі
    mol.vy = [v * 2 for v in vy]  # Збільшення швидкостей вдвічі

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

    # Виведення нової повної енергії системи
    total_energy = mol.pe + mol.ke
    print(f"New total energy of the system: {total_energy}")

    # Усереднення температури та тиску
    average_temperature = sum(temperatures) / len(temperatures)
    average_pressure = sum(pressures) / len(pressures)
    print(f"Average temperature: {average_temperature}")
    print(f"Average pressure: {average_pressure}")

    # Повторення збільшення температури та вимірювання P(T) та E(T) для шести різних температур
    temperature_factors = [1, 2, 3, 4, 5, 6]
    for factor in temperature_factors:
        mol.vx = [v * factor for v in vx]  # Збільшення швидкостей
        mol.vy = [v * factor for v in vy]  # Збільшення швидкостей

        running = True
        temperatures = []
        pressures = []
        mol.step_count = 0

        while running:
            # Обчислення прискорень і інтегрування
            mol.accel()
            for _ in range(nsnap):
                mol.verlet()

            # Збереження температури та тиску
            if mol.step_count >= equilibrium_steps and mol.step_count < equilibrium_steps + averaging_steps:
                temperatures.append(mol.temperature())
                pressures.append(mol.pressure())

            # Перевірка кінця симуляції
            if mol.step_count >= equilibrium_steps + averaging_steps:
                running = False

        # Усереднення температури та тиску
        average_temperature = sum(temperatures) / len(temperatures)
        average_pressure = sum(pressures) / len(pressures)
        total_energy = mol.pe + mol.ke
        print(f"Temperature factor: {factor}")
        print(f"Average temperature: {average_temperature}")
        print(f"Average pressure: {average_pressure}")
        print(f"Total energy: {total_energy}")
        print()


if __name__ == "__main__":
    main()
