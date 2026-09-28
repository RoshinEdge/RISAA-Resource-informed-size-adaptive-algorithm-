import random
import math

# ============================================================================
# 1. ОПРЕДЕЛЕНИЕ ЗАДАЧИ FLOORPLANNING (целочисленный вариант)
#    Все размеры, координаты и стоимости — целые числа.
# ============================================================================

# --- 1.1. Данные о блоках (ширина, высота) — целые ---
block_sizes = [
    (20, 45),   # блок 0
    (1, 20),   # блок 1
    (40, 10),   # блок 2
    (35, 20),   # блок 3
    (50, 20),   # блок 4
    (40, 30),   # блок 0
    (10, 10),   # блок 1
    (30, 30),   # блок 2
    (34, 35),   # блок 3
    (30, 20)   # блок 4
]

# --- 1.2. Список соединений: (id_блока_A, id_блока_B, вес_связи) ---
connections = [
    (0, 1, 2),
    (0, 2, 1),
    (1, 2, 3),
    (1, 3, 1),
    (2, 4, 2),
    (3, 4, 1),
    (4, 8, 2),
    (0, 7, 10),
    (9, 5, 3),
    (5, 6, 1)
]

# --- 1.3. Параметры размещения (целые) ---
WIDTH = 100
HEIGHT = 100


# ============================================================================
# 2. КЛАСС, ПРЕДСТАВЛЯЮЩИЙ ТЕКУЩЕЕ РАЗМЕЩЕНИЕ (все целочисленное)
# ============================================================================
class Floorplan:
    def __init__(self, blocks, connections, width, height):
        """
        blocks : список кортежей (w, h) — целые
        connections : список (i, j, weight) — целые веса
        width, height : целые размеры площадки
        """
        self.blocks = blocks
        self.connections = connections
        self.width = width
        self.height = height
        self.num_blocks = len(blocks)
        
        # Генерация случайного начального размещения с целыми координатами
        self.positions = []   # список (x, y) — целые
        for (w, h) in blocks:
            # Случайное целое от 0 до (width - w) включительно
            x = random.randint(0, width - w)
            y = random.randint(0, height - h)
            self.positions.append((x, y))
        
        # Вычисляем стоимость сразу (целое число)
        self.cost = self.compute_cost()
    
    def compute_cost(self):
        """
        Целевая функция = длина соединений + штраф за перекрытия.
        Все операции целочисленные.
        """
        total = 0
        
        # ---- 2.1. Длина соединений (взвешенное манхэттенское расстояние) ----
        for (i, j, w) in self.connections:
            xi, yi = self.positions[i]
            xj, yj = self.positions[j]
            dist = abs(xi - xj) + abs(yi - yj)   # целое
            total += w * dist                    # целое
        
        # ---- 2.2. Штраф за перекрытия (целочисленный) ----
        penalty_factor = 10   # целый коэффициент
        overlap_penalty = 0
        for i in range(self.num_blocks):
            xi, yi = self.positions[i]
            wi, hi = self.blocks[i]
            for j in range(i + 1, self.num_blocks):
                xj, yj = self.positions[j]
                wj, hj = self.blocks[j]
                # Перекрытие по осям (целые)
                overlap_x = max(0, min(xi + wi, xj + wj) - max(xi, xj))
                overlap_y = max(0, min(yi + hi, yj + hj) - max(yi, yj))
                if overlap_x > 0 and overlap_y > 0:
                    overlap_area = overlap_x * overlap_y   # целое
                    overlap_penalty += penalty_factor * overlap_area
        
        total += overlap_penalty
        return total   # целое число
    
    def get_neighbor(self, step_size=1):
        """
        Генерирует соседнее решение: случайный блок сдвигается на целое число
        в диапазоне [-step_size, step_size] по каждой оси.
        step_size — целое число (по умолчанию 1).
        Возвращает новый объект Floorplan.
        """
        new_pos = self.positions[:]
        idx = random.randint(0, self.num_blocks - 1)
        x, y = new_pos[idx]
        w, h = self.blocks[idx]
        
        # Случайное целое смещение
        dx = random.randint(-step_size, step_size)
        dy = random.randint(-step_size, step_size)
        new_x = x + dx
        new_y = y + dy
        
        # Ограничиваем, чтобы блок не выходил за границы площадки
        new_x = max(0, min(new_x, self.width - w))
        new_y = max(0, min(new_y, self.height - h))
        
        new_pos[idx] = (new_x, new_y)
        
        # Создаём новый объект (без пересчёта стоимости сразу)
        new_floorplan = Floorplan.__new__(Floorplan)
        new_floorplan.blocks = self.blocks
        new_floorplan.connections = self.connections
        new_floorplan.width = self.width
        new_floorplan.height = self.height
        new_floorplan.num_blocks = self.num_blocks
        new_floorplan.positions = new_pos
        new_floorplan.cost = None
        return new_floorplan
    
    def update_cost(self):
        if self.cost is None:
            self.cost = self.compute_cost()
        return self.cost


