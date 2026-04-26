import streamlit as st

# --- CONFIGURATION & MOCK LOGIC ---
# (In a real app, these would come from user inputs or a calculator engine)
st.set_page_config(page_title="Solar Design Tool", layout="wide")

# Placeholder Inputs (Replace these with your actual logic/sliders)
wattage = 500.0
daily_energy_wh = wattage * 24
dod = 0.8  # Depth of Discharge
battery_type = "LiFePO4"
sys_voltage = 12
panel_watt = 400
num_panels = 4
solar_array_w = num_panels * panel_watt
num_batteries = 4
battery_usable_wh = (num_batteries * 100 * 12) * dod
inverter_continuous_w = 2000
series_strings = 1
parallel_groups = 4
inverter_dc_current = inverter_continuous_w / sys_voltage
battery_cable_length = 5
battery_interconnect_current = 100
ac_current = inverter_continuous_w / 120

def draw_system_diagram():
    st.info("🎨 [System Diagram Placeholder] - You can use st.graphviz_chart() here later.")

def recommend_cable_size(amps, volts, length, is_dc=True):
    # Simple logic for demonstration
    if amps > 100: return "2/0 AWG"
    if amps > 50: return "4 AWG"
    return "10 AWG"

# ---- MAIN UI ----
st.title("☀️ Off-Grid Solar System Designer")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔋 Battery Bank (100Ah / 12V)")
    st.metric("Number of 100Ah batteries required", f"{num_batteries} pcs")
    st.caption(f"Each provides {battery_usable_wh:.0f} Wh usable ({dod*100:.0f}% DoD)")
    
    st.subheader("☀️ Solar Array (400W panels)")
    st.metric("Total array size", f"{solar_array_w:.0f} W")
    st.metric("Number of 400W panels", f"{num_panels} panels")
    
    st.subheader("⚡ Inverter")
    st.metric("Continuous power rating", f"{inverter_continuous_w} W")
    st.caption("Plus surge capacity (2-3x for motor loads)")

with col2:
    st.subheader("📋 DIY Solar System Setup")
    # RE-TYPED LINE TO PREVENT SYNTAX ERROR
    summary_text = f"""
**To run {wattage:.0f}W appliances 24/7 you need:**

1. **Battery Bank**: {num_batteries} x 100Ah {battery_type}  
   **Configuration**: {sys_voltage}V system - {series_strings} in series, {parallel_groups} parallel strings

2. **Solar Panels**: {num_panels} x {panel_watt}W monocrystalline

3. **Charge Controller**: MPPT rated for {solar_array_w:.0f}W / {sys_voltage}V

4. **Inverter**: {inverter_continuous_w}W pure sine wave

5. **Cables & Protection**: See diagram and table below.
"""
    st.markdown(summary_text)

draw_system_diagram()

# ---- DETAILED CABLE TABLE ----
st.markdown("---")
st.header("🔌 Detailed Cable & Wiring Recommendations")

cable_info = [
    {
        "Run": f"Battery Bank -> Inverter ({sys_voltage}V DC)",
        "Current": f"{inverter_dc_current:.1f} A",
        "Length": f"{battery_cable_length} ft",
        "Size": recommend_cable_size(inverter_dc_current, sys_voltage, battery_cable_length, is_dc=True),
        "Type": "Welding / UL battery cable (fine stranded, 105C)",
        "Accessories": "Class T fuse (1.25x current), hydraulic lugs"
    }
]

if parallel_groups > 1:
    cable_info.append({
        "Run": "Battery parallel interconnects (string to busbar)",
        "Current": f"{battery_interconnect_current:.1f} A",
        "Length": "3 ft",
        "Size": recommend_cable_size(battery_interconnect_current, sys_voltage, 3, is_dc=True),
        "Type": "Same as above",
        "Accessories": "Fuse per string (optional)"
    })

solar_distance = st.slider("Solar array to controller distance (ft)", 10, 150, 30, key="solar_dist")
solar_voc_estimate = num_panels * 37
solar_current_imp = solar_array_w / max(1, solar_voc_estimate)

cable_info.append({
    "Run": "Solar panels -> Charge Controller (DC, PV)",
    "Current": f"{solar_current_imp:.1f} A",
    "Length": f"{solar_distance} ft",
    "Size": recommend_cable_size(solar_current_imp, 48, solar_distance, is_dc=True),
    "Type": "PV wire (UV resistant, MC4 connectors)",
    "Accessories": "DC breaker / PV disconnect"
})

cable_info.append({
    "Run": "Inverter -> AC Load Panel (120V AC)",
    "Current": f"{ac_current:.1f} A",
    "Length": "10 ft",
    "Size": recommend_cable_size(ac_current, 120, 10, is_dc=False),
    "Type": "THHN/THWN-2 or NM-B (Romex), copper",
    "Accessories": "Main AC breaker, GFCI"
})

for c in cable_info:
    with st.expander(f"📏 {c['Run']} - {c['Current']}"):
        st.markdown(f"""
- **Recommended size**: **{c['Size']}** - **Cable type**: {c['Type']}  
- **Accessories**: {c['Accessories']}  
- *One-way distance*: {c['Length']}
""")

# ---- OFF-THE-SHELF ALTERNATIVES ----
st.markdown("---")
st.header("📦 Off-the-shelf Alternatives (EcoFlow / DJI)")

capacity_wh = daily_energy_wh
if capacity_wh <= 1024:
    alternatives = [("EcoFlow RIVER 2 Pro", "1024 Wh, 1800W", "$499")]
elif capacity_wh <= 3600:
    alternatives = [("EcoFlow DELTA Pro", "3600 Wh, 3600W", "$2999")]
else:
    alternatives = [("EcoFlow DELTA Pro Ultra", "6100 Wh, 7200W", "$5699")]

st.markdown(f"Based on your required **{capacity_wh:.0f} Wh** per day:")
for name, specs, price in alternatives:
    with st.expander(f"**{name}** - {specs}"):
        st.markdown(f"- **Price**: {price} (approx.)\n- **Plug & play**: Built-in inverter.")

st.markdown("---")
st.info("🔧 **Note**: All numbers are estimates. Always consult a licensed electrician.")
