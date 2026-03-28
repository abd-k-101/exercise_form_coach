import cv2


def draw_text(frame, text, x, y, color=(0, 255, 0), scale=0.7, thickness=2):
    cv2.putText(
        frame,
        text,
        (x, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )


def draw_analysis(frame, result):
    y = 30
    gap = 28

    draw_text(frame, f"Phase: {result.phase}", 20, y)
    y += gap
    draw_text(frame, f"Reps: {result.rep_count}", 20, y)
    y += gap
    draw_text(frame, f"Knee angle: {result.knee_angle}", 20, y)
    y += gap
    draw_text(frame, f"Hip angle: {result.hip_angle}", 20, y)
    y += gap
    draw_text(frame, f"Torso angle: {result.torso_angle}", 20, y)
    y += gap
    draw_text(frame, f"Shin angle: {result.shin_angle}", 20, y)
    y += gap
    draw_text(frame, f"Live bias: {result.live_movement_bias}", 20, y)
    y += gap

    if result.distance_status is not None:
        draw_text(
            frame,
            f"Camera distance: {result.distance_status.message}",
            20,
            y,
            color=result.distance_status.color,
            scale=0.8,
            thickness=2,
        )
        y += gap + 8

    draw_text(frame, "Live cue:", 20, y)
    y += gap
    for msg in result.live_feedback:
        draw_text(frame, f"- {msg}", 20, y)
        y += gap

    y += 10
    draw_text(frame, "Last completed rep:", 20, y, color=(255, 255, 0))
    y += gap

    if result.last_rep_feedback is not None:
        rep = result.last_rep_feedback
        draw_text(frame, f"Rep #{rep.rep_index}", 20, y, color=(255, 255, 0))
        y += gap
        draw_text(frame, f"Score: {rep.score}/100", 20, y, color=(255, 255, 0))
        y += gap
        draw_text(frame, f"Bias: {rep.movement_bias}", 20, y, color=(255, 255, 0))
        y += gap
        draw_text(frame, f"Min knee: {rep.min_knee_angle}", 20, y, color=(255, 255, 0))
        y += gap
        draw_text(frame, f"Max torso: {rep.max_torso_angle}", 20, y, color=(255, 255, 0))
        y += gap
        draw_text(frame, f"Max shin: {rep.max_shin_angle}", 20, y, color=(255, 255, 0))
        y += gap

        for msg in rep.feedback:
            draw_text(frame, f"- {msg}", 20, y, color=(255, 255, 0))
            y += gap
    else:
        draw_text(frame, "No completed rep yet.", 20, y, color=(255, 255, 0))