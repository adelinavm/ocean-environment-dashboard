import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    df_lama = pd.read_csv("data_clean.csv")

    df_baru_raw = pd.read_excel("20180920_Marine_Pollution.xlsx", sheet_name="Sheet1")
    df_baru_long = pd.melt(df_baru_raw, id_vars=["Countries"], var_name="INDICATOR", value_name="OBS_VALUE")
    df_baru_long["TIME_PERIOD"] = 2018
    df_baru_long["UNIT_MEASURE"] = "COUNT"
    df_baru_long["DATA_SOURCE"] = "SPREP (2018)"

    country_to_code = {
        "American Samoa": "AS", "Cook Islands": "CK", "Fiji": "FJ", "French Polynesia": "PF",
        "International Waters": "IW", "Niue": "NU", "Papua New Guinea": "PG", "Samoa": "WS",
        "Solomon Islands": "SB", "Tokelau": "TK", "Tonga": "TO", "Tuvalu": "TV", "Vanuatu": "VU"
    }
    df_baru_long["GEO_PICT"] = df_baru_long["Countries"].map(country_to_code)
    df_baru_long["INDICATOR"] = "MARINE_POLLUTION_" + df_baru_long["INDICATOR"].str.upper().str.replace(" ", "_")
    df_baru = df_baru_long[["INDICATOR", "GEO_PICT", "TIME_PERIOD", "OBS_VALUE", "UNIT_MEASURE", "DATA_SOURCE"]]

    df_terbaru_raw = pd.read_csv("ENV_Marine_Pollution_Obs_data_v4.csv")
    df_terbaru_long = pd.melt(df_terbaru_raw, id_vars="Row Labels", var_name="INDICATOR", value_name="OBS_VALUE")
    df_terbaru_long = df_terbaru_long.rename(columns={"Row Labels": "Countries"})
    df_terbaru_long["TIME_PERIOD"] = 2015
    df_terbaru_long["UNIT_MEASURE"] = "COUNT"
    df_terbaru_long["DATA_SOURCE"] = "SPREP (2015)"
    df_terbaru_long["GEO_PICT"] = df_terbaru_long["Countries"].map(country_to_code)
    df_terbaru_long["INDICATOR"] = "MARINE_POLLUTION_" + df_terbaru_long["INDICATOR"].str.upper().str.replace(" ", "_")
    df_terbaru = df_terbaru_long[["INDICATOR", "GEO_PICT", "TIME_PERIOD", "OBS_VALUE", "UNIT_MEASURE", "DATA_SOURCE"]]

    df_all = pd.concat([df_lama, df_baru, df_terbaru], ignore_index=True)

    indicators_to_remove = ["AG_PRD_FIESMS", "ER_GRF_PLNTSTOR"]
    df_all = df_all[~df_all["INDICATOR"].isin(indicators_to_remove)]

    indicator_labels = {
        "MARINE_POLLUTION_ABANDONED": "Abandoned Waste",
        "MARINE_POLLUTION_CHEMICALS": "Chemical Pollution",
        "MARINE_POLLUTION_DUMPED": "Dumped Waste",
        "MARINE_POLLUTION_GENERAL_GARBAGE": "General Garbage",
        "MARINE_POLLUTION_LAND_BASED_SOURCE": "Land-based Sources",
        "MARINE_POLLUTION_LOST_DURING_FISHING": "Lost During Fishing",
        "MARINE_POLLUTION_METALS": "Metal Waste",
        "MARINE_POLLUTION_OIL_SPLILLAGES_AND_LEAKAGES": "Oil Spillages & Leakages",
        "MARINE_POLLUTION_OLD_FISHING_GEAR": "Old Fishing Gear",
        "MARINE_POLLUTION_PLASTICS": "Plastic Waste",
        "MARINE_POLLUTION_WASTE_OILS": "Waste Oils",
        "EN_MAR_BEALITSQ": "Mangrove Area (sq km)",
        "ER_H2O_FWTL": "Freshwater Levels",
        "ER_MRN_MARINKBA": "Marine Protected Area Coverage",
        "ER_PTD_TOT": "Total Protected Land Area",
        "ER_RSK_LST": "Species at Risk",
        "SPC_12_4_2": "Hazardous Waste Management",
        "SPC_12_5_1": "Recycling Rate",
        "SPC_14_2_1": "Sustainable Marine Management",
        "SPC_14_6_1": "Combatting Illegal, Unreported and Unregulated (IUU) Fishing",
        "SPC_14_b_1": "Small-scale Fisheries Access",
        "SPC_15_8_1": "Control of Invasive Non-native Species",
        "SPC_2_4_1": "Sustainable Agriculture Practices",
    }
    df_all["INDICATOR_LABEL"] = df_all["INDICATOR"].replace(indicator_labels)
    return df_all

