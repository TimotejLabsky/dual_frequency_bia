"""Dual-frequency BIA body composition formulas.

Primary references:
- Sun et al. (2003) - TBW prediction from multi-frequency BIA
- Kyle et al. (2004) - ECW prediction from multi-frequency BIA
- Mifflin-St Jeor (1990) - BMR estimation
- Wang et al. (1999) - FFM hydration constant (0.73)

Derived metrics (visceral fat, bone mass, muscle mass, metabolic age, protein)
use empirical formulas reverse-engineered from Xiaomi Mi Body Composition scales
(via bodymiscale HACS integration).
"""

from __future__ import annotations

from ..const import (
    BMR_AGE,
    BMR_FEMALE_OFFSET,
    BMR_HEIGHT,
    BMR_MALE_OFFSET,
    BMR_WEIGHT,
    BONE_FEMALE_BASE,
    BONE_MALE_BASE,
    ECW_FEMALE_AGE,
    ECW_FEMALE_HT2Z,
    ECW_FEMALE_INTERCEPT,
    ECW_FEMALE_WEIGHT,
    ECW_MALE_AGE,
    ECW_MALE_HT2Z,
    ECW_MALE_INTERCEPT,
    ECW_MALE_WEIGHT,
    ECW_TBW_RATIO_HIGH,
    ECW_TBW_RATIO_LOW,
    FFM_HYDRATION,
    TBW_FEMALE_HT2Z,
    TBW_FEMALE_INTERCEPT,
    TBW_FEMALE_WEIGHT,
    TBW_MALE_HT2Z,
    TBW_MALE_INTERCEPT,
    TBW_MALE_WEIGHT,
)
from ..models import ECWTBWStatus, Gender, UserProfile


def calc_bmi(weight: float, height_m: float) -> float:
    """BMI = weight / height^2."""
    return round(weight / (height_m**2), 1)


def calc_ideal_weight(height_m: float, gender: Gender) -> float:
    """Ideal weight using Devine formula.

    Male:   50.0 + 2.3 * ((height_cm - 152.4) / 2.54)
    Female: 45.5 + 2.3 * ((height_cm - 152.4) / 2.54)
    """
    height_cm = height_m * 100
    inches_over_60 = (height_cm - 152.4) / 2.54
    base = 50.0 if gender == Gender.MALE else 45.5
    return round(max(base + 2.3 * inches_over_60, base), 1)


def calc_bmr(weight: float, height_cm: float, age: float, gender: Gender) -> int:
    """Basal Metabolic Rate using Mifflin-St Jeor equation.

    Male:   BMR = 10 * weight + 6.25 * height - 5 * age + 5
    Female: BMR = 10 * weight + 6.25 * height - 5 * age - 161
    """
    offset = BMR_MALE_OFFSET if gender == Gender.MALE else BMR_FEMALE_OFFSET
    bmr = BMR_WEIGHT * weight + BMR_HEIGHT * height_cm - BMR_AGE * age + offset
    return round(max(bmr, 0))


def calc_tbw(
    weight: float, height_cm: float, impedance_high: float, gender: Gender
) -> float:
    """Total Body Water from 250kHz impedance (Sun et al. 2003).

    Male:   TBW = 1.203 + 0.449 * (Ht^2 / Z_high) + 0.176 * Weight
    Female: TBW = 3.747 + 0.450 * (Ht^2 / Z_high) + 0.113 * Weight
    """
    ht2_z = (height_cm**2) / impedance_high
    if gender == Gender.MALE:
        tbw = TBW_MALE_INTERCEPT + TBW_MALE_HT2Z * ht2_z + TBW_MALE_WEIGHT * weight
    else:
        tbw = (
            TBW_FEMALE_INTERCEPT
            + TBW_FEMALE_HT2Z * ht2_z
            + TBW_FEMALE_WEIGHT * weight
        )
    return round(max(tbw, 0), 2)


def calc_ecw(
    weight: float,
    height_cm: float,
    age: float,
    impedance_low: float,
    gender: Gender,
) -> float:
    """Extracellular Water from 50kHz impedance (Kyle et al. 2004).

    Male:   ECW = -1.519 + 0.229 * (Ht^2 / Z_low) + 0.074 * Weight + 0.021 * Age
    Female: ECW = -0.073 + 0.174 * (Ht^2 / Z_low) + 0.039 * Weight + 0.023 * Age
    """
    ht2_z = (height_cm**2) / impedance_low
    if gender == Gender.MALE:
        ecw = (
            ECW_MALE_INTERCEPT
            + ECW_MALE_HT2Z * ht2_z
            + ECW_MALE_WEIGHT * weight
            + ECW_MALE_AGE * age
        )
    else:
        ecw = (
            ECW_FEMALE_INTERCEPT
            + ECW_FEMALE_HT2Z * ht2_z
            + ECW_FEMALE_WEIGHT * weight
            + ECW_FEMALE_AGE * age
        )
    return round(max(ecw, 0), 2)


