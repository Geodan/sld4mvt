import querywriter as qw
import sldextract as se
import config


if __name__ == "__main__":
    zl = config.tile[2]
    for layr in se.sld_to_rules("../slds/osm_roads.sld"):
        query = layr.make_query(qw.zoom_to_scale[zl])
        qw.writer(layr.name, zl, query)