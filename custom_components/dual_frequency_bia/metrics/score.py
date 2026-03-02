"""Body composition score calculation (0-100).

Scores each metric against ideal ranges by age/gender,
then produces a weighted composite score.

Based on bodymiscale's scoring approach with adjustments for dual-frequency metrics.
"""

from __future__ import annotations

from ..models import Gender


def _score_bmi(bmi: float) -> float:
    """Score BMI (ideal: 18.5-24.9)."""
    if 18.5 <= bmi <= 24.9:
        return 100.0
    if bmi < 18.5:
        return max(100 - (18.5 - bmi) * 15, 0)
    # bmi > 24.9
    return max(100 - (bmi - 24.9) * 10, 0)


def _score_body_fat(body_fat: float, age: float, gender: Gender) -> float:
    """Score body fat percentage against age/gender ideal ranges."""
    if gender == Gender.MALE:
        if age < 30:
            ideal_low, ideal_high = 10.0, 20.0
        elif age < 50:
            ideal_low, ideal_high = 12.0, 22.0
        else:
            ideal_low, ideal_high = 14.0, 25.0
    else:
        if age < 30:
            ideal_low, ideal_high = 18.0, 28.0
        elif age < 50:
            ideal_low, ideal_high = 20.0, 30.0
        else:
            ideal_low, ideal_high = 22.0, 33.0

    if ideal_low <= body_fat <= ideal_high:
        return 100.0
    if body_fat < ideal_low:
        return max(100 - (ideal_low - body_fat) * 8, 0)
    return max(100 - (body_fat - ideal_high) * 6, 0)


def _score_muscle_mass(muscle_mass: float, weight: float, gender: Gender) -> float:
    """Score muscle mass as percentage of total weight."""
    if weight <= 0:
        return 50.0
    muscle_pct = muscle_mass / weight * 100
    if gender == Gender.MALE:
        ideal_low, ideal_high = 40.0, 50.0
    else:
        ideal_low, ideal_high = 30.0, 40.0

    if ideal_low <= muscle_pct <= ideal_high:
        return 100.0
    if muscle_pct < ideal_low:
        return max(100 - (ideal_low - muscle_pct) * 5, 0)
    return max(100 - (muscle_pct - ideal_high) * 5, 50)


def _score_water(water_pct: float, gender: Gender) -> float:
    """Score water percentage."""
    if gender == Gender.MALE:
        ideal_low, ideal_high = 55.0, 65.0
    else:
        ideal_low, ideal_high = 45.0, 60.0

    if ideal_low <= water_pct <= ideal_high:
        return 100.0
    if water_pct < ideal_low:
        return max(100 - (ideal_low - water_pct) * 5, 0)
    return max(100 - (water_pct - ideal_high) * 3, 50)


def _score_visceral_fat(visceral_fat: float) -> float:
    """Score visceral fat rating (ideal: 1-9)."""
    if visceral_fat <= 9:
        return 100.0
    if visceral_fat <= 14:
        return max(100 - (visceral_fat - 9) * 10, 0)
    return max(100 - (visceral_fat - 9) * 8, 0)


def _score_bone_mass(bone_mass: float, weight: float, gender: Gender) -> float:
    """Score bone mass against ideal for body weight."""
    if gender == Gender.MALE:
        if weight < 65:
            ideal = 2.65
        elif weight < 95:
            ideal = 3.29
        else:
            ideal = 3.69
    else:
        if weight < 50:
            ideal = 1.95
        elif weight < 75:
            ideal = 2.40
        else:
            ideal = 2.95

    deviation = abs(bone_mass - ideal)
    return max(100 - deviation * 30, 0)


def _score_bmr(bmr: float, weight: float, age: float, gender: Gender) -> float:
    """Score BMR against expected for age/weight/gender."""
    # Expected BMR from Mifflin-St Jeor with average height
    avg_height = 175 if gender == Gender.MALE else 162
    expected = 10 * weight + 6.25 * avg_height - 5 * age
    expected += 5 if gender == Gender.MALE else -161

    if expected <= 0:
        return 50.0
    ratio = bmr / expected
    if 0.95 <= ratio <= 1.05:
        return 100.0
    deviation = abs(ratio - 1.0)
    return max(100 - deviation * 200, 0)


def calc_body_score(
    bmi: float,
    body_fat: float,
    muscle_mass: float,
    water_pct: float,
    visceral_fat: float,
    bone_mass: float,
    bmr: float,
    weight: float,
    age: float,
    gender: Gender,
) -> int:
    """Calculate composite body score (0-100).

    Weights:
    - Body fat: 25%
    - Muscle mass: 20%
    - BMI: 15%
    - Water: 15%
    - Visceral fat: 10%
    - Bone mass: 10%
    - BMR: 5%
    """
    scores = {
        "bmi": (_score_bmi(bmi), 0.15),
        "body_fat": (_score_body_fat(body_fat, age, gender), 0.25),
        "muscle_mass": (_score_muscle_mass(muscle_mass, weight, gender), 0.20),
        "water": (_score_water(water_pct, gender), 0.15),
        "visceral_fat": (_score_visceral_fat(visceral_fat), 0.10),
        "bone_mass": (_score_bone_mass(bone_mass, weight, gender), 0.10),
        "bmr": (_score_bmr(bmr, weight, age, gender), 0.05),
    }

    total = sum(score * w for score, w in scores.values())
    return round(max(min(total, 100), 0))
