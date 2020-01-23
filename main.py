import sldextract as se
import sys
import ast

zoom_to_scale = {
    0: 500000000,
    1: 250000000,
    2: 150000000,
    3: 70000000,
    4: 35000000,
    5: 15000000,
    6: 10000000,
    7: 4000000,
    8: 2000000,
    9: 1000000,
    10: 500000,
    11: 250000,
    12: 150000,
    13: 70000,
    14: 35000,
    15: 15000,
    16: 8000,
    17: 4000,
    18: 2000,
    19: 1000,
    20: 500
}

if __name__ == "__main__":
    min_zoom, max_zoom = 0, 20
    sld = sys.argv[1]
    mapping = ast.literal_eval(sys.argv[2])
    if len(sys.argv[1:]) == 4:
        min_zoom = int(sys.argv[3])
        max_zoom = int(sys.argv[4])
    # zl = config.tile[2]
    for layr in se.sld_to_rules(sld):
        for zl in range(min_zoom, max_zoom + 1):
            query = layr.make_query(zoom_to_scale[zl], mapping)
            print(query)

    # qw.writer(layr.name, zl, query)
