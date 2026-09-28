# RISAA — Resource-Informed Size-Adaptive Algorithm

![status](https://img.shields.io/badge/status-research-blue)
![platform](https://img.shields.io/badge/platform-FPGA-orange)
![language](https://img.shields.io/badge/language-Python%20%7C%20Tcl-green)
![license](https://img.shields.io/badge/license-MIT-lightgrey)

---

## 🇬🇧 English

### Overview

**RISAA** is a floorplanning algorithm for multi-FPGA prototyping that extends classical Simulated Annealing with **variable block sizes**. Instead of fixing the geometry of each module, the algorithm allows blocks to reshape during the search, adapting to the columnar architecture of modern FPGAs.

The method targets a well-known bottleneck: once device utilization exceeds 80–85%, routing delays and clock skew grow nonlinearly, and maximum operating frequency collapses. RISAA addresses this by jointly optimizing placement and block geometry under soft and hard constraints.

### Key Features

| Feature | Description |
|---|---|
| **Variable block sizes** | Width and height of each block are tuned during annealing |
| **Soft constraints** | Bounded overlap between blocks (α ≤ 0.5) |
| **Hard constraints** | Strict prohibition of intersections with keep-out zones |
| **Composite cost function** | Wirelength + overlap + forbidden zones + area overhead |
| **Multi-FPGA aware** | Partitioning across two or more dies |
| **Deterministic runtime** | All internal loops are bounded |

### Algorithm at a Glance

```
┌──────────────────────────────────────────────────────────┐
│  1. Post-synthesis analysis                              │
│     → LUT / FF / DSP / BRAM counts per module            │
│                                                          │
│  2. Minimal area estimation                              │
│     s_min = max(1, ⌈1.15 · max(LUT/2.5, FF/5.0)⌉)        │
│                                                          │
│  3. Initial placement                                    │
│     → fixed blocks pinned, movable blocks random-seeded  │
│                                                          │
│  4. Simulated annealing loop                             │
│     ┌────────────────────────────────────────────┐       │
│     │  a) propose neighbor (move or resize)      │       │
│     │  b) evaluate ΔC                            │       │
│     │  c) accept if ΔC < 0                       │       │
│     │     else accept with P = exp(−ΔC / T)      │       │
│     │  d) cool: T ← γ · T   (γ = 0.99)           │       │
│     └────────────────────────────────────────────┘       │
│                                                          │
│  5. Report best placement + timing via Vivado STA        │
└──────────────────────────────────────────────────────────┘
```

### Cost Function

$$
C = C_{conn} + C_{overlap} + C_{forbidden} + C_{area}
$$

| Term | Meaning | Weight |
|---|---|---|
| `C_conn` | Weighted Manhattan wirelength | 1 |
| `C_overlap` | Overlap area between blocks | λ = 10 |
| `C_forbidden` | Intersection with keep-out zones | λ = 1000 |
| `C_area` | Excess area over `s_min` | λ = 10 |

### Results (PicoSoC on dual Kintex-7 XC7K325T)

| Parameter | 1 FPGA, no FP | 2 FPGA, no FP | 2 FPGA + RISAA |
|---|---:|---:|---:|
| Utilization (primary) | 92 % | 78 % | **71 %** |
| WNS, ns | −2.10 | −0.90 | **−0.05** |
| F_max, MHz | 140.8 | 169.5 | **198.0** |
| Gain vs. baseline | — | +20.4 % | **+40.6 %** |

> Achieved frequency is within **1 %** of the 200 MHz target.

### Repository Structure

```
risaa/
├── src/
│   ├── risaa.py            # core annealer
│   ├── geometry.py         # overlap / keep-out predicates
│   ├── cost.py             # composite objective
│   └── io_parser.py        # XDC / Pblock reader
├── scripts/
│   ├── run_risaa.tcl       # Vivado integration
│   └── report_timing.tcl   # STA wrapper
├── examples/
│   └── picosoc/            # reference design
├── docs/
│   └── algorithm.md
└── README.md
```

### Quick Start

```bash
git clone https://github.com/<user>/risaa.git
cd risaa
pip install -r requirements.txt

python src/risaa.py \
    --design examples/picosoc/netlist.json \
    --temp-init 1000 \
    --cooling 0.99 \
    --iters 5000 \
    --resize-prob 0.3 \
    --aspect 0.2 5.0
```

### Requirements

- Python ≥ 3.9
- NumPy, SciPy
- Xilinx Vivado ≥ 2020.2 (for timing closure)
- Supported devices: Kintex-7, Virtex-7, UltraScale, UltraScale+

### Citation

```bibtex
@article{risaa2026,
  title   = {Variable-Size Floorplanning for Multi-FPGA Prototyping
             via Simulated Annealing},
  author  = {<authors>},
  journal = {IEEE Access},
  year    = {2026},
  doi     = {<doi>}
}
```

### License

MIT License. See `LICENSE` for details.

---

## 🇷🇺 Русский

### Обзор

**RISAA** — алгоритм планирования размещения для мульти-ПЛИС прототипирования, расширяющий классическую имитацию отжига возможностью **изменять размеры блоков**. Геометрия модулей не фиксируется заранее: блоки могут перестраиваться в ходе поиска, подстраиваясь под столбцовую архитектуру современных FPGA.

Метод нацелен на известное узкое место: при утилизации кристалла выше 80–85 % задержки маршрутизации и тактовый перекос растут нелинейно, а максимальная рабочая частота резко падает. RISAA решает эту проблему, оптимизируя размещение и геометрию блоков совместно, с учётом мягких и жёстких ограничений.

### Ключевые особенности

| Особенность | Описание |
|---|---|
| **Изменяемые размеры** | Ширина и высота блоков настраиваются в процессе отжига |
| **Мягкие ограничения** | Ограниченная доля перекрытий (α ≤ 0,5) |
| **Жёсткие ограничения** | Полный запрет пересечений с запретными зонами |
| **Составная целевая функция** | Длина соединений + перекрытия + запретные зоны + площадь |
| **Мульти-ПЛИС** | Разбиение на два и более кристаллов |
| **Детерминированное время** | Все внутренние циклы ограничены сверху |

### Алгоритм в двух словах

```
┌──────────────────────────────────────────────────────────┐
│  1. Постсинтезный анализ                                 │
│     → количество LUT / FF / DSP / BRAM по модулям        │
│                                                          │
│  2. Оценка минимальной площади                           │
│     s_min = max(1, ⌈1.15 · max(LUT/2.5, FF/5.0)⌉)        │
│                                                          │
│  3. Начальное размещение                                 │
│     → фиксированные блоки закреплены, остальные — случайно│
│                                                          │
│  4. Цикл имитации отжига                                 │
│     ┌────────────────────────────────────────────┐       │
│     │  a) сгенерировать соседа (сдвиг / ресайз)  │       │
│     │  b) вычислить ΔC                           │       │
│     │  c) принять, если ΔC < 0                   │       │
│     │     иначе — с вероятностью exp(−ΔC / T)    │       │
│     │  d) охладить: T ← γ · T   (γ = 0,99)       │       │
│     └────────────────────────────────────────────┘       │
│                                                          │
│  5. Отчёт: лучший план + тайминг через Vivado STA        │
└──────────────────────────────────────────────────────────┘
```

### Целевая функция

$$
C = C_{conn} + C_{overlap} + C_{forbidden} + C_{area}
$$

| Слагаемое | Смысл | Вес |
|---|---|---|
| `C_conn` | Взвешенная манхэттенская длина связей | 1 |
| `C_overlap` | Площадь перекрытий между блоками | λ = 10 |
| `C_forbidden` | Пересечение с запретными зонами | λ = 1000 |
| `C_area` | Избыточная площадь сверх `s_min` | λ = 10 |

### Результаты (PicoSoC на двух Kintex-7 XC7K325T)

| Параметр | 1 FPGA, без FP | 2 FPGA, без FP | 2 FPGA + RISAA |
|---|---:|---:|---:|
| Утилизация (осн. FPGA) | 92 % | 78 % | **71 %** |
| WNS, нс | −2,10 | −0,90 | **−0,05** |
| F_max, МГц | 140,8 | 169,5 | **198,0** |
| Прирост к базовому | — | +20,4 % | **+40,6 %** |

> Достигнутая частота отличается от целевых 200 МГц менее чем на **1 %**.

### Структура репозитория

```
risaa/
├── src/
│   ├── risaa.py            # ядро алгоритма
│   ├── geometry.py         # предикаты перекрытий и запретных зон
│   ├── cost.py             # целевая функция
│   └── io_parser.py        # чтение XDC / Pblock
├── scripts/
│   ├── run_risaa.tcl       # интеграция с Vivado
│   └── report_timing.tcl   # обёртка STA
├── examples/
│   └── picosoc/            # эталонный проект
├── docs/
│   └── algorithm.md
└── README.md
```

### Быстрый старт

```bash
git clone https://github.com/<user>/risaa.git
cd risaa
pip install -r requirements.txt

python src/risaa.py \
    --design examples/picosoc/netlist.json \
    --temp-init 1000 \
    --cooling 0.99 \
    --iters 5000 \
    --resize-prob 0.3 \
    --aspect 0.2 5.0
```

### Требования

- Python ≥ 3.9
- NumPy, SciPy
- Xilinx Vivado ≥ 2020.2 (для временного анализа)
- Поддерживаемые семейства: Kintex-7, Virtex-7, UltraScale, UltraScale+

### Цитирование

```bibtex
@article{risaa2026,
  title   = {Variable-Size Floorplanning for Multi-FPGA Prototyping
             via Simulated Annealing},
  author  = {<авторы>},
  journal = {IEEE Access},
  year    = {2026},
  doi     = {<doi>}
}
```

### Лицензия

MIT. Подробности — в файле `LICENSE`.

---

## 📊 Visual Summary

```
Utilization (%)                    F_max (MHz)
  92 ┤████████████████████  baseline   140.8 ┤██████████
  78 ┤████████████████      2 FPGA      169.5 ┤████████████
  71 ┤███████████████       RISAA       198.0 ┤██████████████
     └──────────────────                     └─────────────
```

```
   ΔF_max vs. baseline
   +50% ┤
        │                             ▲ +40.6%
   +30% ┤                             │
        │                             │
   +10% ┤              ▲ +20.4%       │
        │              │              │
     0% ┤──────────────┴──────────────┴────
                    2 FPGA        2 FPGA
                   без FP        + RISAA
```
