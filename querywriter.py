import os

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

def writer(name, zoom, query, path=os.path.join(os.environ["HOMEPATH"], "Desktop")):
    with open("{}/query_{}_zoomlevel{}.sql".format(path, name, zoom), "w") as fh:
        fh.write(query)