df = load_data()

country_map = {
    'CK': 'Cook Islands', 'WS': 'Samoa', 'PF': 'French Polynesia', 'PG': 'Papua New Guinea',
    'MH': 'Marshall Islands', 'FJ': 'Fiji', 'VU': 'Vanuatu', 'FM': 'Micronesia (Federated States of)',
    'KI': 'Kiribati', 'NR': 'Nauru', 'PW': 'Palau', 'NU': 'Niue', 'TV': 'Tuvalu', 'TO': 'Tonga',
    'AS': 'American Samoa', 'IW': 'International Waters', 'SB': 'Solomon Islands', 'TK': 'Tokelau'
}
df['Country'] = df['GEO_PICT'].map(country_map).fillna(df['GEO_PICT'])

# Sidebar
st.sidebar.markdown("### Indicator Selection")
indicator_options = df["INDICATOR_LABEL"].dropna().unique()
selected_indicator = st.sidebar.selectbox("Select Indicator", sorted(indicator_options))

# Filter & Clean Data
filtered_df = df[df["INDICATOR_LABEL"] == selected_indicator].copy()
filtered_df = filtered_df.dropna(subset=["OBS_VALUE"])
filtered_df["OBS_VALUE"] = pd.to_numeric(filtered_df["OBS_VALUE"], errors="coerce")
filtered_df["TIME_PERIOD"] = pd.to_numeric(filtered_df["TIME_PERIOD"], errors="coerce")
filtered_df = filtered_df.dropna(subset=["TIME_PERIOD"])
filtered_df["TIME_PERIOD"] = filtered_df["TIME_PERIOD"].astype(int)

country_coords = {
    'Cook Islands': (-21.2367, -159.7777), 'Samoa': (-13.7590, -172.1046),
    'French Polynesia': (-17.6797, -149.4068), 'Papua New Guinea': (-6.314993, 143.95555),
    'Marshall Islands': (7.1315, 171.1845), 'Fiji': (-17.7134, 178.0650),
    'Vanuatu': (-15.3767, 166.9592), 'Micronesia (Federated States of)': (7.4256, 150.5508),
    'Kiribati': (1.8709, -157.3630), 'Nauru': (-0.5228, 166.9315), 'Palau': (7.5150, 134.5825),
    'Niue': (-19.0544, -169.8672), 'Tuvalu': (-7.1095, 177.6493), 'Tonga': (-21.1789, -175.1982),
    'American Samoa': (-14.2710, -170.1322), 'Solomon Islands': (-9.6457, 160.1562), 'Tokelau': (-9.2002, -171.8484),
    'International Waters': (-10.0, 160.0)
}

st.title("🌊 Pacific Marine Pollution Dashboard")
st.markdown(f"### Indicator: {selected_indicator}")

# Prepare Map
latest_df = filtered_df.sort_values("TIME_PERIOD").groupby("Country").tail(1)
latest_df["lat"] = latest_df["Country"].map(lambda x: country_coords.get(x, (None, None))[0])
latest_df["lon"] = latest_df["Country"].map(lambda x: country_coords.get(x, (None, None))[1])
latest_df = latest_df.dropna(subset=["lat", "lon", "OBS_VALUE"])

# Prepare Trend Plot
trend_plot = (
    filtered_df.groupby(["Country", "TIME_PERIOD"])["OBS_VALUE"]
    .mean().reset_index()
)
country_counts = trend_plot["Country"].value_counts()
country_has_single = country_counts[country_counts == 1].index.tolist()
country_has_multi = country_counts[country_counts > 1].index.tolist()
df_line = trend_plot[trend_plot["Country"].isin(country_has_multi)]
df_point = trend_plot[trend_plot["Country"].isin(country_has_single)]

fig_map = px.scatter_mapbox(
    latest_df, lat="lat", lon="lon", size="OBS_VALUE", color="OBS_VALUE",
    color_continuous_scale=["#E74C3C", "#FADA7A", "#27AE60"], size_max=60, zoom=2,
    hover_name="Country", hover_data={"OBS_VALUE": ':.2f', "lat": False, "lon": False},
    labels={"OBS_VALUE": selected_indicator}, height=450
)
fig_map.update_layout(mapbox_style="open-street-map", margin={"r":0,"t":0,"l":0,"b":0})
fig_map.update_traces(marker=dict(sizemode="area", opacity=0.8))

