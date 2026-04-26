import streamlit as st
import math

st.set_page_config(page_title="Solar Design Tool", layout="wide")

# --- Sidebar inputs ---
with st.sidebar:
    st.header("⚙️ System Parameters")
    total_wattage = st.number_input("Total appliance power (Watts)", min_value=0, value=500, step=50, help="Sum of all devices you want to run.")
    runtime_hours = st.number_input("Hours to run per day", min_value=1, max_value=24, value=24, step=1, help="Usually 24 for continuous operation.")
    battery_type = st.selectbox("Battery Type", ["LiFePO4 (Lithium)", "AGM/Lead Acid"])
    sun_hours = st.slider("Peak Sun Hours per Day", 1.0, 8.0, 4.5)
    sys_voltage = st.selectbox("System Voltage (DC)", [12, 24, 48], index=0, help="Recommended: 12V for <2kWh/day, 24V for 2-5kWh, 48V for >5kWh.")
    battery_cable_length = st.number_input("Battery to inverter distance (ft)", 1, 50, 5)

if total_wattage <= 0:
    st.warning("Please enter a wattage greater than 0.")
    st.stop()

# --- Constants ---
dod = 0.8 if "Lithium" in battery_type else 0.5
daily_energy_wh = total_wattage * runtime_hours
inverter_efficiency = 0.90

# Battery calculation
required_battery_wh = daily_energy_wh / inverter_efficiency
battery_usable_wh_per_unit = 1200 * dod  # 100Ah * 12V
num_batteries = math.ceil(required_battery_wh / battery_usable_wh_per_unit)

# Solar array
needed_solar_w = (daily_energy_wh * 1.3) / sun_hours
num_panels = math.ceil(needed_solar_w / 400)
solar_array_w = num_panels * 400

# Inverter
inverter_w = math.ceil(total_wattage * 1.25)

# Battery config
series_strings = sys_voltage // 12
parallel_groups = math.ceil(num_batteries / series_strings) if series_strings > 0 else num_batteries
final_voltage = series_strings * 12

# Currents
inverter_dc_amps = (inverter_w / final_voltage) / 0.85
pv_voltage_est = 80
pv_amps = solar_array_w / pv_voltage_est
charge_controller_amps = solar_array_w / final_voltage

# --- Cable sizing functions ---
def recommend_cable_size_advanced(amps, voltage, distance_ft, is_dc=True):
    max_vdrop_pct = 0.03 if is_dc else 0.02
    max_vdrop = voltage * max_vdrop_pct
    round_trip_ft = distance_ft * 2
    awg_resistance = {0:0.0983,1:0.1239,2:0.1563,3:0.1970,4:0.2485,6:0.3951,8:0.6282,10:0.9989,12:1.588,14:2.525,16:4.016,18:6.385,20:10.15}
    ampacity = {0:170,1:145,2:130,3:115,4:100,6:80,8:65,10:50,12:35,14:25,16:18,18:14,20:11}
    for awg, r in sorted(awg_resistance.items(), key=lambda x: x[0]):
        total_resistance = (r/1000) * round_trip_ft
        vdrop = amps * total_resistance
        if vdrop <= max_vdrop and amps <= ampacity.get(awg,0):
            return "{} AWG".format(awg) if awg <=0 else "{} AWG".format(awg)
    return "10 AWG (minimum)"

def recommend_cable_size_simple(amps):
    if amps <=15: return "14 AWG"
    elif amps <=20: return "12 AWG"
    elif amps <=30: return "10 AWG"
    elif amps <=55: return "6 AWG"
    elif amps <=85: return "4 AWG"
    elif amps <=130: return "1 AWG"
    elif amps <=175: return "2/0 AWG"
    elif amps <=230: return "4/0 AWG"
    else: return "Parallel 4/0 AWG"

# --- Main display ---
st.title("☀️ 24/7 Solar System Designer")
st.markdown("Based on **{}W** running **{} hours/day** ({} Wh/day)".format(total_wattage, runtime_hours, daily_energy_wh))

col1, col2 = st.columns(2)
with col1:
    st.subheader("🔋 Battery Bank")
    st.metric("100Ah 12V Batteries", "{} pcs".format(num_batteries))
    st.caption("{}% DoD, {}V system".format(int(dod*100), final_voltage))
    st.caption("Config: {}S {}P".format(series_strings, parallel_groups))
    st.subheader("☀️ Solar Array")
    st.metric("Total Array", "{} W".format(solar_array_w))
    st.metric("400W Panels", "{} panels".format(num_panels))
with col2:
    st.subheader("⚡ Inverter")
    st.metric("Continuous Rating", "{} W".format(inverter_w))
    st.metric("MPPT Controller", "{:.0f} A @ {}V".format(charge_controller_amps, final_voltage))

