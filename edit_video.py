import pathlib
import shutil
import numpy as np
from PIL import Image
from moviepy import VideoFileClip
import cv2

current_path = pathlib.Path(__file__).parent

def _to_uint8(frame):
    arr = np.asarray(frame)
    if arr.dtype == np.uint8:
        return arr
    if np.issubdtype(arr.dtype, np.floating):
        # MoviePy sometimes returns floats in 0..1 or 0..255
        if arr.max() <= 1.1:
            arr = (arr * 255.0).clip(0, 255)
        else:
            arr = arr.clip(0, 255)
    return arr.astype(np.uint8)

def apply_mask(frame, lower=(37, 40, 40), upper=(85, 255, 255)):
    """
    Remove green background using HSV thresholding.
    Returns an RGBA image where alpha is a binary-ish mask (0 or 255).
    """
    frame_u8 = _to_uint8(frame)
    hsv = cv2.cvtColor(frame_u8, cv2.COLOR_RGB2HSV)

    # Mask for green (green -> 255)
    mask_green = cv2.inRange(hsv, np.array(lower), np.array(upper))

    # Foreground mask: non-green -> 255
    fg_mask = cv2.bitwise_not(mask_green)

    # Optional: small morphological opening to clean tiny spots
    kernel3 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel3, iterations=1)

    # Return RGBA with alpha = fg_mask (0/255)
    rgba = np.dstack((frame_u8, fg_mask))
    return rgba

def expand_transparency(rgba, shrink_pixels=0, feather=5, alpha_thresh=1):
    """
    Expand the transparent area by `shrink_pixels`:
      - erode the binary foreground mask `shrink_pixels` times (3x3 ellipse kernel)
      - blur (feather) the eroded mask to make smooth edges
      - premultiply RGB by the resulting alpha to avoid green fringing
    Parameters:
      shrink_pixels: int, number of pixels to remove from object edge (>=0)
      feather: int, radius for gaussian blur (>=0). Final kernel = 2*feather+1 (odd).
      alpha_thresh: pixels with alpha <= this are considered fully transparent (used only if needed)
    """
    # Separate
    rgb = rgba[:, :, :3].astype(np.uint8)
    alpha = rgba[:, :, 3].astype(np.uint8)

    # Ensure binary mask (0 or 255) from alpha
    bin_mask = (alpha > alpha_thresh).astype(np.uint8) * 255

    if shrink_pixels > 0:
        # Use a small ellipse kernel and perform `shrink_pixels` iterations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        eroded = cv2.erode(bin_mask, kernel, iterations=shrink_pixels)
    else:
        eroded = bin_mask

    # Feather / smooth the alpha (make sure kernel is odd and >=1)
    if feather and feather > 0:
        k = max(1, int(feather) * 2 + 1)
        eroded_blurred = cv2.GaussianBlur(eroded, (k, k), 0)
    else:
        eroded_blurred = eroded

    # Make sure alpha is 0..255 uint8
    new_alpha = np.clip(eroded_blurred, 0, 255).astype(np.uint8)

    # Premultiply RGB by alpha to avoid leftover green fringes at semi-transparent edges
    # alpha_scale shape (H, W, 1)
    alpha_scale = (new_alpha.astype(np.float32) / 255.0)[:, :, None]
    premult_rgb = (rgb.astype(np.float32) * alpha_scale).round().astype(np.uint8)

    out_rgba = np.dstack((premult_rgb, new_alpha))
    return out_rgba

def save_frames(output_folder, clip, times, shrink_pixels=0, feather=5) -> list:
    frames = []
    for i, t in enumerate(times):
        frame = clip.get_frame(t)
        rgba = apply_mask(frame)

        # expand transparent area (shrink the object)
        if shrink_pixels > 0 or (feather and feather > 0):
            rgba = expand_transparency(rgba, shrink_pixels=shrink_pixels, feather=feather)

        # save PNG frame
        png_path = output_folder.joinpath(f"frame_{i:05d}.png")
        image_item = Image.fromarray(rgba)
        image_item.save(png_path)

        frames.append(image_item)

    return frames

def main():
    fps_out = 15
    data_path = current_path.joinpath("data", "secrete", "secrete")
    video_path = data_path.joinpath("input_01.mp4")
    output_folder = video_path.parent.joinpath(video_path.stem)
    # ADJUST THESE:
    shrink_pixels = 1   # how many pixels to remove around the object
    feather = 1         # softness of the new edge

    # delete old folder if it exists
    if output_folder.exists():
        shutil.rmtree(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    clip = VideoFileClip(str(video_path))
    duration = clip.duration
    times = np.arange(0, duration, 1.0 / fps_out)


    frames = save_frames(output_folder, clip, times, shrink_pixels=shrink_pixels, feather=feather)

    frames[0].save(
        output_folder.joinpath("output.png"),
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / fps_out),
        loop=0,
        format="PNG"  # APNG
    )
    print("APNG saved to:", output_folder.joinpath("output.png"))

if __name__ == "__main__":
    main()
