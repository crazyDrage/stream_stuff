import pathlib#

import subprocess


ffmpeg_exe = pathlib.Path("C://Users//Dragon//software//ffmpeg-master-latest-win64-gpl-shared//ffmpeg-master-latest-win64-gpl-shared//bin//ffmpeg.exe")

input_folder = pathlib.Path("C://Users//Dragon//Videos//clip_temp")
video_ending = ".mp4"
audio_ending = ".wav"

def get_file_list(folder_path: pathlib.Path) -> dict:
    video_file = None
    audio_files = []
    for file in folder_path.glob(f"*{video_ending}"):
        if file.name.startswith("_"):
            continue
        video_file = file
    for file in folder_path.glob(f"*{audio_ending}"):
        if file.name.startswith("_"):
            continue
        audio_files.append(file)
    return {
        "video_file": video_file,
        "audio_files": audio_files,
    }
def command_builder_2() -> list:
    """
    ffmpeg
  -i video.mp4
  -i audio1.wav
  -i audio2.wav
  -i audio3.wav
  -i audio4.wav
  -i audio5.wav
  -i audio6.wav
  -map 0:v
  -map 1:a
  -map 2:a
  -map 3:a
  -map 4:a
  -map 5:a
  -map 6:a
  -c:v copy
  -c:a aac
  output.mp4
    """
    file_list = get_file_list(input_folder)
    video_file = file_list["video_file"]
    audio_files = file_list["audio_files"]
    commands = []
    commands.append(f"-i {str(video_file)}")
    commands.append("-map 0:v")
    for index, audio_file in enumerate(audio_files):
        commands.append(f"-i {str(audio_file)}")
        commands.append(f"-map {index + 1}:a")
    commands.append("-c:v copy")
    commands.append("-c:a aac")
    output_file = input_folder.joinpath(f"_combined_output{video_ending}")
    commands.append(str(output_file))
    return commands


def command_builder() -> list:
    """
    ffmpeg
  -i video.mp4
  -i en.wav
  -i fr.wav
  -i de.wav
  -i es.wav
  -i it.wav
  -i jp.wav
  -map 0:v
  -map 1:a -metadata:s:a:0 language=eng
  -map 2:a -metadata:s:a:1 language=fra
  -map 3:a -metadata:s:a:2 language=deu
  -map 4:a -metadata:s:a:3 language=spa
  -map 5:a -metadata:s:a:4 language=ita
  -map 6:a -metadata:s:a:5 language=jpn
  -c:v copy
  -c:a aac
  output.mp4
    """
    file_list = get_file_list(input_folder)
    video_file = file_list["video_file"]
    audio_files = file_list["audio_files"]
    commands = []
    commands.append("-i")
    commands.append(str(video_file))
    for index, audio_file in enumerate(audio_files):
        commands.append("-i")
        commands.append(str(audio_file))

    commands.append("-map")
    commands.append("0:v")
    for index, audio_file in enumerate(audio_files):
        commands.append("-map")
        commands.append(f"{index + 1}:a")

        audio_name = audio_file.stem.split("-")[-1]
        commands.append(f"-metadata:s:a:{index}")
        commands.append(f"title={audio_name}")  # Change 'eng' to appropriate language
    commands.append("-c:v")
    commands.append("copy")
    commands.append("-c:a")
    commands.append("aac")
    output_file = input_folder.joinpath(f"_combined_output{video_ending}")
    commands.append(str(output_file))
    return commands

def main():
    result = subprocess.run([ffmpeg_exe, *command_builder()], capture_output=True)
    if result.returncode != 0:
        print("FFmpeg execution failed.")
        print("Error Output:")
        print(result.stderr.decode())
        return
    output = result.stdout.decode()
    print(output)


if __name__ == "__main__":
    main()


