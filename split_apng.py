import pathlib
from PIL import Image

def add_marker_pixel(img: Image.Image) -> Image.Image:
    img = img.copy()
    img.putpixel((0, 0), (255, 255, 255, 155))
    return img

def update_timeing_in_apng(input_file: pathlib.Path,
                           output_file: pathlib.Path):

    im = Image.open(input_file)
    animation_files = []
    frames = []
    durations = []

    try:
        i = 0
        while True:  # arbitrary large number to prevent infinite loop
            im.seek(i)
            frame = im.copy().convert("RGBA")

            duration_ms = im.info.get("duration", 66)

            frames.append(frame)
            durations.append(66)
            if duration_ms > 66:
                if len(frames) > 1:
                    animation_files.append([frames, durations])
                    frames = []
                    durations = []

            i += 1

    except EOFError:
        pass
    for af_index, af in enumerate(animation_files):
        file_path = output_file.parent.joinpath(f"{output_file.stem}_part_{af_index}.png")
        af[0][0].save(
            file_path,
            save_all=True,
            append_images=af[0][1:],
            duration=af[1],  # real durations in ms
            loop=0,
            format="PNG",
        )



def main():
    input_folder = pathlib.Path("data", "apng_animation", "input")
    output_folder = pathlib.Path("data", "apng_animation", "output")
    output_folder.mkdir(parents=True, exist_ok=True)
    for input_file in input_folder.glob("*.png"):
        new_file_name = input_file.stem + "_fixed.png"
        output_file = output_folder.joinpath(new_file_name)
        update_timeing_in_apng(
            input_file=input_file,
            output_file=output_file
        )

if __name__ == "__main__":
    main()
