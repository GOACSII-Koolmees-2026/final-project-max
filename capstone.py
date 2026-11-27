import pandas as pd
from bokeh.io import output_file, show
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, CustomJS, HoverTool, Select
from bokeh.plotting import figure

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

# ---------------------------------------------------------
# 4. Graph 1
latest_year = int(df_clean["Year"].max())
df_latest = df_clean[df_clean["Year"] == latest_year]
source_scatter = ColumnDataSource(df_latest)

p1 = figure(
    title=f"All European Countries: Wind & Solar Share vs. Carbon Intensity ({latest_year})",
    x_axis_label="Wind and Solar Share of Electricity (%)",
    y_axis_label="Carbon Intensity (gCO2e/kWh)",
    width=900,
    height=480,
    tools="pan,wheel_zoom,box_zoom,reset,save",
)

p1.scatter(
    x="wind_solar_share",
    y="carbon_intensity",
    source=source_scatter,
    size=10,
    color="#1f77b4",
    alpha=0.8,
)
# ISO-3 name
p1.text(
    x="wind_solar_share",
    y="carbon_intensity",
    text="ISO 3 code",
    source=source_scatter,
    text_font_size="8pt",
    x_offset=5,
    y_offset=4,
    text_alpha=0.75,
)

hover1 = HoverTool(
    tooltips=[
        ("Country", "@Area (@{ISO 3 code})"),
        ("Wind & Solar Share", "@wind_solar_share{0.1f}%"),
        ("Carbon Intensity", "@carbon_intensity{0} gCO2e/kWh"),
        ("Coal Share (OWID)", "@coal_share_elec{0.1f}%"),
        ("CO2 per Capita (OWID)", "@co2_per_capita{0.2f} t"),
    ]
)
p1.add_tools(hover1)

# ---------------------------------------------------------
# 5. GRAPH 2
p2 = figure(
    title="Carbon Intensity Over Time: All European Countries (Select a Country to Highlight)",
    x_axis_label="Year",
    y_axis_label="Carbon Intensity (gCO2e/kWh)",
    width=900,
    height=480,
    tools="pan,wheel_zoom,box_zoom,reset,save",
)

for country in all_countries:
    c_df = df_clean[df_clean["Area"] == country].sort_values("Year")
    src = ColumnDataSource(c_df)
    p2.line(
        x="Year",
        y="carbon_intensity",
        source=src,
        line_width=1.5,
        color="#b0b0b0",
        alpha=0.45,
    )

default_country = "Germany" if "Germany" in all_countries else all_countries[0]
highlight_df = df_clean[df_clean["Area"] == default_country].sort_values("Year")
highlight_source = ColumnDataSource(highlight_df)
full_source = ColumnDataSource(df_clean)

p2.line(
    x="Year",
    y="carbon_intensity",
    source=highlight_source,
    line_width=3.5,
    color="#d62728",
    legend_label="Selected Country",
)
p2.scatter(
    x="Year",
    y="carbon_intensity",
    source=highlight_source,
    size=7,
    color="#d62728",
    legend_label="Selected Country",
)

hover2 = HoverTool(
    tooltips=[
        ("Country", "@Area"),
        ("Year", "@Year"),
        ("Carbon Intensity", "@carbon_intensity{0} gCO2e/kWh"),
        ("Wind & Solar", "@wind_solar_share{0.1f}%"),
        ("Coal Share (OWID)", "@coal_share_elec{0.1f}%"),
    ]
)
p2.add_tools(hover2)

select = Select(
    title="Choose a European Country to Highlight:",
    value=default_country,
    options=all_countries,
)

callback = CustomJS(
    args=dict(
        highlight_source=highlight_source, full_source=full_source, select=select
    ),
    code="""
    const selected = select.value;
    const data = full_source.data;
    const out = {Year: [], carbon_intensity: [], Area: [], wind_solar_share: [], coal_share_elec: []};

    let rows = [];
    for (let i = 0; i < data['Area'].length; i++) {
        if (data['Area'][i] === selected) {
            rows.push({
                Year: data['Year'][i],
                carbon_intensity: data['carbon_intensity'][i],
                Area: data['Area'][i],
                wind_solar_share: data['wind_solar_share'][i],
                coal_share_elec: data['coal_share_elec'][i]
            });
        }
    }
    rows.sort((a, b) => a.Year - b.Year);

    for (let r of rows) {
        out.Year.push(r.Year);
        out.carbon_intensity.push(r.carbon_intensity);
        out.Area.push(r.Area);
        out.wind_solar_share.push(r.wind_solar_share);
        out.coal_share_elec.push(r.coal_share_elec);
    }
    highlight_source.data = out;
    highlight_source.change.emit();
""",
)
select.js_on_change("value", callback)

# ---------------------------------------------------------
#  6. SHOW
show(column(p1, select, p2))
