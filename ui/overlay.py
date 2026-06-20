import cv2

from config import FONT_SCALE, FONT_SCALE_SECONDARY, THICKNESS, HUD_ALPHA, HUD_PADDING

_FONT   = cv2.FONT_HERSHEY_SIMPLEX
_GREEN  = (80, 220, 80)
_WHITE  = (220, 220, 220)
_YELLOW = (255, 215, 0)
_ORANGE = (255, 190, 50)


def draw_text(frame, text, x, y, color=(0, 255, 0), scale=0.7, thickness=2):
    cv2.putText(frame, text, (x, y), _FONT, scale, (0, 0, 0), thickness + 2, cv2.LINE_AA)
    cv2.putText(frame, text, (x, y), _FONT, scale, color, thickness, cv2.LINE_AA)


def _hud_background(frame, x1, y1, x2, y2):
    overlay = frame.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), (0, 0, 0), -1)
    cv2.addWeighted(overlay, HUD_ALPHA, frame, 1 - HUD_ALPHA, 0, frame)


def draw_analysis(frame, result, fps: float = 0.0):
    PAD   = HUD_PADDING
    HUD_X = 8
    HUD_Y = 8
    S_PRI = FONT_SCALE            # 1.2 — phase, reps, score
    S_SEC = FONT_SCALE_SECONDARY  # 0.85 — angles, feedback, bias
    THK   = THICKNESS             # 2
    # baseline-to-baseline gaps scale with font size
    G_PRI = int(S_PRI * 34) + 8
    G_SEC = int(S_SEC * 28) + 8

    # Build ordered list of (text, color, scale, gap_after_px)
    lines = []
    lines.append((f"Phase: {result.phase}",     _GREEN, S_PRI, G_PRI))
    lines.append((f"Reps:  {result.rep_count}", _GREEN, S_PRI, G_PRI + 6))
    lines.append((f"Knee: {result.knee_angle}   Hip: {result.hip_angle}",      _WHITE, S_SEC, G_SEC))
    lines.append((f"Torso: {result.torso_angle}   Shin: {result.shin_angle}",  _WHITE, S_SEC, G_SEC))
    lines.append((f"Bias: {result.live_movement_bias}",                         _WHITE, S_SEC, G_SEC + 6))

    if result.distance_status is not None:
        lines.append((
            f"Distance: {result.distance_status.message}",
            result.distance_status.color, S_SEC, G_SEC + 6,
        ))

    if result.live_feedback:
        lines.append(("Live cues:", _GREEN, S_SEC, G_SEC))
        for msg in result.live_feedback:
            lines.append((f"  {msg}", _WHITE, S_SEC, G_SEC))

    lines.append(("Last rep:", _YELLOW, S_SEC, G_SEC))
    if result.last_rep_feedback is not None:
        rep = result.last_rep_feedback
        lines.append((f"#{rep.rep_index}  Score: {rep.score}/100", _YELLOW, S_PRI, G_PRI))
        lines.append((f"Bias: {rep.movement_bias}",                 _YELLOW, S_SEC, G_SEC))
        lines.append((
            f"Knee: {rep.min_knee_angle}  Torso: {rep.max_torso_angle}  Shin: {rep.max_shin_angle}",
            _YELLOW, S_SEC, G_SEC + 4,
        ))
        for msg in rep.feedback:
            lines.append((f"  {msg}", _ORANGE, S_SEC, G_SEC))
    else:
        lines.append(("No completed rep yet.", _YELLOW, S_SEC, G_SEC))

    # Measure all lines to size the background rect
    cap_h_first = int(S_PRI * 28)  # approx cap-height of the first (primary) line
    max_tw = 0
    total_h = PAD + cap_h_first
    for text, _, scale, gap in lines:
        (tw, _), _ = cv2.getTextSize(text, _FONT, scale, THK)
        max_tw = max(max_tw, tw)
        total_h += gap
    total_h += PAD + 8  # bottom padding + descender room

    _hud_background(frame, HUD_X, HUD_Y, HUD_X + PAD + max_tw + PAD, HUD_Y + total_h)

    # Render text over the background
    x = HUD_X + PAD
    y = HUD_Y + PAD + cap_h_first  # first baseline sits cap_h below the top padding
    for text, color, scale, gap in lines:
        draw_text(frame, text, x, y, color=color, scale=scale, thickness=THK)
        y += gap

    # FPS counter — top-right, outline provides enough contrast without a background
    fps_text = f"FPS: {fps:.1f}"
    w = frame.shape[1]
    (tw, _), _ = cv2.getTextSize(fps_text, _FONT, S_SEC, THK)
    draw_text(frame, fps_text, w - tw - 12, 30, color=_GREEN, scale=S_SEC, thickness=THK)
