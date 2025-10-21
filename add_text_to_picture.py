import pathlib
import json
import copy
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime, timedelta, timezone

project_root = pathlib.Path(__file__).parent
data_path = project_root.joinpath("data", "schedule")

TIME_ZONE_DIFF_FROM_UTC = {
    "UTC": 0,
    "EST": -6
}


def convert_time_str(time_str, offset_hours):
    """Convert a time string like '12:00 am' by adding offset_hours."""
    try:
        t = datetime.strptime(time_str, "%I:%M %p")
        new_t = t + timedelta(hours=offset_hours)
        return new_t.strftime("%I:%M %p")
    except Exception:
        return time_str


def get_timezone_offset_difference(
        time_zone_01: str,
        time_zone_offset_01: int | float,
        time_zone_02: str,
        time_zone_offset_02: int | float
) -> float:
    offset_01 = TIME_ZONE_DIFF_FROM_UTC.get(time_zone_01, 0) + time_zone_offset_01
    offset_02 = TIME_ZONE_DIFF_FROM_UTC.get(time_zone_02, 0) + time_zone_offset_02

    # Difference between the two offsets
    difference = offset_02 - offset_01
    return difference


def draw_text(draw,
              base_image,
              draw_info,
              debug=True):
    box_start = draw_info["box_start"]
    box_end = draw_info["box_end"]
    bg_picture_path = draw_info.get("bg_picture_path", "")
    info_text = draw_info.get("info_text", [])
    text_color = draw_info.get("color", "#000000")
    text_size = draw_info.get("size", 20)
    align = draw_info.get("align", "l").lower()
    valign = draw_info.get("valign", "t").lower()

    # Compute box geometry
    box = [box_start["x"], box_start["y"], box_end["x"], box_end["y"]]
    box_width = box_end["x"] - box_start["x"]
    box_height = box_end["y"] - box_start["y"]

    # Optional debug outline
    if debug:
        draw.rectangle(box,
                       outline="black",
                       width=2)

    # Optional background image
    if bg_picture_path:
        bg_path = data_path.joinpath(bg_picture_path)
        if bg_path.exists():
            bg_image = Image.open(bg_path).convert("RGBA").resize((box_width, box_height))
            base_image.paste(bg_image, (box_start["x"], box_start["y"]), bg_image)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", text_size)
    except:
        font = ImageFont.load_default()

    line_height = text_size + 5
    total_text_height = len(info_text) * line_height

    # Vertical alignment
    if valign == "c":
        y_cursor = box_start["y"] + (box_height - total_text_height) / 2
    elif valign == "b":
        y_cursor = box_end["y"] - total_text_height - 5
    else:
        y_cursor = box_start["y"] + 5

    # Draw text lines
    for text_line in info_text:
        text_width = draw.textlength(text_line, font=font)

        if align == "c":
            x = box_start["x"] + (box_width - text_width) / 2
        elif align == "r":
            x = box_end["x"] - text_width - 5
        else:
            x = box_start["x"] + 5

        draw.text((x, y_cursor), text_line, font=font, fill=text_color)
        y_cursor += line_height


def handle_config_file(data_json_path, debug=False):
    # Load config file
    with open(data_json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    base_tz_name = config["time_zone"]["name"]
    base_tz_offset = config["time_zone"]["number"]
    start_date_time = datetime.now()

    try:
        start_date_time = datetime.strptime(config["start_date_time"], "%d.%m.%Y")
    except Exception:
        pass


    tz_to_generate = config.get("time_zones_to_generate", [config["time_zone"]])
    base_image_path = data_path.joinpath(config["base_image"])

    for tz in tz_to_generate:
        time_zone_text = copy.deepcopy(config["time_zone_text"])
        tz_name = tz["name"]
        tz_offset = tz["number"]

        # compute offset difference from base zone
        # offset_diff = tz_offset - base_tz_offset
        offset_diff = get_timezone_offset_difference(
            time_zone_01=base_tz_name,
            time_zone_offset_01=base_tz_offset,
            time_zone_02=tz_name,
            time_zone_offset_02=tz_offset
        )

        print(f"🕓 Generating schedule for {tz_name} "
              f"(Base: {base_tz_name} {base_tz_offset:+}, Offset diff: {offset_diff:+})")

        base_image = Image.open(base_image_path).convert("RGBA")
        draw = ImageDraw.Draw(base_image)

        time_zone_string = ""
        if tz_offset == 0:
            time_zone_string = tz_name
        elif tz_offset > 0:
            time_zone_string = f"{tz_name} +{tz_offset}"
        else:
            time_zone_string = f"{tz_name} {tz_offset}"

        if "info_text" in time_zone_text:
            end_date = (start_date_time + timedelta(days=time_zone_text["day_nr"]))
            start_date_str = start_date_time.strftime("%d %b")
            end_date_str = end_date.strftime("%d %b")
            time_zone_text["info_text"] = [
                t.format(time_zone=time_zone_string,
                         start_date=start_date_str,
                         end_date=end_date_str)
                for t in time_zone_text["info_text"]
            ]
        draw_text(draw=draw,
                  base_image=base_image,
                  draw_info=time_zone_text,
                  debug=debug)

        for day in config.get("days", []):
            start_time = convert_time_str(day.get("start_time", ""), offset_diff)
            end_time = convert_time_str(day.get("end_time", ""), offset_diff)
            day_string = (start_date_time + timedelta(days=day["day_nr"])).strftime("%A")

            for item in day.get("info_items", []):
                item = copy.deepcopy(item)
                if "info_text" in item:
                    item["info_text"] = [
                        t.format(start_time=start_time,
                                 end_time=end_time,
                                 time_zone=time_zone_string,
                                 day_name_short=day_string[:2],
                                 day_name_long=day_string)
                        for t in item["info_text"]
                    ]


                draw_text(draw=draw,
                          base_image=base_image,
                          draw_info=item,
                          debug=debug)


        # Save result per time zone
        output_name = f"output_schedule_{tz_name}.png"
        output_path = data_json_path.parent.joinpath(output_name)
        base_image.save(output_path)
        print(f"✅ Saved: {output_path}")


def main():
    data_json_path = data_path.joinpath("schedule_text_data.json")
    handle_config_file(data_json_path=data_json_path, debug=False)


if __name__ == "__main__":
    main()
