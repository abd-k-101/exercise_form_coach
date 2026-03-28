from models.pose_landmarks import LandmarkPoint, PoseLandmarkDict


class LandmarkSmoother:
    def __init__(self, alpha=0.35):
        self.alpha = alpha
        self.prev: PoseLandmarkDict = {}

    def smooth(self, landmarks: PoseLandmarkDict) -> PoseLandmarkDict:
        smoothed: PoseLandmarkDict = {}

        for name, point in landmarks.items():
            if point is None:
                smoothed[name] = None
                continue

            if name not in self.prev or self.prev[name] is None:
                smoothed[name] = LandmarkPoint(
                    x=point.x,
                    y=point.y,
                    visibility=point.visibility,
                )
            else:
                prev = self.prev[name]
                sx = self.alpha * point.x + (1 - self.alpha) * prev.x
                sy = self.alpha * point.y + (1 - self.alpha) * prev.y
                sv = self.alpha * point.visibility + (1 - self.alpha) * prev.visibility

                smoothed[name] = LandmarkPoint(x=sx, y=sy, visibility=sv)

        self.prev = smoothed
        return smoothed