# ============================================================================
# 3. АЛГОРИТМ ИМИТАЦИИ ОТЖИГА (температура может быть целой, охлаждение целочисленное)
# ============================================================================
def simulated_annealing_floorplan(initial_floorplan,
                                  initial_temp=1000,      # целая температура
                                  cooling_percent=99,    # целое число процентов (99 → *0.99)
                                  min_temp=1,            # целая минимальная температура
                                  max_iter=5000,
                                  step_size=1,
                                  verbose=True):
    """
    Все параметры температуры и охлаждения — целые числа.
    Критерий Метрополиса использует float только для exp, но это не влияет
    на целочисленность координат и стоимости.
    """
    current = initial_floorplan
    current_cost = current.update_cost()
    
    best = current
    best_cost = current_cost
    
    history = [current_cost]
    
    temp = initial_temp
    iteration = 0
    accepted = 0
    improvements = 0
    
    while temp >= min_temp and iteration < max_iter:
        iteration += 1
        
        neighbor = current.get_neighbor(step_size)
        neighbor_cost = neighbor.update_cost()
        delta = neighbor_cost - current_cost   # целое
        
        # Критерий Метрополиса (с использованием float для вероятности)
        # Можно заменить на целочисленную аппроксимацию, но оставим для простоты
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current = neighbor
            current_cost = neighbor_cost
            accepted += 1
            if current_cost < best_cost:
                best = current
                best_cost = current_cost
                improvements += 1
        
        # Целочисленное охлаждение: temp = temp * cooling_percent // 100
        temp = temp * cooling_percent // 100
        if temp < 1:
            temp = 1   # не даём стать нулём
        
        history.append(current_cost)
        
        if verbose and iteration % 500 == 0:
            print(f"Iter {iteration:5d} | T = {temp:3d} | "
                  f"Cost = {current_cost:5d} | Best = {best_cost:5d} | "
                  f"Accept = {accepted:5d} | Improve = {improvements:5d}")
    
    if verbose:
        print(f"\n=== ЗАВЕРШЕНО за {iteration} итераций ===")
        print(f"Принято изменений: {accepted} ({(accepted/iteration)*100:.1f}%)")
        print(f"Улучшений: {improvements}")
        print(f"Начальная стоимость: {initial_floorplan.cost}")
        print(f"Лучшая стоимость: {best_cost}")
    
    return best, best_cost, history


# ============================================================================
# 4. ЗАПУСК ПРИМЕРА
# ============================================================================
if __name__ == "__main__":
    # Создаём начальное случайное размещение
    floorplan = Floorplan(block_sizes, connections, WIDTH, HEIGHT)
    print(f"Начальная стоимость: {floorplan.cost}")
    
    # Параметры отжига (все целые)
    best, best_cost, hist = simulated_annealing_floorplan(
        floorplan,
        initial_temp=1000,
        cooling_percent=99,      # 99% от текущей температуры
        min_temp=1,
        max_iter=10000,
        step_size=2,            # целый шаг
        verbose=True
    )
    
    # Выводим финальные координаты блоков (целые)
    print("\n=== ФИНАЛЬНОЕ РАЗМЕЩЕНИЕ ===")
    for i, (x, y) in enumerate(best.positions):
        w, h = block_sizes[i]
        print(f"Блок {i}: ({x}, {y})  размер {w}x{h}")
    
    # График сходимости (опционально)
    try:
        import matplotlib.pyplot as plt
        plt.figure(figsize=(10,5))
        plt.plot(hist)
        plt.xlabel('Итерация')
        plt.ylabel('Стоимость')
        plt.title('Сходимость имитации отжига (целочисленные координаты)')
        plt.grid(True)
        plt.show()
    except ImportError:
        print("\nДля графика установите matplotlib: pip install matplotlib")