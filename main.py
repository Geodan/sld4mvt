import querywriter as qw
import sldextract as se


# sld = pathname
# mapping = mapping
# tile =

if __name__ == "__main__":
    for layr in se.sld_to_rules("../slds/gm-sld-master/marketing/pc4_p_autoch.sld"):
        for zl in qw.zoom_to_scale:
            query = layr.make_query(qw.zoom_to_scale[zl])
            qw.writer(layr.name, zl, query)