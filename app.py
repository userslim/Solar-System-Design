import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64

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

# ---- SYSTEM VOLTAGE (for battery bank) ----
if num_batteries <= 2:
    sys_voltage = 12
    series_strings = 1
    parallel_groups = num_batteries
elif num_batteries <= 8:
    sys_voltage = 24
    parallel_groups = math.ceil(num_batteries / 2)
    series_strings = 2
else:
    sys_voltage = 48
    parallel_groups = math.ceil(num_batteries / 4)
    series_strings = 4

# Inverter DC input current
inverter_dc_current = inverter_continuous_w / (sys_voltage * 0.85)

# Battery interconnect current
if parallel_groups > 1:
    battery_interconnect_current = inverter_dc_current / parallel_groups
else:
    battery_interconnect_current = inverter_dc_current

# Solar array current (simplified)
solar_array_current = solar_array_w / sys_voltage

# ---- CABLE SIZING FUNCTION ----
def recommend_cable_size(current_amps, voltage, distance_ft, is_dc=True):
    max_vdrop_pct = 0.03 if is_dc else 0.02
    max_vdrop = voltage * max_vdrop_pct
    round_trip_ft = distance_ft * 2
    
    awg_resistance = {
        0: 0.0983, 1: 0.1239, 2: 0.1563, 3: 0.1970, 4: 0.2485,
        6: 0.3951, 8: 0.6282, 10: 0.9989, 12: 1.588, 14: 2.525,
        16: 4.016, 18: 6.385, 20: 10.15
    }
    ampacity = {0: 170, 1: 145, 2: 130, 3: 115, 4: 100,
                6: 80, 8: 65, 10: 50, 12: 35, 14: 25,
                16: 18, 18: 14, 20: 11}
    
    for awg, r_per_1000ft in sorted(awg_resistance.items(), key=lambda x: x[0]):
        total_resistance = (r_per_1000ft / 1000) * round_trip_ft
        vdrop = current_amps * total_resistance
        if vdrop <= max_vdrop and current_amps <= ampacity.get(awg, 0):
            return f"{awg} AWG" if awg <= 0 else f"{awg} AWG"
    return "10 AWG (minimum - check NEC)"

