import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def generate_synthetic_data(days=7, step_mins=15):
    """
    Creates a Pandas DataFrame with:
    - Time Index
    - Solar Generation (Bell curve per day)
    - Nuclear Generation (Flat baseline)
    - H2 Demand (Constant industrial demand)
    """
    # 1. Create Time Index
    total_steps = int(24 * 60 / step_mins * days)
    time_index = pd.date_range(start="2025-01-01", periods=total_steps, freq=f"{step_mins}min")
    
    df = pd.DataFrame(index=time_index)
    
    # 2. Create Solar Profile (Simple Bell Curve)
    # Peak at noon (12:00), Zero at night
    x = np.linspace(0, days * 2 * np.pi, total_steps)
    # Sine wave + Shift to make night zero
    solar_curve = np.sin(x - np.pi/2) 
    # Clip negative values (Night time) to 0
    solar_curve = np.clip(solar_curve, 0, 1)
    
    df['solar_pu'] = solar_curve  # pu = Per Unit (0 to 1 scale)
    
    # 3. Create Hydrogen Demand (Industry runs 24/7)
    # Let's say demand fluctuates slightly (noise) around a target
    noise = np.random.normal(0, 0.05, total_steps)
    # Change 100 to 1000
    df['h2_demand_kg'] = 1000 + (noise * 10)
    return df

# --- Simple Test Block ---
if __name__ == "__main__":
    # If you run this file directly, it plots the data to show you it works
    data = generate_synthetic_data(days=3)
    
    plt.figure(figsize=(10, 4))
    plt.plot(data.index, data['solar_pu'], label="Solar Profile (Normalized)")
    plt.plot(data.index, data['h2_demand_kg']/200, label="H2 Demand (Scaled)")
    plt.title("Synthetic Training Data Check")
    plt.legend()
    plt.show()
    print("Data Generation Successful!")