# --- Connection diagram (using list join to avoid triple-quote issues) ---
st.markdown("### 🔗 System Connection Diagram")
diagram_lines = [
    "```",
    "☀️ SOLAR ARRAY ({} x 400W)",
    "    │  PV wire – {} (short) / {} (long)",
    "    ▼",
    "⚡ MPPT ({}A @ {}V)",
    "    │  Battery cable – {}",
    "    ▼",
    "🔋 BATTERY ({}S{}P, {} x 100Ah)",
    "    │  Heavy DC + Class T fuse – {}",
    "    ▼",
    "🔄 INVERTER ({}W)",
    "    │  AC cable – {} Romex",
    "    ▼",
    "💡 LOAD ({}W)",
    "```"
]
diagram = "\n".join(diagram_lines)
st.markdown(diagram.format(
    num_panels,
    recommend_cable_size_simple(pv_amps),
    recommend_cable_size_advanced(pv_amps, pv_voltage_est, 30, True),
    charge_controller_amps, final_voltage,
    recommend_cable_size_advanced(charge_controller_amps, final_voltage, 10, True),
    series_strings, parallel_groups, num_batteries,
    recommend_cable_size_advanced(inverter_dc_amps, final_voltage, battery_cable_length, True),
    inverter_w,
    recommend_cable_size_advanced(inverter_w/120, 120, 10, False),
    total_wattage
))

# --- DIY instructions ---
with st.expander("📋 DIY Setup Instructions"):
    st.markdown("""
1. **Batteries**: Wire {} in series for {}V, then {} such strings in parallel. Use busbars and a Class T fuse.
2. **Solar**: Mount {} panels facing south, wire into MPPT controller.
3. **Controller**: Connect PV → controller → battery. Set proper voltage parameters.
4. **Inverter**: Connect battery → inverter with heavy cable. Ground all equipment.
5. **AC**: Inverter output to load panel. Install disconnects and breakers.
""".format(series_strings, final_voltage, parallel_groups, num_panels))

# --- Cable table ---
st.header("🔌 Cable Recommendations")
solar_distance = st.slider("Solar to controller (ft)", 10, 150, 30)
ac_distance = st.slider("Inverter to AC panel (ft)", 5, 100, 10)
cable_data = [
    ("Battery → Inverter ({}V)".format(final_voltage), "{:.0f}A".format(inverter_dc_amps), recommend_cable_size_advanced(inverter_dc_amps, final_voltage, battery_cable_length, True), "Battery cable"),
    ("Solar → Controller", "{:.0f}A".format(pv_amps), recommend_cable_size_advanced(pv_amps, pv_voltage_est, solar_distance, True), "PV wire"),
    ("Controller → Battery", "{:.0f}A".format(charge_controller_amps), recommend_cable_size_advanced(charge_controller_amps, final_voltage, 10, True), "Battery cable"),
    ("Inverter → AC Panel", "{:.0f}A".format(inverter_w/120), recommend_cable_size_advanced(inverter_w/120, 120, ac_distance, False), "THHN/Romex")
]
st.table({"Connection": [r[0] for r in cable_data], "Current": [r[1] for r in cable_data], "Recommended": [r[2] for r in cable_data], "Cable Type": [r[3] for r in cable_data]})

# --- Off-the-shelf alternatives ---
st.header("📦 Off-the-Shelf Alternatives (EcoFlow / DJI)")
daily_wh = daily_energy_wh
if daily_wh <= 1024:
    alts = [("EcoFlow RIVER 2 Pro", "1024Wh", "$499"), ("DJI Power 1000", "1024Wh", "$499")]
elif daily_wh <= 2048:
    alts = [("EcoFlow DELTA 2 Max", "2048Wh", "$1599"), ("DJI Power 1000 x2", "2048Wh", "$1000+")]
elif daily_wh <= 3600:
    alts = [("EcoFlow DELTA Pro", "3600Wh", "$2999"), ("EcoFlow DELTA Pro + extra batt", "7200Wh", "$4798")]
else:
    alts = [("EcoFlow DELTA Pro Ultra", "6000Wh+", "Contact dealer"), ("DJI custom", "Multiple", "Variable")]
cols = st.columns(2)
for i, (name, cap, price) in enumerate(alts[:2]):
    with cols[i]:
        st.subheader(name)
        st.write("Capacity:", cap)
        st.write("Price:", price)

# --- Summary comparison ---
st.divider()
st.subheader("DIY vs. Off-the-Shelf")
diy_cost = num_batteries*150 + num_panels*200 + inverter_w*0.5
st.markdown("**DIY System Cost**: ~${:.0f}".format(diy_cost))
st.markdown("**DIY Pros**: Scalable, repairable, lower long-term cost.")
st.markdown("**Off-the-shelf Pros**: No wiring, portable, app control.")
st.warning("⚠️ Always use proper fuses and consult an electrician.")
