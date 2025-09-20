from datetime import datetime



def main():
    current_time_string = "03:33:00"
    stream_time_string = "21:46:00"

    target_time_string = "23:59:00"

    current_time = datetime.strptime(current_time_string, '%H:%M:%S')
    stream_time = datetime.strptime(stream_time_string, '%H:%M:%S')
    target_time = datetime.strptime(target_time_string, '%H:%M:%S')

    stream_start_time = current_time - stream_time
    print(current_time.time())

    target_stream_time = target_time - stream_start_time
    print(target_stream_time.time())


def stream_plan():
    stream_times = {
        "Monday": "",
        "2": "",
        "Wednesday": ""
    }


if __name__ == "__main__":
    main()