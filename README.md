# Stability-Aware Dispatch for Industrial Green Hydrogen

## Overview
This project simulates an industrial microgrid (Nuclear + Solar + Battery) powering a PEM Electrolyzer.
Unlike standard models that optimize only for cost, this model includes **Grid Stability Constraints** (Frequency/Inertia proxy) to ensure the system is physically viable.

## Key Features
- **Multi-Objective Optimization:** Minimizes LCOH ($/kg) while penalizing Frequency Deviation (Hz).
- **Component constraints:** Models realistic ramp rates for Nuclear (slow) vs. Batteries (fast).
- **Electrolyzer Physics:** Includes efficiency curves relative to load factor.

## Tech Stack
- Python (Pandas, NumPy)
- Optimization: CVXPY / SciPy
- Visualization: Matplotlib
