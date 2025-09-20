import pathlib
import shutil
import numpy as np
from PIL import Image
from moviepy import VideoFileClip
import cv2
import random

current_path = pathlib.Path(__file__).parent

def combine_animation_files(clip_amount = 35,
                            input_folder= None,
                            output_file=None,
                            min_delay=1000,
                            max_delay=10000):
    animated_png_files = [video_file_path for video_file_path in input_folder.glob("*.png")]

    files_to_combine = []
    while len(files_to_combine) < clip_amount:
        random_list_index = random.Random().randint(0, len(animated_png_files) - 1)
        files_to_combine.append(animated_png_files[random_list_index])

    for file_path in animated_png_files:
        if file_path in files_to_combine:
            continue
        files_to_combine.insert(random.Random().randint(0, len(files_to_combine) - 1), file_path)

    # your code here
    # ---------------------------

    # Load all frames from all files and track durations
    all_frames = []
    all_durations = []

    for file_path in files_to_combine:
        im = Image.open(file_path)
        try:
            i = 0
            while True:
                im.seek(i)
                frame = im.convert("RGBA")
                all_frames.append(frame)

                # Get original frame duration if exists, otherwise default 100ms
                duration = im.info.get("duration", 100)
                all_durations.append(duration)

                i += 1
        except EOFError:
            pass  # reached end of this APNG

        # Add a random delay after this file
        delay_between_files = random.randint(min_delay, max_delay)
        if all_frames:
            # Add delay to last frame of this file
            all_durations[-1] += delay_between_files

    print(f"Total frames collected: {len(all_frames)}")

    # Save combined APNG
    if all_frames:
        all_frames[0].save(
            output_file,
            save_all=True,
            append_images=all_frames[1:],
            duration=all_durations,  # per-frame durations
            loop=0,
            format="PNG"
        )
        print(f"Combined APNG saved to {output_file}")


def main():
    clip_amount = 35
    input_folder = current_path.joinpath("data", "secrete", "secrete", "output_folder")
    output_folder = current_path.joinpath("data", "secrete", "secrete")
    #output_file = current_path.joinpath("data", "secrete", "secrete", "intro_animation.png")
    min_delay = 1000  # ms
    max_delay = 10000  # ms
    for i in range(1, 11):
        output_file = output_folder.joinpath(f"intro_animation_{str(i).zfill(3)}.png")
        print("Working on:", output_file)
        combine_animation_files(
            clip_amount=clip_amount,
            input_folder=input_folder,
            output_file=output_file,
            min_delay=min_delay,
            max_delay=max_delay
        )



if __name__ == "__main__":
    main()

