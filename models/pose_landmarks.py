from dataclasses import dataclass
from typing import Dict, Optional, Tuple, List

Point2D = Tuple[float, float]


@dataclass
class LandmarkPoint:
    x: float
    y: float
    visibility: float = 1.0

    @property
    def xy(self) -> Point2D:
        return (self.x, self.y)


PoseLandmarkDict = Dict[str, Optional[LandmarkPoint]]


@dataclass
class DistanceStatus:
    message: str
    color: Tuple[int, int, int]


@dataclass
class RepFeedback:
    rep_index: int
    score: int
    movement_bias: str
    min_knee_angle: float
    max_torso_angle: float
    max_shin_angle: float
    depth_ok: bool
    feedback: List[str]