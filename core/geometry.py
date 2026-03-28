import math


def calculate_angle(a, b, c):
    """
    Returns angle ABC in degrees.
    a, b, c are (x, y)
    """
    ba = (a[0] - b[0], a[1] - b[1])
    bc = (c[0] - b[0], c[1] - b[1])

    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2)
    mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cos_angle = dot / (mag_ba * mag_bc)
    cos_angle = max(-1.0, min(1.0, cos_angle))
    angle = math.degrees(math.acos(cos_angle))
    return angle


def line_angle_from_vertical(p1, p2):
    """
    Angle of line p1->p2 relative to vertical axis in degrees.
    0 = perfectly vertical
    """
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    angle = math.degrees(math.atan2(abs(dx), abs(dy) + 1e-6))
    return angle


def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)