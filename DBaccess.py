import psycopg2

# Initialize database parameters
host = "metis.geodan.nl"
user = "freekb"
dbname = "research"
port = "5432"

mapping = {"OSM_Roads": "freeks_schema.osmweg"}


class DBConnect:

    def __init__(self, host="", user="", dbname="", port=""):
        self.conn = psycopg2.connect("host={} user={} dbname={} port={}".format(host, user, dbname, port))
        self.cur = self.conn.cursor()

    def do_query(self, query):
        self.cur.execute(query)
        return self.cur.fetchall()

    def close(self):
        self.cur.close()
        self.conn.close()
