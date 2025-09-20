import pathlib

def main():
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
        start_nr = 6*i
        macro_lines = macro_file_lines[start_nr: start_nr + 6]
        macro_key_row.append(macro_lines[2].split("=")[1])

    key_dict = {}
    for i in range(len(key_names)):
        key_dict[key_names[i]] = macro_key_row[i]

    template_file_string = template_file_path.read_text()
    for key_key, key_item in key_dict.items():
        output_file = output_folder.joinpath("alt+num_{0}.MSMACRO".format(key_key))
        output_file.write_text(template_file_string.format(key_key, key_item))
    pass

if __name__ == "__main__":
    main()

