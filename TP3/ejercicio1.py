import pandas as pd
import matplotlib.pyplot as plt

url = "https://drive.google.com/uc?export=download&id=1g8KNOJsaE3jzXob-ZsTE_PqYwuxJ05pg"

# Cargar sin encabezado
datos = pd.read_csv(url, header=None)

# Renombrar columnas
datos.columns = ["x", "y"]

# Limpiar paréntesis y espacios
datos["x"] = datos["x"].astype(str).str.replace("(", "", regex=False).str.strip()
datos["y"] = datos["y"].astype(str).str.replace(")", "", regex=False).str.strip()

# Convertir a float
datos["x"] = datos["x"].astype(float)
datos["y"] = datos["y"].astype(float)

print(datos.head())
print(datos.info())

# Graficar
plt.scatter(datos["x"], datos["y"], label="Datos originales")
plt.xlabel("x")
plt.ylabel("y")
plt.title("Dataset original")
plt.legend()
plt.grid(True)
plt.show()