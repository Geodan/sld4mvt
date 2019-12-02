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
        field = sub_element.find('.//{*}PropertyName').text
        value = sub_element.find('.//{*}Literal').text
        if is_number(value):
            value = float(value)
        current_filter = Filter(logic_string, field, value)
        filts.append(current_filter)
    return filts


def is_number(string):
    """
    Check whether a string is a number.
    """

    try:
        float(string)
        return True
    except ValueError:
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

    def make_query(self, input_denom):
        """
        Returns WHERE clause for query, based on scale input.
        """

        query = "SELECT * FROM {} WHERE (".format(self.name)
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
            query += "1 = 2)"
        return query


if __name__ == "__main__":
    for layr in sld_to_rules('../slds/gm-sld-master/topo/topo/t.brt.geografischgebied_punt.sld'):
        print(layr.make_query(3000000))
        # for rule in layr.rules:
        #     print(rule.min_scale, rule.max_scale, rule.logical, rule.filters)
