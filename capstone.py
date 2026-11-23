import pandas as pd
from bokeh.io import output_file

output_file("all_europe_energy_transition.html")
# ---------------------------------------------------------
# 1. LOAD DATA
ember_file = "Datasets/release_generation_yearly_lower.csv"
owid_energy_file = "Datasets/owid-energy-data.csv"
owid_co2_url = "Datasets/owid-co2-data.csv"

df_ember = pd.read_csv(ember_file)
df_owid_e = pd.read_csv(owid_energy_file, usecols=["iso_code", "year", "coal_share_elec", "gdp"])
df_owid_c = pd.read_csv(owid_co2_url, usecols=["iso_code", "year", "co2_per_capita"])

# ---------------------------------------------------------
# 2. FILTERING AND AGGREGATION
eu_ember = df_ember[
    (df_ember["Continent"] == "Europe")
    & (df_ember["ISO 3 code"].notna())
    & (df_ember["Year"] >= 2010)
    ].copy()

# Wind and solar
wind_solar = eu_ember[eu_ember["Electricity source"] == "Wind and solar"][
    ["Area", "ISO 3 code", "Year", "Share of generation (%)"]
].rename(columns={"Share of generation (%)": "wind_solar_share"})

# Total generation CO
carbon_int = eu_ember[eu_ember["Electricity source"] == "Total generation"][
    ["ISO 3 code", "Year", "Emissions intensity (gCO2e/kWh)"]
].rename(columns={"Emissions intensity (gCO2e/kWh)": "carbon_intensity"})

df_merged = pd.merge(
    wind_solar, carbon_int, on=["ISO 3 code", "Year"], how="inner"
)

# ---------------------------------------------------------
# 3. EMBER + OWID
df_merged = pd.merge(
    df_merged,
    df_owid_e,
    left_on=["ISO 3 code", "Year"],
    right_on=["iso_code", "year"],
    how="left",
)
df_merged = pd.merge(
    df_merged,
    df_owid_c,
    left_on=["ISO 3 code", "Year"],
    right_on=["iso_code", "year"],
    how="left",
)

df_clean = (
    df_merged[
        [
            "Area",
            "ISO 3 code",
            "Year",
            "wind_solar_share",
            "carbon_intensity",
            "coal_share_elec",
            "co2_per_capita",
        ]
    ]
    .dropna(subset=["wind_solar_share", "carbon_intensity"])
    .copy()
)

df_clean["coal_share_elec"] = df_clean["coal_share_elec"].fillna(0).round(1)
df_clean["co2_per_capita"] = df_clean["co2_per_capita"].fillna(0).round(2)

all_countries = sorted(df_clean["Area"].unique().tolist())
