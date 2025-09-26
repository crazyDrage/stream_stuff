import pathlib
from pynput.keyboard import Controller, Key
import time


def key_mapping():
    return {
        "ctl_l": 224,
        "shift_l": 225,
        "alt_l": 226,

        "ctl_r": 228,
        "shift_r": 229,
        "alt_r": 230,

        "A": 5,
        "B": 6,
        "C": 7,
        "D": 8,
        "E": 9,
        "F": 10,
        "G": 11,
        "H": 12,
        "num_1": 89,
        "num_2": 90,
        "num_3": 91,
        "num_4": 92,
        "num_5": 93,
        "num_6": 94,
        "num_7": 95,
        "num_8": 96,
        "num_9": 97,
        "num_0": 98,
        "num_+": 87,
        "num_-": 86,
        "f1": 58,
        "f2": 59,
        "f3": 60,
        "f4": 61,
        "f5": 62,
        "f6": 63,
        "f7": 64,
        "f8": 65,
        "f9": 66,
        "f10": 67,
        "f11": 68,
        "f12": 69,
        "f13": 104,
        "f14": 105,
        "f15": 106,
        "f16": 107,
        "f17": 108,
        "f18": 109,
        "f19": 110,
        "f20": 111,
        "f21": 112,
        "f22": 113,
        "f23": 114,
        "f24": 115,
    }


def format_key_action(position: int, key_string: str, push_down: bool = True):
    action_list = []
    if push_down:
        action_list.append(f"Map_{position}=132")
    else:
        action_list.append(f"Map_{position}=4")
    action_list.append(f"DataH_{position}=0")
    action_list.append(f"DataL_{position}={str(key_mapping()[key_string])}")

    return action_list


def delay_action(position: int):
    action_list = [
        f"Map_{position}=6",
        f"DataH_{position}=0",
        f"DataL_{position}=2",
    ]
    return action_list


def convert_keys_and_create_files():
    macro_file = pathlib.Path("data", "macro_keys")
    output_folder = pathlib.Path("data", "output")
    template_file_path = pathlib.Path("data", "macro_file_ref")
    macro_file_lines = macro_file.read_text().split("\n")[7:]
    macro_key_row = []
    key_names = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "0",
        "+",
        "-",
    ]
    for i in range(12):
        start_nr = 6 * i
        macro_lines = macro_file_lines[start_nr: start_nr + 6]
        macro_key_row.append(macro_lines[2].split("=")[1])

    key_dict = {}
    for i in range(len(key_names)):
        key_dict[key_names[i]] = macro_key_row[i]

    template_file_string = template_file_path.read_text()
    for key_key, key_item in key_dict.items():
        output_file = output_folder.joinpath("alt+num_{0}.MSMACRO".format(key_key))
        output_file.write_text(template_file_string.format(key_key, key_item))


def get_header_string(output_file_path, action_count: int, default_delay_ms: int):
    output_file_path = pathlib.Path(output_file_path).absolute()
    if output_file_path.suffix != ".MSMACRO":
        output_file_path = pathlib.Path(str(output_file_path) + ".MSMACRO")

    file_path_string = str(output_file_path).replace("\\", "/")
    header_list = [
        "[Setting]",
        f"MacroFilePath={str(file_path_string)}",
        f"DefaultDelay={str(default_delay_ms)}",
        "DelayType=2",
        "LoopType=0",
        "LoopTime=1",
        f"Count={str(action_count)}"]

    return {
        "header": header_list,
        "path": output_file_path
    }

def generate_macro_file(output_file, keys_list, default_delay_ms=20):
    action_lines = []
    action_count = 0
    i = 0
    while i < len(keys_list):
        if action_count != 0:
            action_lines.extend(delay_action(action_count))
            action_count += 1
        action_lines.extend(
            format_key_action(position=action_count,
                                             key_string=keys_list[i],
                                             push_down=True)
        )
        action_count += 1
        i += 1
    i = len(keys_list) - 1
    while i >= 0:
        action_lines.extend(delay_action(action_count))
        action_count += 1
        action_lines.extend(
            format_key_action(position=action_count,
                                             key_string=keys_list[i],
                                             push_down=False)
        )
        action_count += 1
        i -= 1
    header_info = get_header_string(output_file_path=output_file,
                                    action_count=action_count,
                                    default_delay_ms=default_delay_ms)
    output_file = header_info["path"]
    file_lines = [
        *header_info["header"],
        *action_lines
    ]
    output_file.write_text("\n".join(file_lines) + "\n")


