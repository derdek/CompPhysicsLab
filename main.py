import math
import pygame
import random
import matplotlib.pyplot as plt
import numpy as np
import os
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
    mol.vx = vx
    mol.vy = vy

    # Ініціалізація початкової енергії
    mol.accel()
    initial_energy = mol.pe + mol.ke

    temperatures = []
    energies = []
    pressures = []
    temperature_factors = [1, 2, 3, 4, 5, 6]

    for factor in temperature_factors:
        mol.vx = [v * factor for v in vx]  # Збільшення швидкостей
        mol.vy = [v * factor for v in vy]  # Збільшення швидкостей

        running = True
        temp_list = []
        pressure_list = []
        mol.step_count = 0

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Обчислення прискорень і інтегрування
            mol.accel()
            for _ in range(nsnap):
                mol.verlet()

            # Збереження температури та тиску
            if mol.step_count >= 50 and mol.step_count < 150:
                temp_list.append(mol.temperature())
                pressure_list.append(mol.pressure())

            # Перевірка кінця симуляції
            if mol.step_count >= 150:
                running = False

        # Усереднення температури та тиску
        average_temperature = sum(temp_list) / len(temp_list)
        average_pressure = sum(pressure_list) / len(pressure_list)
        total_energy = mol.pe + mol.ke

        temperatures.append(average_temperature)
        energies.append(total_energy - initial_energy)
        pressures.append(average_pressure)

    pygame.quit()

    # Створення папки для збереження графіків
    output_dir = "plots"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Побудова графіків
    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(temperatures, energies, marker='o')
    plt.xlabel('Temperature (T)')
    plt.ylabel('E(T) - E(0)')
    plt.title('E(T) - E(0) vs Temperature')
    plt.grid(True)

    plt.subplot(1, 2, 2)
    plt.plot(temperatures, pressures, marker='o')
    plt.xlabel('Temperature (T)')
    plt.ylabel('Pressure (P)')
    plt.title('Pressure vs Temperature')
    plt.grid(True)

    plt.tight_layout()
    plt.savefig(f'{output_dir}/energy_pressure_vs_temperature.png')
    plt.show()

    # Перевірка пропорційності
    slope, intercept = np.polyfit(temperatures, energies, 1)
    print(f"Slope of E(T) - E(0) vs T: {slope}")

    # Порівняння з очікуваними значеннями
    expected_slope = 1.5 * particles_count  # Для гармонічного твердого тіла
    print(f"Expected slope for harmonic solid: {expected_slope}")
    print(f"Difference: {abs(slope - expected_slope)}")


if __name__ == "__main__":
    main()
