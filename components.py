# src/components.py
import numpy as np

class NuclearPlant:
    def __init__(self, capacity_mw, ramp_limit):
        self.capacity = capacity_mw
        self.ramp_limit = ramp_limit
        self.current_output = capacity_mw # Starts at full power (Baseload)

    def get_output(self):
        # Nuclear prefers to stay flat.
        # In future, we can add logic to lower it, but for now, it's baseload.
        return self.current_output

class SolarFarm:
    def __init__(self, capacity_mw, efficiency=0.20):
        self.capacity = capacity_mw
        self.efficiency = efficiency
    
    def get_generation(self, irradiance_w_m2):
        """
        Input: Solar Irradiance (Watts per square meter)
        Output: MW generated
        Formula: Area * Efficiency * Irradiance (Simplified for simulation)
        """
        # Simplified: Assuming capacity is achieved at 1000 W/m2 standard test conditions
        generation_mw = self.capacity * (irradiance_w_m2 / 1000.0)
        return generation_mw

class Electrolyzer:
    def __init__(self, capacity_mw, min_load_pct, ramp_limit_pct):
        self.capacity = capacity_mw
        self.min_load_mw = capacity_mw * min_load_pct
        self.ramp_limit_mw = capacity_mw * ramp_limit_pct
        self.current_load_mw = 0 # Starts off
    
    def get_efficiency(self, load_mw):
        """
        The 'Secret Sauce' for your interview.
        Real electrolyzers drop efficiency at low loads.
        """
        load_pct = load_mw / self.capacity
        
        # Simple curve: If load < 20%, efficiency drops hard.
        if load_pct < 0.20:
            return 0.50 # Terrible efficiency
        elif load_pct > 0.90:
            return 0.65 # Good efficiency (Heating losses start)
        else:
            return 0.70 # Peak efficiency
    
    def calculate_production(self, power_input_mw):
        # Constraint Check 1: Min Load
        if power_input_mw < self.min_load_mw and power_input_mw > 0:
            print(f"Warning: Power {power_input_mw}MW is below Min Load. Shutting down.")
            return 0 # Shutdown
            
        efficiency = self.get_efficiency(power_input_mw)
        # 1 kg H2 roughly takes 50 kWh of electricity (approx)
        h2_produced_kg = (power_input_mw * 1000) / 50 * efficiency 
        return h2_produced_kg
    
# ... (SolarFarm and Electrolyzer classes are above)

class Battery:
    def __init__(self, capacity_mwh, max_mw):
        self.capacity_mwh = capacity_mwh
        self.current_soc_mwh = capacity_mwh * 0.5 # Start 50% full
        self.max_discharge_mw = max_mw
    
    def update(self, flow_mw, timestep_hours=0.25):
        """
        Update the State of Charge (SoC).
        flow_mw: Positive = Charging, Negative = Discharging
        """
        energy_change = flow_mw * timestep_hours
        self.current_soc_mwh += energy_change
        
        # Physics Constraint: Cannot go below 0 or above Capacity
        self.current_soc_mwh = max(0, min(self.current_soc_mwh, self.capacity_mwh))