"""Constants for the Dual Frequency BIA integration."""

from __future__ import annotations

DOMAIN = "dual_frequency_bia"

# Config keys - user profile
CONF_BIRTHDAY = "birthday"
CONF_GENDER = "gender"
CONF_HEIGHT = "height"
CONF_PROFILE_ID = "profile_id"

# Config keys - source sensors
CONF_SENSOR_WEIGHT = "sensor_weight"
CONF_SENSOR_IMPEDANCE_HIGH = "sensor_impedance_high"
CONF_SENSOR_IMPEDANCE_LOW = "sensor_impedance_low"
CONF_SENSOR_HEART_RATE = "sensor_heart_rate"
CONF_SENSOR_PROFILE_ID = "sensor_profile_id"

# Debounce delay (seconds) for batching rapid BLE sensor updates
DEBOUNCE_DELAY = 2.0

# --- Dual-frequency BIA regression coefficients ---
# TBW from 250kHz impedance (Sun et al. 2003)
# Male:   TBW = 1.203 + 0.449 * (Ht^2 / Z_high) + 0.176 * Weight
# Female: TBW = 3.747 + 0.450 * (Ht^2 / Z_high) + 0.113 * Weight
TBW_MALE_INTERCEPT = 1.203
TBW_MALE_HT2Z = 0.449
TBW_MALE_WEIGHT = 0.176
TBW_FEMALE_INTERCEPT = 3.747
TBW_FEMALE_HT2Z = 0.450
TBW_FEMALE_WEIGHT = 0.113

# ECW from 50kHz impedance (Kyle et al. 2004, Sergi et al. 2015)
# Male:   ECW = -1.519 + 0.229 * (Ht^2 / Z_low) + 0.074 * Weight + 0.021 * Age
# Female: ECW = -0.073 + 0.174 * (Ht^2 / Z_low) + 0.039 * Weight + 0.023 * Age
ECW_MALE_INTERCEPT = -1.519
ECW_MALE_HT2Z = 0.229
ECW_MALE_WEIGHT = 0.074
ECW_MALE_AGE = 0.021
ECW_FEMALE_INTERCEPT = -0.073
ECW_FEMALE_HT2Z = 0.174
ECW_FEMALE_WEIGHT = 0.039
ECW_FEMALE_AGE = 0.023

# FFM hydration constant (Wang et al. 1999)
FFM_HYDRATION = 0.73

# ECW/TBW ratio normal range
ECW_TBW_RATIO_LOW = 0.36
ECW_TBW_RATIO_HIGH = 0.40

# --- Derived metric coefficients ---

# BMR (Mifflin-St Jeor)
# Male:   BMR = 10 * weight + 6.25 * height - 5 * age + 5
# Female: BMR = 10 * weight + 6.25 * height - 5 * age - 161
BMR_WEIGHT = 10.0
BMR_HEIGHT = 6.25
BMR_AGE = 5.0
BMR_MALE_OFFSET = 5.0
BMR_FEMALE_OFFSET = -161.0

# Visceral fat estimation (empirical, from bodymiscale/Xiaomi reverse-engineering)
# These are piecewise-linear approximations based on age, weight, height, gender.
# Male baseline
VF_MALE_COEFF_1 = 120.0
VF_MALE_COEFF_2 = 0.10
VF_MALE_COEFF_3 = 0.15
VF_MALE_COEFF_4 = 0.55
VF_MALE_COEFF_5 = 0.70
# Female baseline
VF_FEMALE_COEFF_1 = 120.0
VF_FEMALE_COEFF_2 = 0.10
VF_FEMALE_COEFF_3 = 0.15
VF_FEMALE_COEFF_4 = 0.55
VF_FEMALE_COEFF_5 = 0.70

# Bone mass estimation coefficients (Xiaomi empirical)
BONE_MALE_BASE = 0.18016894
BONE_MALE_COEFF = -0.00068
BONE_FEMALE_BASE = 0.245691014
BONE_FEMALE_COEFF = -0.000912

# --- Validation ranges ---
WEIGHT_MIN = 10.0
WEIGHT_MAX = 300.0
IMPEDANCE_MIN = 50.0
IMPEDANCE_MAX = 3000.0
HEIGHT_MIN = 50  # cm
HEIGHT_MAX = 250  # cm
HEART_RATE_MIN = 30
HEART_RATE_MAX = 250
PROFILE_ID_MIN = 1
PROFILE_ID_MAX = 16
