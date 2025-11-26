from src.database import get_data_as_dataframe

# Probemos traer los primeros 5 items
sql = "SELECT * FROM Items LIMIT 5;"
df = get_data_as_dataframe(sql)

print()
print("Si ves una tabla abajo, la conexión funciona:")
print()
print(df)
print()