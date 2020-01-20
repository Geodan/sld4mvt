import querywriter as qw
import sldextract as se
import sys
import ast

if __name__ == "__main__":
    sld = sys.argv[1]
    mapping = ast.literal_eval(sys.argv[2])
    min_zoom = int(sys.argv[3])
    max_zoom = int(sys.argv[4])
    # zl = config.tile[2]
    for layr in se.sld_to_rules(sld):
        for zl in range(min_zoom, max_zoom + 1):
            query = layr.make_query(qw.zoom_to_scale[zl], mapping)
            print(query)

    # qw.writer(layr.name, zl, query)