def calc_icw(tbw: float, ecw: float) -> float:
    """Intracellular Water = TBW - ECW."""
    return round(max(tbw - ecw, 0), 2)


def calc_ffm(tbw: float) -> float:
    """Fat-Free Mass from TBW using hydration constant (Wang et al. 1999).

    FFM = TBW / 0.73
    """
    return round(tbw / FFM_HYDRATION, 2)


def calc_body_fat(weight: float, ffm: float) -> float:
    """Body fat percentage = (Weight - FFM) / Weight * 100."""
    if weight <= 0:
        return 0.0
    bf = (weight - ffm) / weight * 100
    return round(max(min(bf, 75.0), 0.0), 1)


def calc_lean_body_mass(weight: float, body_fat_pct: float) -> float:
    """Lean Body Mass = Weight * (1 - body_fat/100)."""
    return round(weight * (1 - body_fat_pct / 100), 2)


def calc_water_percentage(tbw: float, weight: float) -> float:
    """Water percentage = TBW / Weight * 100."""
    if weight <= 0:
        return 0.0
    return round(tbw / weight * 100, 1)


def calc_ecw_tbw_ratio(ecw: float, tbw: float) -> float:
    """ECW/TBW ratio. Normal range: 0.36-0.40."""
    if tbw <= 0:
        return 0.0
    return round(ecw / tbw, 3)


def calc_ecw_tbw_status(ratio: float) -> ECWTBWStatus:
    """Classify ECW/TBW ratio."""
    if ratio < ECW_TBW_RATIO_LOW:
        return ECWTBWStatus.LOW
    if ratio > ECW_TBW_RATIO_HIGH:
        return ECWTBWStatus.HIGH
    return ECWTBWStatus.NORMAL


def calc_bone_mass(
    weight: float, body_fat_pct: float, gender: Gender
) -> float:
    """Bone mass estimation from lean body mass (empirical).

    Bone mass ≈ 5.2% of lean body mass, with gender-specific base offset.
    Based on DXA validation studies showing bone mineral content is ~4-5% of FFM.
    """
    lbm = weight * (1 - body_fat_pct / 100)
    if gender == Gender.MALE:
        base = BONE_MALE_BASE
    else:
        base = BONE_FEMALE_BASE

    bone = lbm * 0.05158 - base
    # Small adjustment at threshold (from Xiaomi empirical tuning)
    if bone > 2.2:
        bone += 0.1
    else:
        bone -= 0.1
    bone = max(min(bone, 5.0), 0.5)
    return round(bone, 2)


def calc_visceral_fat(
    weight: float, height_cm: float, age: float, gender: Gender
) -> float:
    """Visceral fat rating (1-59 scale, empirical from Xiaomi reverse-engineering).

    Uses piecewise model based on height-to-weight ratio, age, and gender.
    """
    if gender == Gender.MALE:
        if height_cm < weight * 1.6 + 63.0:
            vf = (
                age * 0.15
                + (
                    weight * 305.0
                    / (height_cm * 0.0826 * height_cm - height_cm * 0.4 + 48.0)
                    - 2.9
                )
            )
        else:
            vf = (
                age * 0.15
                + (
                    weight * (height_cm * -0.0015 + 0.765)
                    - height_cm * 0.143
                )
                - 5.0
            )
    else:
        if weight <= height_cm * 0.5 - 13.0:
            vf = (
                age * 0.07
                + (
                    weight * (height_cm * -0.0024 + 0.691)
                    - height_cm * 0.027
                )
                - 10.5
            )
        else:
            vf = (
                age * 0.07
                + (
                    weight * 500.0
                    / (
                        height_cm * 1.45
                        + height_cm * 0.1158 * height_cm
                        - 120.0
                    )
                    - 6.0
                )
            )

    return round(max(min(vf, 59.0), 1.0), 1)


