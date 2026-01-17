import pathlib
from PIL import Image

def add_marker_pixel(img: Image.Image, marker_pixel_01=True) -> Image.Image:
    img = img.copy()
    #for index_nr in range(10):
    #    img.putpixel((100 + index_nr if marker_pixel_01 else 110 + index_nr, 5), (0, 0, 0, 255))
    img.putpixel((100 if marker_pixel_01 else 110, 0), (0, 0, 0, 125))
    return img

def make_empty_frame(size):
    """
    Create a fully transparent frame with a black marker pixel at (0, 0).
    """
    empty = Image.new("RGBA", size, (0, 0, 0, 0))
    empty.putpixel((0, 0), (0, 0, 0, 255))
    return empty

def update_timeing_in_apng(input_file: pathlib.Path,
                           output_file: pathlib.Path):

    im = Image.open(input_file)

    frames = []
    durations = []
    marker_pixel_first = False

    try:
        i = 0
        while i < 600:  # arbitrary large number to prevent infinite loop
            im.seek(i)
            frame = im.copy().convert("RGBA")

            duration_ms = im.info.get("duration", 66)

            frame = add_marker_pixel(frame, marker_pixel_first)
            marker_pixel_first = not marker_pixel_first

            frames.append(frame)
            durations.append(66)
            duration_ms -= 66

            # Split long durations into multiple 100ms frames
            while duration_ms > 0:
                frame = make_empty_frame(frame.size)
                frame = add_marker_pixel(frame, marker_pixel_first)
                marker_pixel_first = not marker_pixel_first

                # Make a real copy of the frame
                durations.append(66)
                frames.append(frame)
                duration_ms -= 66

            i += 1

    except EOFError:
        pass

    frames[0].save(
        output_file,
        save_all=True,
        append_images=frames[1:],
        duration=durations,  # real durations in ms
        loop=0,
        format="PNG",
    )



def main():
    input_folder = pathlib.Path("data", "apng", "input")
    output_folder = pathlib.Path("data", "apng", "output")
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