# ---- DRAW CONNECTION DIAGRAM ----
def draw_system_diagram(num_panels, sys_voltage, parallel_groups, inverter_continuous_w, battery_type):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Component positions (x, y)
    panels_pos = (2, 4.5)
    charge_ctrl_pos = (5, 4.5)
    battery_pos = (8, 3)
    inverter_pos = (5, 1.5)
    load_pos = (2, 1.5)
    
    # Draw boxes
    def draw_box(x, y, width, height, text, color='lightblue'):
        rect = patches.Rectangle((x-width/2, y-height/2), width, height, 
                                 linewidth=2, edgecolor='black', facecolor=color)
        ax.add_patch(rect)
        ax.text(x, y, text, ha='center', va='center', fontsize=10, fontweight='bold')
    
    draw_box(panels_pos[0], panels_pos[1], 2.0, 1.0, f"{num_panels}x 400W\nSolar Panels", 'lightgreen')
    draw_box(charge_ctrl_pos[0], charge_ctrl_pos[1], 2.0, 1.0, "MPPT\nCharge Controller", 'lightyellow')
    draw_box(battery_pos[0], battery_pos[1], 2.2, 1.2, f"{parallel_groups} Parallel Strings\n{series_strings} in series\n{num_batteries} x 100Ah ({battery_type})", 'lightcoral')
    draw_box(inverter_pos[0], inverter_pos[1], 2.0, 1.0, f"Inverter\n{inverter_continuous_w}W\nPure Sine Wave", 'lightcyan')
    draw_box(load_pos[0], load_pos[1], 2.0, 1.0, "AC Load Panel\n& Appliances", 'lightgray')
    
    # Arrows and labels
    # Panels -> Charge controller
    ax.annotate('', xy=(charge_ctrl_pos[0]-1, charge_ctrl_pos[1]), xytext=(panels_pos[0]+1, panels_pos[1]),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(3.5, 4.7, "PV Wire (MC4)", ha='center', fontsize=8, rotation=0)
    
    # Charge controller -> Battery
    ax.annotate('', xy=(battery_pos[0]-1.2, battery_pos[1]), xytext=(charge_ctrl_pos[0]+1, charge_ctrl_pos[1]),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(6.8, 4.2, f"{sys_voltage}V DC\nBattery Cable", ha='center', fontsize=8)
    
    # Battery -> Inverter
    ax.annotate('', xy=(inverter_pos[0]+1.2, inverter_pos[1]), xytext=(battery_pos[0]-1.2, battery_pos[1]),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(6.8, 2.2, f"{sys_voltage}V DC\nHeavy Cable + Fuse", ha='center', fontsize=8)
    
    # Inverter -> Load
    ax.annotate('', xy=(load_pos[0]+1, load_pos[1]), xytext=(inverter_pos[0]-1, inverter_pos[1]),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    ax.text(3.5, 1.5, "120V AC\nRomex/THHN", ha='center', fontsize=8)
    
    # Add grounding and fuse notes
    ax.text(9, 0.5, "⚠️ Grounding Rod\n& AC/DC Disconnects\nRequired", fontsize=8, 
            bbox=dict(facecolor='white', edgecolor='red'), ha='center')
    
    plt.title("DIY Solar System Connection Diagram (Simplified)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    return fig

# ---- MAIN UI ----
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
       *Configuration*: **{sys_voltage}V** system – {series_strings} in series, {parallel_groups} parallel strings  
    
    2. **Solar Panels**: {num_panels} × {panel_watt}W monocrystalline  
    
    3. **Charge Controller**: MPPT {solar_array_w:.0f}W / {sys_voltage}V  
    
    4. **Inverter**: {inverter_continuous_w}W pure sine wave  
    """)

# ---- DIAGRAM SECTION ----
st.markdown("---")
st.header("🔗 System Connection Diagram")
st.markdown("The diagram below shows how all components are connected. Cable types and sizes are noted.")

fig = draw_system_diagram(num_panels, sys_voltage, parallel_groups, inverter_continuous_w, battery_type.split()[0])
st.pyplot(fig)

# ---- CABLE SIZING DETAILS ----
st.markdown("---")
st.header("🔌 Detailed Cable & Wiring Recommendations")

cable_info = []

# Battery to inverter
cable_info.append({
    "Run": f"Battery Bank → Inverter ({sys_voltage}V DC)",
    "Current": f"{inverter_dc_current:.1f} A",
    "Length (ft)": battery_cable_length,
    "Size": recommend_cable_size(inverter_dc_current, sys_voltage, battery_cable_length, is_dc=True),
    "Type": "Welding / UL battery cable (fine stranded, 105°C)",
    "Accessories": "Class T fuse (1.25x current), hydraulic lugs"
})

# Battery interconnects
if parallel_groups > 1:
    cable_info.append({
        "Run": "Battery parallel interconnects (string to busbar)",
        "Current": f"{battery_interconnect_current:.1f} A",
        "Length (ft)": 3.0,
        "Size": recommend_cable_size(battery_interconnect_current, sys_voltage, 3.0, is_dc=True),
        "Type": "Same as above",
        "Accessories": "Fuse per string (optional)"
    })

# Solar PV
solar_distance = st.slider("Solar array to controller distance (ft)", 10, 150, 30, key="solar_dist")
solar_voc_estimate = num_panels * 37  # rough
solar_current_imp = solar_array_w / max(1, solar_voc_estimate)
cable_info.append({
    "Run": "Solar panels → Charge Controller (DC, PV)",
    "Current": f"{solar_current_imp:.1f} A",
    "Length (ft)": solar_distance,
    "Size": recommend_cable_size(solar_current_imp, 48, solar_distance, is_dc=True),
    "Type": "PV wire (UV resistant, MC4 connectors)",
    "Accessories": "DC breaker / PV disconnect"
})

# AC output
ac_current = inverter_continuous_w / 120
cable_info.append({
    "Run": "Inverter → AC Load Panel (120V AC)",
    "Current": f"{ac_current:.1f} A",
    "Length (ft)": 10.0,
    "Size": recommend_cable_size(ac_current, 120, 10.0, is_dc=False),
    "Type": "THHN/THWN-2 or NM-B (Romex), copper",
    "Accessories": "Main AC breaker, GFCI"
})

for c in cable_info:
    with st.expander(f"📏 {c['Run']} – {c['Current']}"):
        st.markdown(f"""
        - **Recommended size**: **{c['Size']}**  
        - **Cable type**: {c['Type']}  
        - **Accessories**: {c['Accessories']}  
        - *One-way distance*: {c['Length (ft)']} ft
        """)

# ---- OFF-THE-SHELF ALTERNATIVES ----
st.markdown("---")
st.header("📦 Off-the-shelf Alternatives (EcoFlow / DJI)")

capacity_wh = daily_energy_wh
alternatives = []
if capacity_wh <= 1024:
    alternatives = [("EcoFlow RIVER 2 Pro", "1024 Wh, 1800W", "~$499"),
                    ("DJI Power 1000", "1024 Wh, 2200W", "~$499")]
elif capacity_wh <= 2048:
    alternatives = [("EcoFlow DELTA 2 Max", "2048 Wh, 2400W", "~$1599"),
                    ("DJI Power 1000 (x2)", "2048 Wh total", "~$1000+")]
elif capacity_wh <= 3600:
    alternatives = [("EcoFlow DELTA Pro", "3600 Wh, 3600W", "~$2999"),
                    ("DJI Power 1000 + extra batt", "2048 Wh", "~$1249")]
elif capacity_wh <= 7200:
    alternatives = [("EcoFlow DELTA Pro + Extra Batt", "7200 Wh", "~$4798"),
                    ("EcoFlow DELTA Pro Ultra", "6100 Wh, 7200W", "~$5699")]
else:
    alternatives = [("EcoFlow DELTA Pro Ultra stack", ">10 kWh", "Contact dealer"),
                    ("DJI custom config", "Multiple units", "Variable")]

st.markdown(f"Based on {capacity_wh:.0f} Wh daily requirement:")
for name, specs, price in alternatives:
    with st.expander(f"**{name}** – {specs}"):
        st.markdown(f"**Price**: {price}\n\nPlug & play, solar ready.")

# ---- SUMMARY ----
st.markdown("---")
st.header("📊 Summary: DIY vs. Off-the-shelf")
colA, colB = st.columns(2)
with colA:
    st.subheader("DIY System")
    st.markdown(f"- Batteries: {num_batteries}×100Ah → {num_batteries*1200/1000:.1f} kWh\n- Solar: {num_panels}×{panel_watt}W\n- Inverter: {inverter_continuous_w}W\n- Estimated cost: ~${num_batteries*150 + num_panels*200 + inverter_continuous_w*0.5:.0f}")
with colB:
    st.subheader("Off-the-shelf")
    st.markdown(f"- Model: {alternatives[0][0]}\n- Capacity: {alternatives[0][1]}\n- Pros: Portable, no wiring\n- Cons: Higher $/Wh, limited expansion")

st.info("🔧 **Note**: All numbers are estimates. For 24/7 critical loads, add 30% more battery capacity. Always follow local electrical codes and consult a licensed electrician.")
