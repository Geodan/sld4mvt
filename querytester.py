import DBaccess

db = DBaccess.DBConnect(DBaccess.host, DBaccess.user, DBaccess.dbname, DBaccess.port)

query = """
CREATE TABLE freeks_schema.pytest AS(
SELECT *
FROM freeks_schema.osmweg
LIMIT 10)
"""

db.cur.execute(query)
db.conn.commit()
db.close()

