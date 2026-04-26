import streamlit as st
import math

# Page config
st.set_page_config(page_title="Solar System Designer", layout="wide")

# Title and description
st.title("☀️ Solar System Designer – 24/7 Operation")
st.markdown("""
This tool helps you design a **DIY solar system** that runs your appliances **24 hours a day**, 
calculates the number of **100Ah batteries** needed, and suggests **off-the-shelf alternatives** (EcoFlow/DJI).
""")

# Sidebar for inputs
with st.sidebar:
    st.header("⚙️ System Parameters")
    wattage = st.number_input(
        "Total appliance power (Watts)",
        min_value=0.0,
        max_value=20000.0,
        value=500.0,
        step=50.0,
        help="Sum of all devices you want to run continuously for 24 hours."
    )
    
    battery_type = st.selectbox(
        "Battery chemistry",
        ["Lithium (LiFePO₄)", "Lead Acid (AGM/Gel)"],
        help="Lithium allows deeper discharge (80% DoD), Lead Acid only 50%."
    )
    
    peak_sun_hours = st.slider(
        "Average daily peak sun hours",
        min_value=1.0,
        max_value=6.0,
        value=4.0,
        step=0.5,
        help="For most locations: 3.5–5.5 hours."
    )
    
    inverter_efficiency = 0.90  # fixed 90%
    st.caption("🔧 Inverter efficiency assumed: 90%")

if wattage <= 0:
    st.warning("⚠️ Please enter a wattage greater than 0.")
    st.stop()

# ---- CALCULATIONS ----
daily_energy_wh = wattage * 24  # Wh per day
required_battery_wh = daily_energy_wh / inverter_efficiency  # after inverter losses

# Battery usable capacity (12V * 100Ah = 1200Wh per battery)
if battery_type == "Lithium (LiFePO₄)":
    dod = 0.80  # Depth of Discharge
    battery_usable_wh = 1200 * dod
else:
    dod = 0.50
    battery_usable_wh = 1200 * dod

num_batteries = math.ceil(required_battery_wh / battery_usable_wh)

# Solar array sizing (compensates daily consumption & system losses)
solar_loss_factor = 1.2
required_solar_wh = daily_energy_wh * solar_loss_factor
solar_array_w = required_solar_wh / peak_sun_hours
panel_watt = 400  # standard panel power
num_panels = math.ceil(solar_array_w / panel_watt)

# Inverter sizing (continuous + 25% headroom)
inverter_continuous_w = math.ceil(wattage * 1.25)

# ---- MAIN DISPLAY ----
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
    st.caption("Plus surge capacity (2–3x for motor loads)")

with col2:
    st.subheader("📋 DIY Solar System Setup")
    st.markdown(f"""
    **To run {wattage:.0f}W appliances 24/7 you need:**

    1. **Battery Bank**:  
       {num_batteries} × 100Ah (12V) {battery_type.split()[0]} batteries  
       *Configuration example*:  
       - For 12V system: all in parallel  
       - For 24V: 2 in series, {math.ceil(num_batteries/2)} parallel strings  
       - For 48V: 4 in series, {math.ceil(num_batteries/4)} parallel strings  
       (Requires Busbars / Fuses / BMS for Lithium)

    2. **Solar Panels**:  
       {num_panels} × {panel_watt}W monocrystalline panels  
       Mounting structure, MC4 cables, combiner box.

    3. **Charge Controller**:  
       MPPT type, rated for {solar_array_w:.0f}W / system voltage.  
       Example: Victron SmartSolar 150/70 or Epever Tracer.

    4. **Inverter**:  
       Pure sine wave, {inverter_continuous_w}W continuous, low-frequency recommended.

    5. **Cables & Protection**:  
       Appropriate gauge battery cables, breakers/fuses, busbars.

    ✅ **24/7 operation** – The solar array should generate enough energy daily to fully recharge the batteries, even after losses.
    """)

# ---- OFF-THE-SHELF ALTERNATIVES ----
st.markdown("---")
st.header("📦 Off-the-shelf Alternatives (EcoFlow / DJI)")

# Define models based on required capacity (Wh)
capacity_wh = daily_energy_wh

alternatives = []

# EcoFlow models
if capacity_wh <= 1024:
    alternatives.append(("EcoFlow RIVER 2 Pro", "1024 Wh, 1800W output", "~$499"))
    alternatives.append(("DJI Power 1000", "1024 Wh, 2200W output", "~$499"))
elif capacity_wh <= 2048:
    alternatives.append(("EcoFlow DELTA 2 Max", "2048 Wh, 2400W output", "~$1599"))
    alternatives.append(("DJI Power 1000 (x2 + adapter)", "Expandable to 2048 Wh", "~$1000+"))
elif capacity_wh <= 3600:
    alternatives.append(("EcoFlow DELTA Pro", "3600 Wh, 3600W output", "~$2999"))
    alternatives.append(("DJI Power 1000 + extra battery", "2048 Wh (combo)", "~$1249"))
elif capacity_wh <= 7200:
    alternatives.append(("EcoFlow DELTA Pro + Extra Battery", "7200 Wh total", "~$4798"))
    alternatives.append(("EcoFlow DELTA Pro Ultra (1 stack)", "6100 Wh, 7200W", "~$5699"))
else:
    alternatives.append(("EcoFlow DELTA Pro Ultra (multiple stacks)", "Customizable > 10 kWh", "Contact dealer"))
    alternatives.append(("DJI Power Expansion" + " high capacity", "Multiple units parallel", "Variable"))

# Display as a table
st.markdown("Based on your required **{:.0f} Wh** per day (continuous load):".format(capacity_wh))
for name, specs, price in alternatives[:3]:
    with st.expander(f"**{name}** – {specs}"):
        st.markdown(f"""
        - **Usable capacity**: {specs.split(',')[0]}
        - **Price**: {price} (approx.)
        - **Plug & play**: No wiring, solar ready, built-in inverter
        """)

st.caption("💡 For larger needs, consider expandable systems (EcoFlow Smart Generator or multi-unit parallel).")

# ---- SUMMARY COMPARISON ----
st.markdown("---")
st.header("📊 Summary: DIY vs. Off-the-shelf")

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("DIY Solar System")
    st.markdown(f"""
    - **Batteries**: {num_batteries} × 100Ah → ~{num_batteries*1200/1000:.1f} kWh nominal  
    - **Solar**: {num_panels} × {panel_watt}W ≈ {solar_array_w:.0f}W array  
    - **Inverter**: {inverter_continuous_w}W pure sine wave  
    - **Pros**: Fully scalable, replaceable parts, often lower long-term cost  
    - **Cons**: Requires electrical knowledge, assembly, maintenance  
    - **Estimated DIY cost** (rough): ~${num_batteries*150 + num_panels*200 + inverter_continuous_w*0.5:.0f}
    """)

with col_b:
    st.subheader("Off-the-shelf (EcoFlow/DJI)")
    st.markdown(f"""
    - **Typical model**: {alternatives[0][0]} ({alternatives[0][1].split(',')[0]})  
    - **Pros**: No wiring, portable, app control, expandable batteries  
    - **Cons**: Higher cost per Wh, limited expansion beyond add-on batteries  
    - **Best for**: Lower wattage (<1500W) or backup/mobile use  
    - **24/7 runtime**: May need extra battery packs or solar panels (sold separately)
    """)

st.markdown("---")
st.info("🔧 **Note**: All numbers are estimates. For critical 24/7 operation, add 20-30% extra battery capacity and consider 2+ days of autonomy. Consult a certified solar installer for final design.")
