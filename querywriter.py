import os

def writer(name, zoom, query, path=os.path.join(os.environ["HOMEPATH"], "Desktop")):
    with open("{}/query_{}_zoomlevel{}.sql".format(path, name, zoom), "w") as fh:
        fh.write(query)