def generate_macro_files():
    output_folder = pathlib.Path("data", "reddragon_macro_files")
    default_delay_ms = 20
    output_folder.mkdir(parents=True, exist_ok=True)

    keys_to_generate = [
        ["alt", "num_1"],
        ["alt", "num_2"],
        ["alt", "num_3"],
        ["alt", "num_4"],
        ["alt", "num_5"],
        ["alt", "num_6"],
        ["alt", "num_7"],
        ["alt", "num_8"],
        ["alt", "num_9"],
        ["alt", "num_0"],
        ["alt", "num_+"],
        ["alt", "num_-"],
    ]
    keys_to_generate = [
        ["ctl_r", "f13"],
        ["ctl_r", "f13"],
        ["ctl_r", "f14"],
        ["ctl_r", "f15"],
        ["ctl_r", "f16"],
        ["ctl_r", "f17"],
        ["ctl_r", "f18"],
        ["ctl_r", "f19"],
        ["ctl_r", "f20"],
        ["ctl_r", "f21"],
        ["ctl_r", "f22"],
        ["ctl_r", "f23"],
        ["ctl_r", "f24"],

        ["alt_r", "f13"],
        ["alt_r", "f13"],
        ["alt_r", "f14"],
        ["alt_r", "f15"],
        ["alt_r", "f16"],
        ["alt_r", "f17"],
        ["alt_r", "f18"],
        ["alt_r", "f19"],
        ["alt_r", "f20"],
        ["alt_r", "f21"],
        ["alt_r", "f22"],
        ["alt_r", "f23"],
        ["alt_r", "f24"],

        ["shift_r", "f13"],
        ["shift_r", "f13"],
        ["shift_r", "f14"],
        ["shift_r", "f15"],
        ["shift_r", "f16"],
        ["shift_r", "f17"],
        ["shift_r", "f18"],
        ["shift_r", "f19"],
        ["shift_r", "f20"],
        ["shift_r", "f21"],
        ["shift_r", "f22"],
        ["shift_r", "f23"],
        ["shift_r", "f24"],
    ]
    for key_list in keys_to_generate:
        output_file = output_folder.joinpath("+".join(key_list) + ".MSMACRO")
        generate_macro_file(output_file=output_file, keys_list=key_list, default_delay_ms=default_delay_ms)


def press_key(key_to_press):
    keyboard = Controller()

    # Press the key
    keyboard.press(key_to_press)
    print(f"Pressed: {key_to_press}")

    # Hold for 1 second
    time.sleep(1)

    # Release the key
    keyboard.release(key_to_press)
    print(f"Released: {key_to_press}")

def generate_test_files():
    try_nr = 0
    try_amount = 6
    output_folder = pathlib.Path("data", "output_test_12")
    output_folder.mkdir(parents=True, exist_ok=True)
    int_list = [i for i in range(300)]
    i = 1
    start_nr = try_nr * try_amount
    start_nr = 116
    for current_int in int_list[start_nr:start_nr + try_amount]:

        output_file = output_folder.joinpath(str(i) + ".MSMACRO")
        output_file_path = pathlib.Path(output_file).absolute()

        if output_file_path.suffix != ".MSMACRO":
            output_file_path = pathlib.Path(str(output_file_path) + ".MSMACRO")

        file_path_string = str(output_file_path).replace("\\", "/")
        header_list = [
            "[Setting]",
            f"MacroFilePath={str(file_path_string)}",
            f"DefaultDelay=20",
            "DelayType=2",
            "LoopType=0",
            "LoopTime=1",
            f"Count=3"]

        action_lines = []
        action_lines.extend([
            f"Map_0=132",
            f"DataH_0=0",
            f"DataL_0={str(current_int)}"
        ])
        action_lines.extend(delay_action(1))

        action_lines.extend([
            f"Map_2=4",
            f"DataH_2=0",
            f"DataL_2={str(current_int)}"
        ])
        file_lines = [
            *header_list,
            *action_lines
        ]
        output_file.write_text("\n".join(file_lines) + "\n")
        i += 1

def main():
    generate_macro_files()
    #generate_test_files()


if __name__ == "__main__":
    main()
