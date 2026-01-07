# main.py
import pandas as pd
import matplotlib.pyplot as plt
from src.config import *
from src.components import NuclearPlant, SolarFarm, Electrolyzer, Battery
from src.data_loader import generate_synthetic_data
from src.optimizer import DispatchOptimizer

# 1. Setup Simulation
print("Initializing Industrial Microgrid...")
data = generate_synthetic_data(days=SIMULATION_DAYS, step_mins=TIMESTEP_MINUTES)

# Initialize Assets
nuc = NuclearPlant(capacity_mw=NUCLEAR_CAPACITY_MW, ramp_limit=NUCLEAR_RAMP_LIMIT_PCT)
sol = SolarFarm(capacity_mw=SOLAR_CAPACITY_MW)
# We add a simple Battery Class here directly if not in components yet, 
# or ensure components.py has a Battery class. 
# Let's define a simple Battery here to be safe, or assumes you added it to components.py.
# (I will assume you might need this helper class if you didn't write it earlier)

bat = Battery(capacity_mwh=BATTERY_CAPACITY_MWH, max_mw=BATTERY_MAX_DISCHARGE_MW)
# ----------------------

lyzer = Electrolyzer(ELECTROLYZER_CAPACITY_MW, ELECTROLYZER_MIN_LOAD_PCT, ELECTROLYZER_RAMP_LIMIT_PCT)

optimizer = DispatchOptimizer(bat, lyzer)

# 2. Run Simulation Loop
results = []

print(f"Running Simulation for {len(data)} timesteps...")

for t, row in data.iterrows():
    # A. Get Current Conditions
    solar_now = sol.get_generation(row['solar_pu'] * 1000) # Scaling PU to irradiance approx
    nuc_now = nuc.get_output()
    target_h2 = row['h2_demand_kg']
    
    # B. Run Optimizer (The Brain)
    decision = optimizer.solve(solar_now, nuc_now, target_h2)
    
    # C. Update Physics (The Body)
    bat.update(decision['battery_flow_mw'], timestep_hours=TIMESTEP_MINUTES/60)
    
    # D. Calculate Real H2 Produced (Physics Check)
    # The optimizer requested power, but let's see what the electrolyzer actually did
    real_h2_kg = lyzer.calculate_production(decision['electrolyzer_mw'])
    
    # Store Data
    results.append({
        "time": t,
        "solar_mw": solar_now,
        "nuclear_mw": nuc_now,
        "battery_soc_mwh": bat.current_soc_mwh,
        "grid_import_mw": decision['grid_import_mw'], # Stability Metric
        "h2_produced_kg": real_h2_kg
    })

# 3. Visualization
results_df = pd.DataFrame(results).set_index("time")

print("Simulation Complete. Plotting...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# Plot 1: Power Balance
ax1.stackplot(results_df.index, 
              results_df['nuclear_mw'], 
              results_df['solar_mw'], 
              labels=['Nuclear', 'Solar'], alpha=0.6)
ax1.set_ylabel("Power Generation (MW)")
ax1.set_title("Industrial Microgrid Dispatch (Week 1)")
ax1.legend(loc="upper left")

# Plot 2: Stability Violations (Imports)
ax2.plot(results_df.index, results_df['grid_import_mw'], color='red', label='Grid Import (Stability Violation)')
ax2.set_ylabel("Deficit Power (MW)")
ax2.set_title("Stability Violations (When Nuclear+Solar wasn't enough)")
ax2.legend()

plt.tight_layout()
plt.show()