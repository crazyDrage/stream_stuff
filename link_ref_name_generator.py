

def remove_file_ending(file_name):
    file_endings = [
        ".jpeg",
        ".png",
        ".gif"
    ]
    for file_ending in file_endings:
        if file_name.lower().endswith(file_ending.lower()):
            return file_name[:-len(file_ending)]

    return file_name

def convert_url_to_filename(url_string):

    url_new = url_string.replace(":", "..")
    url_new = url_new.replace("/", "_-_")
    print(url_new)
    return url_new

def convert_filename_to_url(file_name):
    file_name = remove_file_ending(file_name)
    png_new_url = file_name.replace("..", ":")
    png_new_url = png_new_url.replace("_-_", "/")
    print(png_new_url)
    return png_new_url



def main():
    link_string = "https://www.vecteezy.com/png/55325903-elegant-black-dahlia-flower-on-a-pure-transparent-background-showcasing-its-unique-beauty-black-dahlia-on-isolated-transparent-background-black-color-dahlia-flower-transparent-background"

    link_as_text = convert_url_to_filename(link_string)
    convert_filename_to_url(link_as_text)


if __name__ == "__main__":
    main()