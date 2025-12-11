from analisis_calidad_de_aire import corr, city_exceed

# Correlaciones más altas entre clima y contaminantes
corr_subset = corr.loc[["Temperature", "Humidity"], ["PM2.5","PM10","NO2","SO2","CO","O3"]]
max_corr = corr_subset.abs().stack().nlargest(3)
print(">>> Correlaciones clima–contaminantes más altas (abs):")
for (var_clima, var_cont), val in max_corr.items():
    signo = corr.loc[var_clima, var_cont]
    print(f"{var_clima} vs {var_cont}: {signo:.3f}")

# Ranking completo de ciudades por porcentaje de días que exceden OMS
city_exceed_sorted = city_exceed.sort_values("porcentaje_excedido", ascending=False)
print(">>> Ranking completo de ciudades con porcentaje de días excedidos (OMS):")
print(city_exceed_sorted[["City","porcentaje_excedido","AQI_promedio"]].round(2).to_string(index=False))

#  Ciudad más contaminada por AQI promedio
top_aqi = city_exceed.sort_values("AQI_promedio", ascending=False).head(1)
ciudad_top = top_aqi.iloc[0]["City"]
aqi_top = top_aqi.iloc[0]["AQI_promedio"]
print(f">>> Ciudad más contaminada por AQI promedio: {ciudad_top} (AQI_promedio={aqi_top:.2f})")
