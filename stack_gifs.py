from PIL import Image


def load_gif_frames(path):
    """Load all frames from a GIF."""
    img = Image.open(path)
    frames = []

    try:
        while True:
            frames.append(img.convert("RGBA").copy())
            img.seek(len(frames))
    except EOFError:
        pass

    return frames


def stack_gifs_vertically(gif_paths, output_path, duration=100):
    # Load frames for all GIFs
    all_frames = [load_gif_frames(p) for p in gif_paths]

    max_len = max(len(frames) for frames in all_frames)

    # Extend shorter GIFs by repeating last frame
    for frames in all_frames:
        if len(frames) < max_len:
            frames.extend([frames[-1]] * (max_len - len(frames)))

    output_frames = []

    for i in range(max_len):
        frames_at_t = [frames[i] for frames in all_frames]

        width = max(f.width for f in frames_at_t)
        height = sum(f.height for f in frames_at_t)

        canvas = Image.new("RGBA", (width, height))

        y = 0
        for f in frames_at_t:
            canvas.paste(f, (0, y))
            y += f.height

        output_frames.append(canvas)

    output_frames[0].save(
        output_path,
        save_all=True,
        append_images=output_frames[1:],
        duration=duration,
        loop=0,
        disposal=2
    )


# Example usage
gif_paths = ["/Users/jae35/Desktop/JULES_test_data/JASMIN_output_u-dk105_3_n7/plots/output/fch4_wetl/map_animation.gif", 
             "/Users/jae35/Desktop/JULES_test_data/JASMIN_output_u-dk105_3_n6/plots/output/fch4_wetl/map_animation.gif"]
stack_gifs_vertically(gif_paths, "/Users/jae35/Desktop/JULES_test_data/stacked_map_animations_resp.gif")