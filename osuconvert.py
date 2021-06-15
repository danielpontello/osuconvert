import json
import re
import sys

section_re = re.compile(r'\[.*\]')
data_re = re.compile(r'.*:.*')

with open(sys.argv[1], "rb") as file:
    lines = file.read().decode('utf-8').replace("\r", "").split("\n")

song_data = {}
current_section = ""

timing_points = []
hit_objects = []


def bit_set(num, bit):
    return (num >> bit & 1) == 1


for line in lines:
    if len(line) > 0:
        if section_re.match(line):
            current_section = line.replace("[", "").replace("]", "").lower().strip()
            print(f"parsing {current_section} section")
            song_data[current_section] = {}
            continue

        if current_section == "timingpoints":
            timing_comp = line.split(",")

            obj = {
                "time": int(timing_comp[0]),
                "beatLength": float(timing_comp[1]),
                "meter": int(timing_comp[2]),
                "sampleSet": timing_comp[3],
                "sampleIndex": timing_comp[4],
                "volume": timing_comp[5],
                "uninherited": timing_comp[6],
                "effects": timing_comp[7]
            }
            timing_points.append(obj)
        elif current_section == "hitobjects":
            hit_comp = line.split(",")

            type = int(hit_comp[3])

            # normal
            if bit_set(type, 0):
                h_obj = {
                    "x": int(hit_comp[0]),
                    "y": int(hit_comp[1]),
                    "time": int(hit_comp[2]),
                    "type": int(hit_comp[3]),
                    "hitsound": hit_comp[4],
                    "objectparams": hit_comp[5]
                }
                hit_objects.append(h_obj)
            # slider
            if bit_set(type, 1):
                points = []
                point_list = hit_comp[5]
                point_params = point_list.split("|")

                curve_type = point_params[0]

                for pt in point_params[1:]:
                    ptc = pt.split(":")
                    points.append({"x": int(ptc[0]), "y": int(ptc[1])})
                s_obj = {
                    "x": int(hit_comp[0]),
                    "y": int(hit_comp[1]),
                    "time": int(hit_comp[2]),
                    "type": int(hit_comp[3]),
                    "hitsound": hit_comp[4],
                    "curvetype": curve_type,
                    "curvepoints": points
                }
            # spinner
            if bit_set(type, 3):
                pass
            pass
        else:
            if data_re.match(line):
                data_comp = line.split(":")
                tag = data_comp[0].strip().lower()
                value = data_comp[1].strip()

                song_data[current_section][tag] = value
song_data["timingpoints"] = timing_points
song_data["hitobjects"] = hit_objects

with open(sys.argv[2], "w") as songfile:
    songfile.write(json.dumps(song_data, indent=4))