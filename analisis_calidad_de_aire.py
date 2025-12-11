import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("city_air_quality.csv")



print("Temperatura corregida (describe):")
print(df["Temperature"].describe())

#  Convertir fecha
df["Date"] = pd.to_datetime(df["Date"])

# Limpieza de outliers (IQR)
pollutants = ["PM2.5","PM10","NO2","SO2","CO","O3"]
df_clean = df.copy()

# Corrección de Temperature
df["Temperature"] = pd.to_numeric(df["Temperature"], errors="coerce")
if df["Temperature"].median() < 5:
    df["Temperature"] = df["Temperature"] * 10

for col in pollutants:
    Q1 = df_clean[col].quantile(0.25)
    Q3 = df_clean[col].quantile(0.75)
    IQR = Q3 - Q1
    lower = Q1 - 1.5 * IQR
    upper = Q3 + 1.5 * IQR
    df_clean.loc[(df_clean[col] < lower) | (df_clean[col] > upper), col] = np.nan

print("Outliers eliminados (NaN por columna):")
print(df_clean[pollutants].isna().sum())

# Índice AQI simplificado
who = {"PM2.5":15,"PM10":45,"NO2":25,"SO2":40,"CO":4,"O3":100}
ratios = pd.DataFrame(index=df_clean.index)
for p in pollutants:
    ratios[p] = df_clean[p] / who[p]

df_clean["AQI_simple"] = ratios.max(axis=1) * 100
print("Estadísticas del AQI_simple:")
print(df_clean["AQI_simple"].describe())

#  Promedios mensuales
df_clean["YearMonth"] = df_clean["Date"].dt.to_period("M")
monthly = df_clean.groupby(["City","YearMonth"])[pollutants + ["AQI_simple"]].mean().reset_index()
monthly["YearMonth"] = monthly["YearMonth"].dt.to_timestamp()
print("Promedios mensuales (primeras filas):")
print(monthly.head())

#  Matriz de correlación
corr = df_clean[["Temperature","Humidity"] + pollutants].corr()
print("Matriz de correlación:")
print(corr)

#  Ciudades que superan niveles OMS
city_exceed = df_clean.groupby("City", group_keys=False).apply(lambda x: pd.Series({
    "dias_totales": x["Date"].nunique(),
    "dias_excedidos": x.loc[x["AQI_simple"] > 100, "Date"].nunique(),
    "porcentaje_excedido": 100 * x.loc[x["AQI_simple"] > 100, "Date"].nunique() / x["Date"].nunique(),
    "AQI_promedio": x["AQI_simple"].mean()
})).reset_index()

print("Ciudades que superan niveles OMS (primeras filas):")
print(city_exceed.sort_values("porcentaje_excedido", ascending=False).head())

#  Gráfico – Evolución PM2.5
ciudad = df_clean["City"].value_counts().idxmax()
df_city = df_clean[df_clean["City"] == ciudad]

plt.figure(figsize=(12,4))
sns.lineplot(data=df_city, x="Date", y="PM2.5")
plt.title(f"Evolución de PM2.5 - {ciudad}")
plt.xlabel("Fecha")
plt.ylabel("PM2.5 (µg/m³)")
plt.show()

# Gráfico 
plt.figure(figsize=(10,6))
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Correlación entre contaminantes y clima")
plt.show()

#  Gráfico  Ranking ciudades más contaminadas
top = city_exceed.sort_values("AQI_promedio", ascending=False).head(15)
plt.figure(figsize=(12,5))
sns.barplot(data=top, x="City", y="AQI_promedio")
plt.xticks(rotation=45)
plt.title("Ranking de ciudades más contaminadas (AQI promedio)")
plt.show()

# Promedio de temperatura por ciudad
promedio_temp_ciudad = df_clean.groupby("City")["Temperature"].mean().reset_index()
print("Promedio de temperatura por ciudad:")
print(promedio_temp_ciudad)

#CSV Actualizado.
df_clean.to_csv("cityairquality_actualizado.csv", index=False)