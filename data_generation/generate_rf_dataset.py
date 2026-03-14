import pandas as pd
import numpy as np

# Seed for consistency
np.random.seed(42)
n_samples = 400  # Total 1600 rows of data

data = []

# Logic: 0 = SAFE, 1 = FIRE, 2 = HUMAN (POACHER)

for _ in range(n_samples):
    # --- SCENARIO 1: FIRE (Target Class 1) ---
    # ESP32 outputs "Fire" Class (ID 1) with high confidence.
    data.append([
        np.random.randint(80, 100),  # Vision_Conf (ESP32)
        1,                            # ESP32_Class (1=Fire)
        np.random.randint(60, 90),   # Audio_db (INMP441)
        1,                            # PIR_Trig (AM312 detected motion) [cite: 48]
        np.random.uniform(20, 60),   # Thermal_Delta (MLX90640 Heat) [cite: 38]
        np.random.randint(800, 2000),# Smoke_PPM (MQ-2 Smoke) [cite: 40]
        1                             # LABEL: FIRE
    ])

    # --- SCENARIO 2: HUMAN/POACHER (Target Class 2) ---
    # ESP32 outputs "Human" Class (ID 2). 
    # High Audio (Chainsaw/Footsteps) + Human Body Heat.
    data.append([
        np.random.randint(85, 100),  # Vision_Conf
        2,                            # ESP32_Class (2=Human)
        np.random.randint(75, 100),  # Audio_db
        1,                            # PIR_Trig [cite: 48]
        np.random.uniform(3, 10),    # Thermal_Delta (Body vs Ambient) [cite: 70]
        np.random.randint(200, 400), # Smoke_PPM (Normal air)
        2                             # LABEL: POACHER
    ])

    # --- SCENARIO 3: ANIMAL/SAFE (Target Class 0) ---
    # ESP32 might see "Animal" (ID 3) or "Human" (ID 2) erroneously.
    # Sensors show low heat and NO smoke.
    data.append([
        np.random.randint(30, 90),   # Vision_Conf
        np.random.choice([2, 3]),    # ESP32_Class (Human or Animal)
        np.random.randint(30, 60),   # Audio_db
        1,                            # PIR_Trig [cite: 48]
        np.random.uniform(0, 3),     # Thermal_Delta (Low heat signature)
        np.random.randint(200, 400), # Smoke_PPM
        0                             # LABEL: SAFE
    ])

    # --- SCENARIO 4: SENSOR FAILURE / BROKEN MQ-2 (Target Class 1/2) ---
    # Even if Smoke sensor is 0, the high Vision + high Thermal should still trigger.
    data.append([
        np.random.randint(90, 100),  # Vision_Conf
        1,                            # ESP32_Class (Fire)
        np.random.randint(60, 90),   # Audio_db
        1,                            # PIR_Trig [cite: 48]
        np.random.uniform(25, 50),   # Thermal_Delta [cite: 38]
        0,                            # BROKEN SENSOR (Smoke_PPM is 0)
        1                             # LABEL: FIRE (Should still be detected)
    ])

# Define column headers matching your hardware specs [cite: 34, 53]
cols = ['Vision_Conf', 'ESP32_Class', 'Audio_db', 'PIR_Trig', 'Thermal_Delta', 'Smoke_PPM', 'Label']
df = pd.DataFrame(data, columns=cols).sample(frac=1).reset_index(drop=True)
df.to_csv('sensor_data_v2.csv', index=False)

print("Success! Created 'sensor_data_v2.csv' with hardware scenarios and sensor failure simulation.")