import math
from helpers import save_snapshot, load_equilibrium_config
from molecular_dynamics import MolecularDynamics


def main():
    particles_count = 16
    container_width = 4
    container_height = 2 * math.sqrt(3)
    nsnap = 5  # кількість кроків між малюванням
    max_speed = 0.2
    dt = 0.01

    # Завантаження рівноважної конфігурації
    x, y, vx, vy = load_equilibrium_config("equilibrium_config.txt")

    mol = MolecularDynamics(particles_count, container_width, container_height, max_speed, dt)
    mol.x = x
    mol.y = y
    mol.vx = vx
    mol.vy = vy

    scaling_factor = 1.1
    ssf = 1
    melted = False

    while not melted:
        ssf *= scaling_factor
        # Зменшення щільності
        mol.Lx *= scaling_factor
        mol.Ly *= scaling_factor
        mol.x = [xi * scaling_factor for xi in mol.x]
        mol.y = [yi * scaling_factor for yi in mol.y]

        running = True
        temp_list = []
        pressure_list = []
        mol.step_count = 0

        while running:
            # Обчислення прискорень і інтегрування
            mol.accel()
            for _ in range(nsnap):
                mol.verlet()

            # Збереження температури та тиску
            if mol.step_count >= 50 and mol.step_count < 150:
                temp_list.append(mol.temperature())
                pressure_list.append(mol.pressure())

            # Збереження знімків
            if mol.step_count % 25 == 0:
                save_snapshot(f"snapshot_{mol.step_count}.png", (mol.x.copy(), mol.y.copy()), mol.Lx, mol.Ly)

            # Перевірка кінця симуляції
            if mol.step_count >= 150:
                running = False

        # Усереднення температури та тиску
        average_temperature = sum(temp_list) / len(temp_list)
        average_pressure = sum(pressure_list) / len(pressure_list)
        total_energy = mol.pe + mol.ke

        print(f"Scaling factor: {ssf}")
        print(f"Max temperature: {max(temp_list):.2e}")
        print(f"Max pressure: {max(pressure_list):.2e}")
        print(f"Average temperature: {average_temperature:.2e}")
        print(f"Average pressure: {average_pressure:.2e}")
        print(f"Total energy: {total_energy:.2e} Eh")
        print()

        # Перевірка на плавлення
        if not mol.is_solid():
            melted = True
            print("The system has melted.")


if __name__ == "__main__":
    main()