fig_trend = px.line(
    df_line, x="TIME_PERIOD", y="OBS_VALUE", color="Country",
    labels={"TIME_PERIOD": "Year", "OBS_VALUE": selected_indicator},
    title=""
)
if not df_point.empty:
    fig_point = px.scatter(
        df_point,
        x="TIME_PERIOD",
        y="OBS_VALUE",
        color="Country",
        hover_name="Country",
        labels={"TIME_PERIOD": "Year", "OBS_VALUE": selected_indicator}
    )
    for trace in fig_point.data:
        fig_trend.add_trace(trace)

fig_trend.update_layout(legend_title_text="Country", height=450)

# Layout: 2 Kolom Baris Atas
col1, col2 = st.columns(2)
with col1:
    st.metric("Average Value (Latest Year)", f"{latest_df['OBS_VALUE'].mean():.2f}")
    st.plotly_chart(fig_map, use_container_width=True)

with col2:
    st.markdown("### 📈 Indicator Trend Over Time")
    st.plotly_chart(fig_trend, use_container_width=True)

# --- Baris Bawah: Dominan dan Perbandingan
marine_df = df[df["INDICATOR"].str.startswith("MARINE_POLLUTION")].copy()
marine_df["OBS_VALUE"] = pd.to_numeric(marine_df["OBS_VALUE"], errors="coerce")
latest_pollution = marine_df.dropna(subset=["OBS_VALUE"]).sort_values("TIME_PERIOD").groupby(["Country", "INDICATOR_LABEL"]).tail(1)
dominant_pollution = latest_pollution.groupby("Country").apply(lambda x: x.loc[x["OBS_VALUE"].idxmax()]).reset_index(drop=True)

fig_dominant = px.bar(
    dominant_pollution.sort_values("OBS_VALUE", ascending=False),
    x="Country", y="OBS_VALUE", color="INDICATOR_LABEL",
    labels={"OBS_VALUE": "Pollution Level", "INDICATOR_LABEL": "Pollution Type"},
    title=""
)

plastik = df[df["INDICATOR_LABEL"] == "Plastic Waste"]
lindung = df[df["INDICATOR_LABEL"] == "Marine Protected Area Coverage"]
merged_env = pd.merge(
    plastik[["Country", "TIME_PERIOD", "OBS_VALUE"]],
    lindung[["Country", "TIME_PERIOD", "OBS_VALUE"]],
    on=["Country", "TIME_PERIOD"], suffixes=("_PLASTIC", "_MPA")
).dropna()

fig_plastic_vs_protect = px.scatter(
    merged_env, x="OBS_VALUE_MPA", y="OBS_VALUE_PLASTIC", hover_name="Country",
    labels={"OBS_VALUE_PLASTIC": "Plastic Pollution", "OBS_VALUE_MPA": "Protected Area Coverage"},
    title=""
)
fig_plastic_vs_protect.update_traces(marker=dict(size=12, opacity=0.7, color="#2980B9"))

col3, col4 = st.columns(2)
with col3:
    st.markdown("### 🌐 Dominant Type of Marine Pollution by Country")
    st.plotly_chart(fig_dominant, use_container_width=True)

with col4:
    st.markdown("### 🛡 Marine Pollution vs. Environmental Protection Efforts")
    st.plotly_chart(fig_plastic_vs_protect, use_container_width=True)

# --- Risiko Lingkungan Tinggi
st.markdown("### ⚠ High-Risk Ocean Areas (High Pollution, Low Protection)")
merged_env["Risk_Score"] = merged_env["OBS_VALUE_PLASTIC"] / (merged_env["OBS_VALUE_MPA"] + 1)
merged_env["lat"] = merged_env["Country"].map(lambda x: country_coords.get(x, (None, None))[0])
merged_env["lon"] = merged_env["Country"].map(lambda x: country_coords.get(x, (None, None))[1])
merged_env = merged_env.dropna(subset=["lat", "lon"])

fig_risk_map = px.scatter_mapbox(
    merged_env, lat="lat", lon="lon", size="Risk_Score", color="Risk_Score",
    color_continuous_scale="Reds", size_max=50,
    hover_name="Country", labels={"Risk_Score": "Environmental Risk Score"},
    zoom=2, height=500
)
fig_risk_map.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig_risk_map, use_container_width=True)
