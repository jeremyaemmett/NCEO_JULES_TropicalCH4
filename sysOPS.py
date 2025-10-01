from PIL import Image, ImageSequence
import pandas as pd
import os


def pngs_to_gif(folder, out='out.gif', duration=600, smooth=False, exclude_substr=None):

    def get_sorted_pngs(folder, exclude_substr):
        def sort_key(name):
            num = ''
            for c in name:
                if c.isdigit():
                    num += c
            return int(num) if num else -1  # sort purely by number

        files = [
            f for f in os.listdir(folder)
            if f.lower().endswith('.png') and (
                exclude_substr is None or 
                not any(sub in f for sub in exclude_substr)
            )
        ]
        return sorted(files, key=sort_key)

    files = get_sorted_pngs(folder, exclude_substr)
    print('sorted files: ', files)

    if not files:
        raise ValueError("No PNG files found in folder.")

    # Load and resize images
    base_img = Image.open(os.path.join(folder, files[0])).convert('RGB')
    base_size = base_img.size
    images = [base_img]

    for f in files[1:]:
        img = Image.open(os.path.join(folder, f)).convert('RGB').resize(base_size)
        images.append(img)

    # Prepare full list of frames (including blended if smooth=True)
    full_frames = []
    for i, img in enumerate(images):
        full_frames.append(img)
        if smooth:
            # Blend to next frame if not the last
            if i < len(images) - 1:
                next_img = images[i + 1]
                for alpha in (0.33, 0.66):
                    blended = Image.blend(img, next_img, alpha)
                    full_frames.append(blended)
            # ALSO, if this is the last image (December), blend back to first (January)
            elif i == len(images) - 1:
                first_img = images[0]
                for alpha in (0.33, 0.66):
                    blended = Image.blend(img, first_img, alpha)
                    full_frames.append(blended)

    # Create a global palette by merging all RGB frames into one long image
    palette_base = Image.new('RGB', (base_size[0], base_size[1] * len(full_frames)))
    for i, frame in enumerate(full_frames):
        palette_base.paste(frame, (0, i * base_size[1]))

    # Use this image to generate a global palette
    palette_image = palette_base.quantize(colors=256, method=Image.MEDIANCUT)

    # Apply global palette to all frames
    paletted_frames = [frame.quantize(palette=palette_image) for frame in full_frames]

    # Save to GIF
    print('saving to: ', out)
    paletted_frames[0].save(out, save_all=True, append_images=paletted_frames[1:], duration=duration, loop=0)


def discover_files(root_path, end_string):

    # Make a list of every t-series file across all of the input variables
    files = [os.path.join(r, f) for r, _, fs in os.walk(root_path) for f in fs if f.endswith(end_string)]

    return files
    
    
def group_file_names_by_end_directory(file_names):

    # Loop through every t-series file
    grouped_files = {}
    for f in file_names:

        # Recover the variable name from the file path
        parts = os.path.normpath(f).split(os.sep)
 
        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(f))
            
        # Group the t-series file paths by their variables: Dictionary with {variable1: [t-series list], variable2: [t-series list]}
        grouped_files.setdefault(key, []).append(f)

    return grouped_files
        

def group_file_contents_by_end_directory(file_names):

    # Loop through every t-series file
    grouped = {}
    for f in file_names:

        # Recover the variable name from the file path
        parts = os.path.normpath(f).split(os.sep)

        try:
            i = parts.index('output')
            after = parts[i+1:-1]
            key = after[0] if len(after) <= 1 else after[-2]
        except ValueError:
            key = os.path.basename(os.path.dirname(f))
            
        # Group the t-series file paths by their variables: Dictionary with {variable1: [t-series list], variable2: [t-series list]}
        grouped.setdefault(key, []).append(pd.read_csv(f, header=None)[0].tolist())

    return grouped


def get_unique_end_directories(file_paths):
    end_dirs = set()
    for path in file_paths:
        dir_path = os.path.dirname(os.path.abspath(path))  # Get full absolute dir path
        end_dirs.add(dir_path)
    return sorted(end_dirs)  # Optional: sorted for consistent order


def combine_gifs_vertically(gif1_path, gif2_path, output_path, gif2_scale=1.0):
    gif1 = Image.open(gif1_path)
    gif2 = Image.open(gif2_path)

    frames = []

    for frame1, frame2 in zip(ImageSequence.Iterator(gif1), ImageSequence.Iterator(gif2)):
        f1 = frame1.convert('RGBA')
        f2 = frame2.convert('RGBA')

        # Resize gif2 frame only
        if gif2_scale != 1.0:
            new_width = int(f2.width * gif2_scale)
            new_height = int(f2.height * gif2_scale)
            f2 = f2.resize((new_width, new_height), resample=Image.BOX)

        # Optionally pad f1 or f2 if widths differ
        combined_width = max(f1.width, f2.width)
        f1_padded = Image.new('RGBA', (combined_width, f1.height), (0, 0, 0, 0))
        f1_padded.paste(f1, ((combined_width - f1.width) // 2, 0))

        f2_padded = Image.new('RGBA', (combined_width, f2.height), (0, 0, 0, 0))
        f2_padded.paste(f2, ((combined_width - f2.width) // 2, 0))

        # Stack vertically
        new_height = f1_padded.height + f2_padded.height
        combined = Image.new('RGBA', (combined_width, new_height))
        combined.paste(f1_padded, (0, 0))
        combined.paste(f2_padded, (0, f1_padded.height))

        frames.append(combined)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=gif1.info.get('duration', 100),
        loop=0,
        disposal=2
    )


def combine_gifs_on_canvas(
    gif1_path,
    gif2_path,
    output_path,
    canvas_size,
    pos1,
    pos2
):
    """
    Combine two animated GIFs on a single canvas.

    Args:
        gif1_path (str): Path to the first GIF
        gif2_path (str): Path to the second GIF
        output_path (str): Path to save the combined GIF
        canvas_size (tuple): (width, height) of the canvas in pixels
        pos1 (tuple): (x, y) bottom-left position of first GIF
        pos2 (tuple): (x, y) bottom-left position of second GIF
    """
    gif1 = Image.open(gif1_path)
    gif2 = Image.open(gif2_path)

    # Use the minimum number of frames
    n_frames = min(gif1.n_frames, gif2.n_frames)
    duration = gif1.info.get('duration', 100)

    canvas_width, canvas_height = canvas_size

    frames = []

    # To handle GIFs with transparency and delta frames, we build full frames manually
    def extract_full_frames(gif):
        """Returns a list of full RGBA frames"""
        full_frames = []
        previous = Image.new("RGBA", gif.size)
        for frame in ImageSequence.Iterator(gif):
            frame_rgba = frame.convert("RGBA")
            composed = Image.alpha_composite(previous.copy(), frame_rgba)
            full_frames.append(composed)
            previous = composed
        return full_frames

    gif1_frames = extract_full_frames(gif1)
    gif2_frames = extract_full_frames(gif2)

    def to_top_left(pos, img_height):
        return (pos[0], canvas_height - pos[1] - img_height)

    for i in range(n_frames):
        canvas = Image.new("RGBA", (canvas_width, canvas_height), "white")

        # Get current frames
        frame1 = gif1_frames[i % len(gif1_frames)]
        frame2 = gif2_frames[i % len(gif2_frames)]

        canvas.paste(frame1, to_top_left(pos1, frame1.height), frame1)
        canvas.paste(frame2, to_top_left(pos2, frame2.height), frame2)

        # Convert to 'P' mode for GIF compatibility
        frames.append(canvas.convert("P", palette=Image.ADAPTIVE))

    # Save the output GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        optimize=False
    )

