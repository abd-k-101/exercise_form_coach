import pytest
from core.geometry import calculate_angle, line_angle_from_vertical


def test_calculate_angle_90_degrees():
    # Right angle: vectors pointing along x and y axes from origin
    angle = calculate_angle((0, 1), (0, 0), (1, 0))
    assert abs(angle - 90.0) < 1e-4


def test_calculate_angle_180_degrees():
    # Straight line: a, b, c collinear
    angle = calculate_angle((0, 0), (1, 0), (2, 0))
    assert abs(angle - 180.0) < 1e-4


def test_line_angle_from_vertical_45_degrees():
    # Equal dx and dy → 45° lean from vertical
    angle = line_angle_from_vertical((0, 0), (1, 1))
    assert abs(angle - 45.0) < 0.1
