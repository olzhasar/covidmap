import json
import os

files = (
    (1, "almaty_city.geo.json"),
    (2, "astana_city.geo.json"),
    (3, "qaragandy_region.geo.json"),
    (4, "almaty_region.geo.json"),
    (5, "aqtobe_region.geo.json"),
    (6, "shymkent_city.geo.json"),
    (7, "north_kazakhstan_region.geo.json"),
    (8, "zhambyl_region.geo.json"),
    (9, "atyrau_region.geo.json"),
    (10, "pavlodar_region.geo.json"),
    (11, "mangystau_region.geo.json"),
    (12, "aqmola_region.geo.json"),
    (13, "turkestan_region.geo.json"),
    (14, "east_kazakhstan_region.geo.json"),
    (15, "qostanay_region.geo.json"),
    (16, "west_kazakhstan_region.geo.json"),
    (17, "qyzylorda_region.geo.json"),
)


data = {
    "type": "FeatureCollection",
    "features": [],
}

for region_id, filename in files:
    print(filename)
    with open(os.path.join("geojson", filename), "r") as f:

        file_data = json.load(f)

    if 'geometries' in file_data:
        obj = file_data['geometries'][0]
        print(len(file_data['geometries']))
    else:
        obj = file_data

    data["features"].append(
        {
            "type": "Feature",
            "properties": {"id": region_id},
            "geometry": obj,
            "id": region_id,
        }
    )

with open("geojson/regions.geo.json", "w") as f:
    json.dump(data, f)
