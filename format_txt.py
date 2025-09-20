import pathlib


def main():
    text_path = pathlib.Path("data", "list.txt")
    text_string = text_path.read_text()
    text_split = text_string.split("\n")
    output_list = []

    for s in text_split:
        if s == "":
            continue
        print(s.split("-")[0])



if __name__ == "__main__":
    main()
