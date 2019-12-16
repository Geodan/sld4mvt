import DBaccess
import config

db = DBaccess.DBConnect(config.host, config.user, config.dbname, config.port)

query = """
CREATE TABLE freeks_schema.pytest AS(
SELECT *
FROM freeks_schema.osmweg
LIMIT 10)
"""

db.cur.execute(query)
db.conn.commit()
db.close()

