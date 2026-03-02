# Dual Frequency BIA

A Home Assistant custom integration that calculates body composition metrics using **dual-frequency bioelectrical impedance analysis (BIA)** from Xiaomi scales that provide both 250kHz and 50kHz impedance values.

## Why Dual-Frequency?

Consumer BIA scales typically use a single frequency (50kHz), which can only estimate total body impedance. The Xiaomi S400 scale measures at **two frequencies**:

- **250kHz (high frequency)** — penetrates all body water compartments, used to estimate **Total Body Water (TBW)**
- **50kHz (low frequency)** — primarily measures extracellular water, used to estimate **Extracellular Water (ECW)**

By using both frequencies, this integration can separately estimate ECW and intracellular water (ICW), providing more accurate body composition analysis than single-frequency approaches.

## Formulas

This integration uses **published, peer-reviewed regression equations** rather than reverse-engineered proprietary formulas:

| Metric | Formula Source |
|--------|---------------|
| Total Body Water (TBW) | Sun et al. 2003 (Am J Clin Nutr) |
| Extracellular Water (ECW) | Kyle et al. 2004 (Nutrition) |
| Fat-Free Mass (FFM) | Wang et al. 1999 (FFM hydration constant = 0.73) |
| Basal Metabolic Rate | Mifflin-St Jeor 1990 |
| Ideal Weight | Devine formula |
| Body Fat, LBM, Water% | Derived from TBW/FFM |
| Visceral Fat, Bone Mass | Empirical estimation (age/weight/height/gender) |

## Sensors

All sensors require weight + both impedance values:

- **Weight** (kg), **BMI**, **Ideal weight** (kg)
- **Total body water** (L), **Extracellular water** (L), **Intracellular water** (L)
- **Fat-free mass** (kg), **Body fat** (%), **Lean body mass** (kg)
- **Water** (%), **Bone mass** (kg), **Muscle mass** (kg)
- **Basal metabolism** (kcal), **Visceral fat**, **Metabolic age** (years)
- **Protein** (%), **Body score** (0-100)
- **ECW/TBW ratio**, **ECW/TBW status** (normal/low/high)
- **Heart rate** (bpm, passthrough if configured)

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to Integrations → three-dot menu → Custom Repositories
3. Add this repository URL, category: Integration
4. Install "Dual Frequency BIA"
5. Restart Home Assistant

### Manual

Copy `custom_components/dual_frequency_bia/` to your Home Assistant `config/custom_components/` directory.

## Configuration

1. Go to **Settings → Devices & Services → Add Integration**
2. Search for "Dual Frequency BIA"
3. **Step 1 — User Profile**: Enter name, date of birth, gender, height, and optional scale profile ID
4. **Step 2 — Source Sensors**: Select the weight, impedance (250kHz), impedance (50kHz), and optional heart rate sensors from your scale

### Multi-Person Setup

Add a separate config entry for each person:
- Set the **Profile ID** (1-16) matching the scale's user profile
- Select the **Profile ID sensor** to gate measurements to the correct person
- The integration will only calculate metrics when the profile ID matches

### Single-Person Setup

Leave Profile ID empty — all measurements will be processed.

## Requirements

- A Xiaomi scale that provides **both** impedance values via BLE (e.g., Xiaomi S400)
- The `xiaomi_ble` integration (or similar) exposing weight, impedance, and impedance_low sensors
- Home Assistant 2024.1+

## ECW/TBW Ratio

The ECW/TBW ratio is a clinically meaningful indicator:

| Range | Status | Meaning |
|-------|--------|---------|
| < 0.38 | Low | Very muscular / high ICW |
| 0.38 - 0.45 | Normal | Healthy fluid distribution |
| > 0.45 | High | May indicate edema or fluid retention |

> **Note:** These thresholds are calibrated for the Sun 2003 + Kyle 2004 equation pair, which structurally produces ratios of 0.40-0.44 for healthy adults. InBody devices use tighter ranges (0.36-0.39) based on their proprietary algorithms — those values are not comparable.
