import cv2
import numpy as np
import math
import imageio.v2 as imageio
import os

mode = 'process'

if mode == 'process':

    input_video = "/Users/jae35/Desktop/IMAG0796.MOV"
    output_video = "/Users/jae35/Desktop/IMAG0796_2.MOV"
    output_grid = "/Users/jae35/Desktop/retained_grid.jpg"
    output_gif = "/Users/jae35/Desktop/retained_squares.gif"
    output_traj = "/Users/jae35/Desktop/trajectory_overlay.jpg"

    cap = cv2.VideoCapture(input_video)

    if not cap.isOpened():
        raise Exception("Could not open video.")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    out = cv2.VideoWriter(
        output_video,
        cv2.VideoWriter_fourcc(*'mp4v'),
        fps,
        (width, height)
    )

    bg = cv2.createBackgroundSubtractorMOG2(
        history=2000,
        varThreshold=10,
        detectShadows=False
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))

    min_area = 1200

    BOX_W = 500
    BOX_H = 500

    GRID_SCALE = 0.25
    saved_frames = []
    gif_frames = []

    FRAME_STRIDE = 1
    MAX_SAMPLES = 80

    frame_idx = 0

    last_center = None
    SMOOTHING = 0.50
    last_box = None

    centers = []
    bg_accumulator = None
    bg_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_f = frame.astype(np.float32)

        if bg_accumulator is None:
            bg_accumulator = np.zeros_like(frame_f)

        bg_accumulator += frame_f
        bg_count += 1

        blur = cv2.GaussianBlur(frame, (11, 11), 0)
        fg = bg.apply(blur)

        _, fg = cv2.threshold(fg, 200, 255, cv2.THRESH_BINARY)

        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8), 1)
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8), 2)

        contours, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        base = np.zeros_like(fg)

        for c in contours:
            if cv2.contourArea(c) > min_area:
                cv2.drawContours(base, [c], -1, 255, -1)

        expanded = cv2.dilate(base, kernel, iterations=1)
        coords = cv2.findNonZero(expanded)

        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)

            cx = x + w // 2
            cy = y + h // 2

            if last_center is None:
                last_center = (cx, cy)
            else:
                last_center = (
                    int(SMOOTHING * last_center[0] + (1 - SMOOTHING) * cx),
                    int(SMOOTHING * last_center[1] + (1 - SMOOTHING) * cy)
                )

            cx, cy = last_center
            centers.append((cx, cy))

            half_w = BOX_W // 2
            half_h = BOX_H // 2

            x1 = max(cx - half_w, 0)
            y1 = max(cy - half_h, 0)
            x2 = min(cx + half_w, frame.shape[1])
            y2 = min(cy + half_h, frame.shape[0])

            last_box = (x1, y1, x2, y2)

        else:
            if last_center is not None:
                cx, cy = last_center
                centers.append((cx, cy))

                x1 = max(cx - BOX_W // 2, 0)
                y1 = max(cy - BOX_H // 2, 0)
                x2 = min(cx + BOX_W // 2, frame.shape[1])
                y2 = min(cy + BOX_H // 2, frame.shape[0])

                last_box = (x1, y1, x2, y2)

        if last_box is not None:
            x1, y1, x2, y2 = last_box

            mask = np.zeros_like(frame[:, :, 0])
            mask[y1:y2, x1:x2] = 255

            output = cv2.bitwise_and(frame, frame, mask=mask)
        else:
            output = frame.copy()

        out.write(output)

        if last_box is not None:
            x1, y1, x2, y2 = last_box
            crop = output[y1:y2, x1:x2]

            square = np.zeros((BOX_H, BOX_W, 3), dtype=np.uint8)
            square[:crop.shape[0], :crop.shape[1]] = crop

            gif_frames.append(cv2.cvtColor(square, cv2.COLOR_BGR2RGB))

        if frame_idx % FRAME_STRIDE == 0:
            resized = cv2.resize(output, (int(width * GRID_SCALE), int(height * GRID_SCALE)))
            saved_frames.append(resized)

            if len(saved_frames) > MAX_SAMPLES:
                saved_frames.pop(0)

        frame_idx += 1

    cap.release()
    out.release()

    print("Saved video:", output_video)

    # =========================
    # GIF SAVE
    # =========================
    if len(gif_frames) > 0:
        imageio.mimsave(output_gif, gif_frames, fps=fps, loop=0)
        print("Saved GIF:", output_gif)

        # 4 frames centered around middle
        frames_dir = "/Users/jae35/Desktop/frames"
        os.makedirs(frames_dir, exist_ok=True)

        n = len(gif_frames)
        mid = n // 2
        span = max(1, n // 10)

        start = max(0, mid - span)
        end = min(n - 1, mid + span)

        idxs = np.linspace(start, end, 4, dtype=int) if n >= 4 else np.arange(n)

        for i, idx in enumerate(idxs):
            frame = cv2.cvtColor(gif_frames[idx], cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"{frames_dir}/frame_{i+1:02d}.png", frame)

        print("Saved sampled frames:", frames_dir)

    # =========================
    # GRID SAVE
    # =========================
    if len(saved_frames) > 0:
        h, w = saved_frames[0].shape[:2]

        cols = math.ceil(math.sqrt(len(saved_frames)))
        rows = math.ceil(len(saved_frames) / cols)

        grid = np.zeros((rows * h, cols * w, 3), dtype=np.uint8)

        for i, img in enumerate(saved_frames):
            r = i // cols
            c = i % cols
            grid[r*h:(r+1)*h, c*w:(c+1)*w] = img

        cv2.imwrite(output_grid, grid)
        print("Saved grid:", output_grid)

    # =========================
    # TRAJECTORY
    # =========================
    if bg_count > 0:
        bg_image = (bg_accumulator / bg_count).astype(np.uint8)
    else:
        raise Exception("No frames processed.")

    traj_img = bg_image.copy()

    if len(centers) > 1:
        pts = np.array(centers, dtype=np.int32).reshape((-1, 1, 2))
        cv2.polylines(traj_img, [pts], False, (0, 0, 255), 3)

        for p in centers:
            cv2.circle(traj_img, p, 4, (0, 255, 255), -1)

    cv2.imwrite(output_traj, traj_img)

    print("Saved trajectory image:", output_traj)


elif mode == 'identify':

    import subprocess

    url = "https://www.inaturalist.org/observations/upload"

    sx, sy = 100, 100
    sw, sh = 600, 600

    fx, fy = 700, 100
    fw, fh = 600, 600

    folder_path = "/Users/jae35/Desktop/email_plots"

    apple_script = f'''
    tell application "Safari"
        activate
        open location "{url}"
        delay 1
        set bounds of front window to {{{sx}, {sy}, {sx + sw}, {sy + sh}}}
    end tell

    tell application "Finder"
        activate

        set newWindow to make new Finder window
        set target of newWindow to (POSIX file "{folder_path}")

        delay 0.5

        set bounds of newWindow to {{{fx}, {fy}, {fx + fw}, {fy + fh}}}

        select every item of newWindow
    end tell
    '''

    subprocess.run(["osascript", "-e", apple_script])