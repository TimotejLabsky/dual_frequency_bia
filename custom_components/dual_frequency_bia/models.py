"""Data models for the Dual Frequency BIA integration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Gender(StrEnum):
    """Biological sex for BIA formula selection."""

    MALE = "male"
    FEMALE = "female"


class Metric(StrEnum):
    """Body composition metrics produced by this integration."""

    WEIGHT = "weight"
    BMI = "bmi"
    BASAL_METABOLISM = "basal_metabolism"
    VISCERAL_FAT = "visceral_fat"
    IDEAL_WEIGHT = "ideal_weight"
    TOTAL_BODY_WATER = "total_body_water"
    EXTRACELLULAR_WATER = "extracellular_water"
    INTRACELLULAR_WATER = "intracellular_water"
    FAT_FREE_MASS = "fat_free_mass"
    BODY_FAT = "body_fat"
    LEAN_BODY_MASS = "lean_body_mass"
    WATER_PERCENTAGE = "water_percentage"
    BONE_MASS = "bone_mass"
    MUSCLE_MASS = "muscle_mass"
    METABOLIC_AGE = "metabolic_age"
    PROTEIN = "protein"
    BODY_SCORE = "body_score"
    ECW_TBW_RATIO = "ecw_tbw_ratio"
    ECW_TBW_STATUS = "ecw_tbw_status"
    HEART_RATE = "heart_rate"


class ECWTBWStatus(StrEnum):
    """ECW/TBW ratio status categories."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


@dataclass(frozen=True)
class UserProfile:
    """User profile for body composition calculations."""

    name: str
    birthday: date
    gender: Gender
    height: int  # cm
    profile_id: int | None  # 1-16, or None for single-person mode

    @property
    def age(self) -> float:
        """Calculate current age in years (fractional)."""
        today = date.today()
        delta = today - self.birthday
        return delta.days / 365.25

    @property
    def height_m(self) -> float:
        """Height in meters."""
        return self.height / 100.0
