from lxml import etree
import math


def sld_to_rules(path):
    """
    Takes an SLD file from a specified path.
    Returns a list of Layer objects, which contain a list of Rules, which contain a list of Filters.
    """
    tree = etree.parse(path)
    root = tree.getroot()

    layers = []
    for layer in root.iter('{*}NamedLayer'):
        rules = []
        for rule in layer.iter('{*}Rule'):

            # Ignore labels, we just want features FOR NOW
            if rule.find('{*}TextSymbolizer') is not None:
                if rule.find('{*}PointSymbolizer') is None and \
                   rule.find('{*}LineSymbolizer') is None and \
                   rule.find('{*}PolygonSymbolizer') is None:
                    continue

            # Get min/max scale denominator, if they exist
            min_scale_el = rule.find('{*}MinScaleDenominator')
            if min_scale_el is None:
                min_scale = 0
            else:
                min_scale = int(float(min_scale_el.text))

            max_scale_el = rule.find('{*}MaxScaleDenominator')
            if max_scale_el is None:
                max_scale = math.inf
            else:
                max_scale = int(float(max_scale_el.text))

            # Assume there is one Filter per Rule
            filt = rule.find('{*}Filter')
            filters = []
            logical = None

            if filt is not None:

                # Check for And/Or, otherwise None
                if filt.find('{*}Or') is not None:
                    logical = "or"
                elif filt.find('{*}And') is not None:
                    logical = "and"
                else:
                    logical = None

                # Add Filter criteria to list
                filters += get_filters("=", filt.iterfind('.//{*}PropertyIsEqualTo'))
                filters += get_filters("<", filt.iterfind('.//{*}PropertyIsLessThan'))
                filters += get_filters("<", filt.iterfind('.//{*}PropertyIsLessThanOrEqualTo'))
                filters += get_filters(">", filt.iterfind('.//{*}PropertyIsGreaterThan'))
                filters += get_filters(">", filt.iterfind('.//{*}PropertyIsGreaterThanOrEqualTo'))

            rules.append(Rule(min_scale, max_scale, logical, filters))
        layers.append(Layer(layer.find('{*}Name').text, rules))
    return layers


def get_filters(logic_string, sld_element):
    """
    Returns list of Filter objects per rule.
    """
    filts = []
    for sub_element in sld_element:
        args = [logic_string]
        for binary in sub_element:
            if "PropertyName" in binary.tag:
                args.append(binary.text)
            elif "Literal" in binary.tag:
                args.append(binary.text)
            elif "Function" in binary.tag:
                if binary.attrib["name"] == "area":
                    args.append("ST_AREA({})".format(binary[0].text))
                else:
                    raise Exception("Unknown function type found in Filter.")
            elif has_arithmetic(sub_element):
                args.append(get_arithmetic(binary))
            else:
                raise Exception("SLD file not structured as expected.\n"
                                "Functionality found not yet supported by this program.")

        filts.append(Filter(*args))
    return filts


def get_arithmetic(sld_element):
    """
    Returns arithmetic operator string for WHERE clause in query.
    """
    operators = {"Add": "+", "Sub": "-", "Mul": "*", "Div": "/"}
    for op in operators:
        if op in sld_element.tag:
            arith_op = operators[op]
    op_vals = []
    for element in sld_element:
        nested_arith = False
        for op in operators:
            if op in element.tag:
                op_vals.append(get_arithmetic(element))
                nested_arith = True
        if not nested_arith:
            prop = element.find("{*}PropertyName")
            if "Literal" in element.tag:
                op_vals.append(element.text)
            elif "PropertyName" in element.tag:
                op_vals.append(element.text)
            elif prop is None:
                lit = element.find("{*}Literal")
                if lit is not None:
                    op_vals.append(lit.text)
                else:
                    raise Exception("Unknown element structure found in arithmetic operator.")
            else:
                op_vals.append(prop.text)
                print(prop.text)

    arith_str = "({} {} {})".format(op_vals[0], arith_op, op_vals[1])
    return arith_str


def is_number(string):
    """
    Check whether a string is a number.
    """
    try:
        float(string)
        return True
    except ValueError:
        return False


def has_arithmetic(sld_element):
    """
    Check whether an sld element has an arithmetic operator sub-element.
    """
    if sld_element.find('.//{*}Add') is not None:
        return True
    elif sld_element.find('.//{*}Sub') is not None:
        return True
    elif sld_element.find('.//{*}Mul') is not None:
        return True
    elif sld_element.find('.//{*}Div') is not None:
        return True
    else:
        return False


class Filter:
    """
    Filter to be used in WHERE clause.
    """
    def __init__(self, logical_string, field, value):
        self.logical_string = logical_string
        self.field = field
        self.value = value


class Rule:
    """
    Rule derived from SLD file.
    """
    def __init__(self, min_scale=0, max_scale=math.inf, logical=None, filters=[]):
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.logical = logical
        self.filters = filters

    def scale_select(self, input_denom):
        """
        Gives input for the WHERE clause based on scale denominator.
        Returns: - None,    when input_denom is outside Rule scale scope
                 - "",      when the Rule contains no Filters
                 - string,  otherwise
        """
        clause = ""
        if self.min_scale <= input_denom <= self.max_scale:
            if len(self.filters) > 0:
                if self.logical is None:
                    clause += "({} {} {})".format(self.filters[0].field,
                                                  self.filters[0].logical_string,
                                                  self.filters[0].value)
                else:
                    clause += "("
                    for fil in self.filters:
                        clause += "({} {} {}) {} ".format(fil.field,
                                                          fil.logical_string,
                                                          fil.value,
                                                          self.logical)
                    clause = clause[:-len(" {} ".format(self.logical))]
                    clause += ")"
            return clause


class Layer:
    """
    Layer on which the rules are applicable.
    """
    def __init__(self, name="", rules=[]):
        self.name = name
        self.rules = rules

    def make_query(self, input_denom, mapping):
        """
        Returns WHERE clause for query, based on scale input.
        """
        # gmo = gm()
        # tilebounds = gmo.TileBounds(*config.tile)
        # intrsct = "{} && ST_MakeEnvelope({}, {}, {}, {}, 3857)".format(
        #     config.geom_column, *tilebounds)
        query = "SELECT * FROM {} WHERE (".format(mapping[self.name])
        is_where_str = False
        is_where_pop = False
        for rul in self.rules:
            where_sub = rul.scale_select(input_denom)

            # Rule.scale_select() might return None
            if type(where_sub) is str:
                is_where_str = True

                if len(where_sub) > 0:
                    is_where_pop = True

                    # Prevent repetition in query (e.g. because of lines and fills)
                    if where_sub not in query:
                        query += rul.scale_select(input_denom)
                        query += " OR "

        if is_where_pop:
            query = query[:-4]
            query += ")"
        elif is_where_str:
            query = query[:-8]
        else:
            query += "False)"
        return query
