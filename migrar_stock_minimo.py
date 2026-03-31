import sqlite3
from utils.constants import DB_PATH

conn = sqlite3.connect(str(DB_PATH))
cursor = conn.cursor()

cursor.execute("""
ALTER TABLE inventario
ADD COLUMN stock_minimo INTEGER NOT NULL DEFAULT 5
""")

conn.commit()
conn.close()

print("Columna stock_minimo agregada correctamente")
