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
    
    # Additional cable parameters
    st.subheader("🔌 Cable length (one-way)")
    battery_cable_length = st.number_input(
        "Distance from battery to inverter (ft)",
        min_value=1.0,
        max_value=50.0,
        value=5.0,
        step=1.0,
        help="Longer distances require thicker cable to reduce voltage drop."
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

# ---- CABLE SIZING FUNCTION ----
def recommend_cable_size(current_amps, voltage, distance_ft, is_dc=True):
    """
    Recommends AWG cable size for given current, voltage, distance (one-way).
    Based on 3% voltage drop for DC, 2% for AC.
    """
    # Voltage drop limit
    if is_dc:
        max_vdrop_pct = 0.03
    else:
        max_vdrop_pct = 0.02
    
    max_vdrop = voltage * max_vdrop_pct
    # Round trip distance (2 * one-way)
    round_trip_ft = distance_ft * 2
    
    # Approximate resistance per 1000 ft for different AWG (ohms)
    awg_resistance = {
        0: 0.0983, 1: 0.1239, 2: 0.1563, 3: 0.1970, 4: 0.2485,
        6: 0.3951, 8: 0.6282, 10: 0.9989, 12: 1.588, 14: 2.525,
        16: 4.016, 18: 6.385, 20: 10.15
    }
    
    # Find smallest AWG that meets voltage drop
    for awg, r_per_1000ft in sorted(awg_resistance.items(), key=lambda x: x[0]):  # lower AWG = thicker
        total_resistance = (r_per_1000ft / 1000) * round_trip_ft
        vdrop = current_amps * total_resistance
        if vdrop <= max_vdrop:
            # Also ampacity check (typical copper 90°C)
            ampacity = {
                0: 170, 1: 145, 2: 130, 3: 115, 4: 100,
                6: 80, 8: 65, 10: 50, 12: 35, 14: 25,
                16: 18, 18: 14, 20: 11
            }
            if current_amps <= ampacity.get(awg, 0):
                return f"{awg} AWG" if awg <= 0 else f"{awg} AWG"
    return "14 AWG (minimal load under 10A) or consult NEC"

# ---- SYSTEM VOLTAGE (for battery bank) ----
# For simplicity, we assume system voltage = 12V for up to 2 batteries, 24V for 3-8, 48V for 9+
if num_batteries <= 2:
    sys_voltage = 12
    series_strings = 1
    parallel_groups = num_batteries
elif num_batteries <= 8:
    sys_voltage = 24
    # 2 batteries in series, rest in parallel
    parallel_groups = math.ceil(num_batteries / 2)
    series_strings = 2
else:
    sys_voltage = 48
    parallel_groups = math.ceil(num_batteries / 4)
    series_strings = 4

# Inverter DC input current
inverter_dc_current = inverter_continuous_w / (sys_voltage * 0.85)  # 85% efficiency factor for worse case

# Battery interconnect current (parallel string current)
if parallel_groups > 1:
    battery_interconnect_current = inverter_dc_current / parallel_groups
else:
    battery_interconnect_current = inverter_dc_current

# Solar array current (assuming system voltage and MPPT controller)
solar_array_current = solar_array_w / sys_voltage

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
       *Configuration*:  
       - System Voltage: **{sys_voltage}V**  
       - Series strings: {series_strings} batteries in series  
       - Parallel strings: {parallel_groups} strings  
       (*Requires Busbars / Fuses / BMS for Lithium*)

    2. **Solar Panels**:  
       {num_panels} × {panel_watt}W monocrystalline panels  
       Mounting structure, MC4 cables, combiner box.

    3. **Charge Controller**:  
       MPPT type, rated for {solar_array_w:.0f}W / {sys_voltage}V.  
       Example: Victron SmartSolar 150/70 or Epever Tracer.

    4. **Inverter**:  
       Pure sine wave, {inverter_continuous_w}W continuous, low-frequency recommended.

    ✅ **24/7 operation** – The solar array should generate enough energy daily.
    """)

# ---- CABLE SIZING DETAILS ----
st.markdown("---")
st.header("🔌 Recommended Cables & Sizes (NEC-compliant)")

# Different cable runs
cable_info = []

# Battery to inverter cable
cable_info.append({
    "Run": f"Battery Bank → Inverter ({sys_voltage}V DC)",
    "Current (A)": f"{inverter_dc_current:.1f} A",
    "Length (ft)": battery_cable_length,
    "Recommended size": recommend_cable_size(inverter_dc_current, sys_voltage, battery_cable_length, is_dc=True),
    "Cable type": "Welding cable / UL listed battery cable (fine stranded, 105°C)",
    "Accessories": "ANL or Class T fuse (1.25x current rating), hydraulic crimp lugs"
})

# Battery interconnect cables (parallel strings)
if parallel_groups > 1:
    cable_info.append({
        "Run": "Battery parallel interconnects (string to busbar)",
        "Current (A)": f"{battery_interconnect_current:.1f} A",
        "Length (ft)": 3.0,
        "Recommended size": recommend_cable_size(battery_interconnect_current, sys_voltage, 3.0, is_dc=True),
        "Cable type": "Same as above",
        "Accessories": "50A-200A rated fuse per parallel string (optional but recommended)"
    })

# Solar panel to charge controller (PV cable)
solar_distance = st.slider("Solar array to controller distance (ft)", 10, 150, 30, key="solar_dist")
solar_voc = num_panels * 37  # typical 400W panel Voc ~37V, series/parallel simplified
solar_current_imp = (solar_array_w / solar_voc) if solar_voc > 0 else 10
cable_info.append({
    "Run": "Solar panels → Charge Controller (DC, PV)",
    "Current (A)": f"{solar_current_imp:.1f} A",
    "Length (ft)": solar_distance,
    "Recommended size": recommend_cable_size(solar_current_imp, 48, solar_distance, is_dc=True),
    "Cable type": "PV wire (UV resistant, dual-insulated, MC4 connectors)",
    "Accessories": "DC breakers (or PV disconnect), lightning arrestor"
})

# Inverter AC output to load center
ac_current = inverter_continuous_w / 120  # assuming 120V AC
cable_info.append({
    "Run": "Inverter → Main AC Load Panel (120V AC)",
    "Current (A)": f"{ac_current:.1f} A",
    "Length (ft)": 10.0,
    "Recommended size": recommend_cable_size(ac_current, 120, 10.0, is_dc=False),
    "Cable type": "THHN/THWN-2 or NM-B (Romex), copper",
    "Accessories": "Main AC breaker (sized per inverter output), GFCI protection"
})

# Display cable table
st.markdown("**Cable Sizing Chart** (3% voltage drop for DC, 2% for AC, copper 90°C assumed)")
for c in cable_info:
    with st.expander(f"📏 {c['Run']} – {c['Current (A)']}"):
        st.markdown(f"""
        - **Recommended size**: **{c['Recommended size']}**  
        - **Cable type**: {c['Cable type']}  
        - **Accessories / Fusing**: {c['Accessories']}  
        - *Distance*: {c['Length (ft)']} ft one-way
        """)

st.caption("💡 Always round up to next thicker size if between AWG, and use proper lugs & torque specs. For long runs (>50ft), consider increasing voltage or using 2AWG or thicker.")

# ---- OFF-THE-SHELF ALTERNATIVES ----
st.markdown("---")
st.header("📦 Off-the-shelf Alternatives (EcoFlow / DJI)")

capacity_wh = daily_energy_wh
alternatives = []

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
    alternatives.append(("DJI Power Expansion high capacity", "Multiple units parallel", "Variable"))

st.markdown(f"Based on your required **{capacity_wh:.0f} Wh** per day (continuous load):")
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
    - **Cables**: As per chart above (includes battery, PV, AC)  
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
st.info("🔧 **Note**: All numbers are estimates. For critical 24/7 operation, add 20-30% extra battery capacity and consider 2+ days of autonomy. Always consult a licensed electrician for final installation, especially for high-current DC circuits.")
