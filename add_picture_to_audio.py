import pathlib
import sys
import traceback

# Import moviepy lazily with a friendly error message if it's not installed.
# If import fails for any reason, print the traceback so we can diagnose the root cause.
try:
    # Some MoviePy installations expose symbols at package top-level instead of moviepy.editor
    from moviepy import ImageClip, AudioFileClip  # type: ignore
except Exception as e:
    print("Failed to import moviepy ImageClip/AudioFileClip:")
    traceback.print_exc()
    ImageClip = None  # type: ignore
    AudioFileClip = None  # type: ignore

project_root_path = pathlib.Path(__file__).parent.absolute().resolve()
temp_data_folder = project_root_path.joinpath("data", "temp")
temp_data_folder.mkdir(parents=True, exist_ok=True)

input_folder = project_root_path.joinpath("data", "audio_image_to_video")

def find_file_and_group_by_prefix(folder: pathlib.Path, audio_exts: list, image_exts: list):
    """Find files in folder that start with input_audio or input_image and group them together."""
    return_dict = {}
    if not folder.exists():
        return return_dict

    for file in folder.iterdir():
        if not file.is_file():
            continue
        file_ext = file.suffix[1:].lower()  # get extension without dot and lowercase
        file_stem = file.stem
        if file_stem not in return_dict:
            return_dict[file_stem] = {"audio": None, "image": None}
        if file_ext in audio_exts:
            return_dict[file_stem]["audio"] = file
        elif file_ext in image_exts:
            return_dict[file_stem]["image"] = file
    return return_dict


def set_clip_duration(clip, duration: float):
    """Set clip duration in a way that's compatible with multiple moviepy versions."""
    # 1) try constructor (some ImageClip accept duration kw)
    try:
        # If clip has an internal method to recreate with duration, use it
        return clip.with_duration(duration) if hasattr(clip, 'with_duration') else clip
    except Exception:
        pass

    # 2) try set_duration method on the clip instance
    if hasattr(clip, 'set_duration'):
        try:
            return clip.set_duration(duration)
        except Exception:
            pass

    # 3) try to set attribute directly
    try:
        clip.duration = duration
        return clip
    except Exception:
        pass

    # 4) as a last resort, try to recreate via constructor with duration kw (some builds accept it)
    try:
        return ImageClip(clip.img, duration=duration)  # type: ignore
    except Exception:
        pass

    # if nothing worked, raise
    raise RuntimeError('Could not set duration on ImageClip with this MoviePy version')


def main():
    if ImageClip is None or AudioFileClip is None:
        print("ERROR: moviepy is not installed. Install it with: pip install moviepy")
        sys.exit(1)

    # try common extensions
    audio_exts = ["mp3", "wav", "m4a", "aac", "ogg"]
    image_exts = ["png", "jpg", "jpeg", "bmp"]

    input_files = find_file_and_group_by_prefix(input_folder, audio_exts, image_exts)

    for input_file_stem, file_pair in input_files.items():
        if file_pair["audio"] is None or file_pair["image"] is None:
            continue
        input_audio_file = pathlib.Path(file_pair["audio"])
        input_image_file = pathlib.Path(file_pair["image"])
        output_video_file = input_folder.joinpath(f"{input_file_stem}.mp4")

        print(f"Using audio: {input_audio_file}")
        print(f"Using image: {input_image_file}")
        print(f"Using output: {output_video_file}")
        print("-" * 40)

        # Load audio using moviepy (this avoids pydub/audioop issues)
        audio = AudioFileClip(str(input_audio_file))
        duration = getattr(audio, 'duration', None)
        print(f"Loaded audio duration: {duration}")
        if duration is None or duration <= 0:
            print("ERROR: audio duration is invalid or zero. Skipping file.")
            audio.close()
            continue

        # Create a still-image video clip for the audio duration
        try:
            # try to construct with duration kw (works on some builds)
            clip = ImageClip(str(input_image_file), duration=duration)  # type: ignore
        except Exception:
            # fallback: construct without duration then set it
            clip = ImageClip(str(input_image_file))  # type: ignore
            try:
                clip = set_clip_duration(clip, duration)
            except Exception as e:
                print("Failed to set duration on ImageClip:")
                traceback.print_exc()
                print("Skipping this file due to incompatible MoviePy ImageClip implementation.")
                clip.close()
                audio.close()
                continue

        # Debug: print clip duration after setting
        clip_dur = getattr(clip, 'duration', None)
        print(f"ImageClip duration after setup: {clip_dur}")

        # attach audio (set_audio returns a new clip in many versions)
        if hasattr(clip, 'set_audio'):
            clip = clip.set_audio(audio)
        else:
            # older/newer versions should have set_audio; this is defensive
            try:
                clip.audio = audio
            except Exception:
                print("WARNING: could not attach audio to clip via set_audio or attribute assignment.")

        # Write the final video file. moviepy will call ffmpeg; ensure ffmpeg is installed on the system.
        print(f"Writing video to: {output_video_file}")
        try:
            # force audio=True and add '-shortest' so the output respects audio length and doesn't drop it
            clip.write_videofile(
                str(output_video_file),
                fps=24,
                codec="libx264",
                audio=True,
                audio_codec="aac",
                ffmpeg_params=["-shortest"],
            )
        except Exception:
            print("Failed while writing the video file:")
            traceback.print_exc()
        finally:
            # close resources to ensure ffmpeg finishes writing audio streams
            try:
                clip.close()
            except Exception:
                pass
            try:
                audio.close()
            except Exception:
                pass


if __name__ == "__main__":
    main()