def calc_muscle_mass(weight: float, body_fat_pct: float, bone_mass: float) -> float:
    """Muscle mass = Weight - (body fat mass) - bone mass.

    Muscle mass ≈ lean body mass - bone mass.
    """
    fat_mass = weight * body_fat_pct / 100
    muscle = weight - fat_mass - bone_mass
    return round(max(muscle, 0), 2)


def calc_metabolic_age(
    bmr: float, weight: float, height_cm: float, gender: Gender
) -> int:
    """Metabolic age estimated by inverting the BMR equation.

    Solves Mifflin-St Jeor for age given the actual BMR.
    If actual BMR is lower than expected for age, metabolic age > chronological age.
    """
    offset = BMR_MALE_OFFSET if gender == Gender.MALE else BMR_FEMALE_OFFSET
    # BMR = 10*w + 6.25*h - 5*age + offset
    # age = (10*w + 6.25*h + offset - BMR) / 5
    metabolic_age = (BMR_WEIGHT * weight + BMR_HEIGHT * height_cm + offset - bmr) / BMR_AGE
    return round(max(min(metabolic_age, 120), 15))


def calc_protein(
    water_pct: float, body_fat_pct: float, bone_mass: float, weight: float
) -> float:
    """Protein percentage estimation.

    Protein ≈ (100 - water% - body_fat% - bone_mass/weight*100)
    Clamped to reasonable range.
    """
    if weight <= 0:
        return 0.0
    bone_pct = bone_mass / weight * 100
    protein = 100 - water_pct - body_fat_pct - bone_pct
    return round(max(min(protein, 30.0), 3.0), 1)


def calculate_all(
    profile: UserProfile,
    weight: float,
    impedance_high: float,
    impedance_low: float,
    heart_rate: float | None = None,
) -> dict[str, float | int | str | None]:
    """Calculate all body composition metrics from dual-frequency BIA.

    Args:
        profile: User profile (age, gender, height).
        weight: Body weight in kg.
        impedance_high: 250kHz impedance (ohms).
        impedance_low: 50kHz impedance (ohms).
        heart_rate: Optional heart rate in bpm.

    Returns:
        Dictionary of metric name -> value for all metrics.
    """
    from .score import calc_body_score

    age = profile.age
    height_cm = float(profile.height)
    height_m = profile.height_m
    gender = profile.gender

    bmi = calc_bmi(weight, height_m)
    ideal_weight = calc_ideal_weight(height_m, gender)
    bmr = calc_bmr(weight, height_cm, age, gender)
    tbw = calc_tbw(weight, height_cm, impedance_high, gender)
    ecw = calc_ecw(weight, height_cm, age, impedance_low, gender)
    icw = calc_icw(tbw, ecw)
    ffm = calc_ffm(tbw)
    body_fat = calc_body_fat(weight, ffm)
    lbm = calc_lean_body_mass(weight, body_fat)
    water_pct = calc_water_percentage(tbw, weight)
    bone_mass = calc_bone_mass(weight, body_fat, gender)
    visceral_fat = calc_visceral_fat(weight, height_cm, age, gender)
    muscle_mass = calc_muscle_mass(weight, body_fat, bone_mass)
    metabolic_age = calc_metabolic_age(bmr, weight, height_cm, gender)
    protein = calc_protein(water_pct, body_fat, bone_mass, weight)
    ecw_tbw_ratio = calc_ecw_tbw_ratio(ecw, tbw)
    ecw_tbw_status = calc_ecw_tbw_status(ecw_tbw_ratio)

    body_score = calc_body_score(
        bmi=bmi,
        body_fat=body_fat,
        muscle_mass=muscle_mass,
        water_pct=water_pct,
        visceral_fat=visceral_fat,
        bone_mass=bone_mass,
        bmr=bmr,
        weight=weight,
        age=age,
        gender=gender,
    )

    return {
        "weight": weight,
        "bmi": bmi,
        "basal_metabolism": bmr,
        "visceral_fat": visceral_fat,
        "ideal_weight": ideal_weight,
        "total_body_water": tbw,
        "extracellular_water": ecw,
        "intracellular_water": icw,
        "fat_free_mass": ffm,
        "body_fat": body_fat,
        "lean_body_mass": lbm,
        "water_percentage": water_pct,
        "bone_mass": bone_mass,
        "muscle_mass": muscle_mass,
        "metabolic_age": metabolic_age,
        "protein": protein,
        "body_score": body_score,
        "ecw_tbw_ratio": ecw_tbw_ratio,
        "ecw_tbw_status": ecw_tbw_status.value,
        "heart_rate": heart_rate,
    }
