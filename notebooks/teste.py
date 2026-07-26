# %%

import pandas as pd

# %% 
# 1. Carrega uma partição gerada na camada Gold (ajuste o ano/round se necessário)
file_path = "data/gold/year=2023/round=01/R.parquet"
df_gold = pd.read_parquet(file_path)

# 2. Exibe métricas de dimensão e lista de colunas
print(f"Dimensões: {df_gold.shape[0]} pilotos x {df_gold.shape[1]} colunas\n")
print("Colunas disponíveis no dataset Gold:")
print(df_gold.columns.tolist())
# %%

df_gold.head(15)
# %%

df_w = pd.read_parquet("data/silver/weather/year=2023/round=01/R.parquet")

print("Valores únicos de chuva na corrida:", df_w['Rainfall'].unique())
print("Houve algum registro de chuva?", df_w['Rainfall'].astype(bool).any())

# %%
