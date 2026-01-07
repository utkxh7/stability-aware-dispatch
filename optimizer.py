# src/optimizer.py
import numpy as np

class DispatchOptimizer:
    def __init__(self, battery, electrolyzer):
        self.battery = battery
        self.electrolyzer = electrolyzer

    def solve(self, solar_mw, nuclear_mw, target_h2_kg):
        """
        Rule-Based Dispatch (The Logic):
        1. Calculate how much power the Electrolyzer NEEDS to meet demand.
        2. Check if Nuclear + Solar is enough.
        3. Use Battery to balance.
        """
        
        # Step 1: How much power do we need? (Approximate inverse of production)
        # Simplified: Assuming 50 kWh = 1 kg H2 for calculation
        power_needed_mw = (target_h2_kg * 50) / 1000 
        
        # Step 2: What is our available supply?
        total_supply_mw = solar_mw + nuclear_mw
        
        # Step 3: Calculate the Gap
        net_power = total_supply_mw - power_needed_mw
        
        # Output variables
        electrolyzer_mw = power_needed_mw # Ideally we run at this
        battery_action_mw = 0 # + is charging, - is discharging
        curtailment_mw = 0
        grid_import_mw = 0 # Stability violation check
        
        # CASE A: Surplus Power (Charge Battery)
        if net_power > 0:
            # Charge what we can
            charge_possible = min(net_power, self.battery.max_discharge_mw) # Simplified rate check
            # Check SoC limit (Can't charge if full)
            space_in_battery = self.battery.capacity_mwh - self.battery.current_soc_mwh
            # Converting MW to MWh for this timestep (15 mins = 0.25 hours)
            # But here we just decide MW rate. The update happens in main.py
            
            battery_action_mw = charge_possible
            
            # Any leftover is wasted (Curtailment)
            curtailment_mw = net_power - battery_action_mw
            
        # CASE B: Deficit Power (Discharge Battery)
        else:
            deficit = abs(net_power)
            # Discharge what we can
            discharge_possible = min(deficit, self.battery.max_discharge_mw)
            
            # We will check if battery has energy in main.py updates, 
            # but here we request the discharge.
            battery_action_mw = -discharge_possible
            
            # If still deficit, we have a problem (Grid Import / Stability Violation)
            if discharge_possible < deficit:
                grid_import_mw = deficit - discharge_possible
        
        return {
            "electrolyzer_mw": electrolyzer_mw,
            "battery_flow_mw": battery_action_mw,
            "curtailment_mw": curtailment_mw,
            "grid_import_mw": grid_import_mw, # This is your "Stability Penalty" metric
            "solar_used": solar_mw - curtailment_mw
        }