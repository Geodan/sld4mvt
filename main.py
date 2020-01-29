import sldextract as se
import ast
import argparse


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


def is_zoom_int(variable, string):
    try:
        int(variable)
    except ValueError:
        parser.error("--zoom{} should be an integer.".format(string))
    else:
        if 0 <= int(variable) <= 20:
            return int(variable)
        else:
            parser.error("--zoom{} should be between 0 and 20.".format(string))


# Initialize argparser
parser = argparse.ArgumentParser(description="Get queries for MVTs based on SLDs.")
parser.add_argument("-f", "--function", required=True,
                    help="Can be 'getlayernames' or 'getqueries'. "
                         "Function 'getlayernames' only requires --sld to be specified.")
parser.add_argument("-s", "--sld", required=True,
                    help="Path or URL to SLD file.")
parser.add_argument("-l", "--layername",
                    help="Specifies what layer to query. "
                         "When not given, all NamedLayers are queried.")
parser.add_argument("-m", "--mapping",
                    help="Dictionary that maps NamedLayers to database tables. "
                         "Should be in the form \"{'key': 'value'}\".")
parser.add_argument("-z", "--zoommin",
                    help="Optional argument, default value is 0.")
parser.add_argument("-x", "--zoommax",
                    help="Optional argument, default value is 20.")
args = parser.parse_args()


if __name__ == "__main__":
    # Set default zoom values
    min_zoom, max_zoom = 0, 20

    # Print the names of the NamedLayers
    if args.function == "getlayernames":
        for layer in se.sld_to_rules(args.sld):
            print(layer.name)

    # Print the requested queries
    elif args.function == "getqueries":
        if args.mapping is None:
            parser.error("'getqueries' requires a Mapping attribute. Add a mapping with the '-m' or '--mapping' flag.")
        else:
            mapping = ast.literal_eval(args.mapping)

            if args.zoommin is not None:
                min_zoom = is_zoom_int(args.zoommin, "min")
            if args.zoommax is not None:
                max_zoom = is_zoom_int(args.zoommax, "max")
            if min_zoom > max_zoom:
                parser.error("--zoommax has to be greater than or equal to --zoommin")

            layernames = [layer.name for layer in se.sld_to_rules(args.sld)]
            if (args.layername is not None) and (args.layername not in layernames):
                parser.error("Given --layername not present in SLD.")
            else:
                for layer in se.sld_to_rules(args.sld):
                    if (args.layername is None) or (layer.name == args.layername):
                        for zl in range(min_zoom, max_zoom + 1):
                            query = layer.make_query(zoom_to_scale[zl], mapping)
                            print(query)
