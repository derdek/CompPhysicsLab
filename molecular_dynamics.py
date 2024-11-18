import math
import numpy as np
from typing import List

from helpers import get_dimensions


class MolecularDynamics:
    def __init__(self, N, Lx, Ly, vmax, dt):
        self.N = N
        self.Lx = Lx
        self.Ly = Ly
        self.vmax = vmax
        self.dt = dt
        self.dt2 = dt ** 2
        self.step_count = 0

        self.x = []
        self.y = []
        self.vx = []
        self.vy = []
        self.ax = []
        self.ay = []
        self.pe = 0  # Ініціалізація потенціальної енергії
        self.ke = 0  # Ініціалізація кінетичної енергії

        rows, cols = get_dimensions(self.N)
        pos_row = self.Ly / rows
        pos_col = self.Lx / cols
        dpos = pos_col * 0.5
        ddpos = dpos * 0.5
        for row in range(rows):
            for col in range(cols):
                if row % 2 == 0:
                    self.x.append(pos_col * (col - 0.5) - ddpos)
                else:
                    self.x.append(pos_col * (col - 0.5) + dpos - ddpos)
                self.y.append(pos_row * (row - 0.5))
                self.vx.append(0)
                self.vy.append(0)

        # Обчислення середньої швидкості (центру мас) і центрування швидкостей
        vx_cum, vy_cum = 0, 0
        for i in range(self.N):
            vx_cum += self.vx[i]
            vy_cum += self.vy[i]
        vx_cum_div_n = vx_cum / self.N
        vy_cum_div_n = vy_cum / self.N
        for i in range(self.N):
            self.vx[i] -= vx_cum_div_n
            self.vy[i] -= vy_cum_div_n

    def accel(self):
        self.ax = [0.0] * self.N
        self.ay = [0.0] * self.N
        pe = 0
        for i in range(self.N - 1):
            for j in range(i + 1, self.N):
                dx = self.x[i] - self.x[j]
                dy = self.y[i] - self.y[j]
                dx, dy = self.separation(dx, dy)
                r = math.sqrt(dx ** 2 + dy ** 2)
                force, potential = self.f(r)
                self.ax[i] += force * dx
                self.ay[i] += force * dy
                self.ax[j] -= force * dx
                self.ay[j] -= force * dy
                pe += potential
        self.pe = pe

    def separation(self, dx, dy):
        if abs(dx) > 0.5 * self.Lx:
            dx = dx - math.copysign(self.Lx, dx)
        if abs(dy) > 0.5 * self.Ly:
            dy = dy - math.copysign(self.Ly, dy)
        return dx, dy

    def periodic(self, xtemp, ytemp):
        if xtemp < 0:
            xtemp %= self.Lx
        elif xtemp >= self.Lx:
            xtemp %= self.Lx
        if ytemp < 0:
            ytemp %= self.Ly
        elif ytemp >= self.Ly:
            ytemp %= self.Ly
        return xtemp, ytemp

    @staticmethod
    def f(r):
        ri = 1 / r
        ri3 = ri ** 3
        ri6 = ri3 ** 2
        g = 24 * ri * ri6 * (2 * ri6 - 1)
        force = g / r
        potential = 4 * ri6 * (ri6 - 1)
        return force, potential

    def verlet(self):
        for i in range(self.N):
            xnew = self.x[i] + self.vx[i] * self.dt + 0.5 * self.ax[i] * self.dt2
            ynew = self.y[i] + self.vy[i] * self.dt + 0.5 * self.ay[i] * self.dt2
            self.x[i], self.y[i] = self.periodic(xnew, ynew)

        for i in range(self.N):
            self.vx[i] += 0.5 * self.ax[i] * self.dt
            self.vy[i] += 0.5 * self.ay[i] * self.dt

        self.accel()

        ke = 0
        for i in range(self.N):
            self.vx[i] += 0.5 * self.ax[i] * self.dt
            self.vy[i] += 0.5 * self.ay[i] * self.dt
            ke += 0.5 * (self.vx[i] ** 2 + self.vy[i] ** 2)
        self.ke = ke

        self.step_count += 1

    def temperature(self):
        ke = self.ke
        return ke / (self.N * 1.5)

    def pressure(self):
        virial = 0
        for i in range(self.N - 1):
            for j in range(i + 1, self.N):
                dx = self.x[i] - self.x[j]
                dy = self.y[i] - self.y[j]
                dx, dy = self.separation(dx, dy)
                r = math.sqrt(dx ** 2 + dy ** 2)
                force, _ = self.f(r)
                virial += force * r
        return self.N * self.temperature() + virial / (2 * self.Lx * self.Ly)

    def is_solid(self, threshold_velocity=0.1, rdf_threshold=0.8):
        # Розрахунок середньої кінетичної енергії
        avg_ke = self.ke / self.N
        # Розрахунок RDF
        r, g = self.calculate_rdf(self.x, self.y, self.Lx, self.Ly, r_max=self.Lx / 2, num_bins=50)
        # Перевірка умови на RDF
        if max(g) < rdf_threshold:
            return False
        # Перевірка умови на середню кінетичну енергію
        if avg_ke > threshold_velocity:
            return False
        # Інші додаткові умови (наприклад, аналіз флуктуацій)
        return True

    def calculate_rdf(self, x, y, Lx, Ly, r_max, num_bins):
        """
        Розраховує радіальну функцію розподілу (RDF) для системи частинок.

        Аргументи:
            x, y: Масиви координат частинок по осях X та Y відповідно.
            Lx, Ly: Розміри системи по осях X та Y.
            r_max: Максимальна відстань для розрахунку RDF.
            num_bins: Кількість інтервалів для гістограми RDF.

        Повертає:
            r: Масив відстаней.
            g: Масив значень RDF.
        """
        N = len(x)
        dr = r_max / num_bins
        r = np.arange(dr, r_max + dr, dr)
        g = np.zeros(num_bins)

        for i in range(N):
            for j in range(i + 1, N):
                dx = x[i] - x[j]
                dy = y[i] - y[j]
                dx, dy = self.separation(dx, dy)  # Приведення до періодичних граничних умов
                r_ij = np.sqrt(dx ** 2 + dy ** 2)
                if r_ij < r_max:
                    bin_index = int(r_ij // dr)
                    g[bin_index] += 2  # Множимо на 2, оскільки кожну пару рахуємо двічі

        # Нормалізація g(r)
        rho = N / (Lx * Ly)
        V_shell = 4 * np.pi * (r[1:] ** 3 - r[:-1] ** 3) / 3
        g[:-1] /= (rho * V_shell)

        return r, g
