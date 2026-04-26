import streamlit as st
import math

# --- PAGE CONFIG ---
st.set_page_config(page_title="Solar Design Tool", layout="wide")

# --- CSS FOR CLEAN LOOK ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def recommend_cable_size(amps):
    """Simple AWG lookup based on ampacity (NEC guidelines for chassis/short runs)"""
    if amps <= 15: return "14 AWG"
    elif amps <= 20: return "12 AWG"
    elif amps <= 30: return "10 AWG"
    elif amps <= 55: return "6 AWG"
    elif amps <= 85: return "4 AWG"
    elif amps <= 130: return "1 AWG"
    elif amps <= 175: return "2/0 AWG"
    elif amps <= 230: return "4/0 AWG"
    else: return "Parallel 4/0 AWG or Busbars"

# --- SIDEBAR / INPUTS ---
with st.sidebar:
    st.header("⚙️ System Parameters")
    sys_voltage = st.selectbox("System Voltage (DC)", [12, 24, 48], index=0)
    battery_type = st.selectbox("Battery Type", ["LiFePO4 (Lithium)", "AGM/Lead Acid"])
    sun_hours = st.slider("Peak Sun Hours per Day", 1.0, 8.0, 4.5)
    dod = 0.8 if "Lithium" in battery_type else 0.5
    
    st.divider()
    st.header("🏠 Appliance Calculator")
    
    # Simple dynamic list for appliances
    if 'appliances' not in st.session_state:
        st.session_state.appliances = [{"name": "Fridge", "watts": 80, "hours": 24}]

    def add_appliance():
        st.session_state.appliances.append({"name": "New Item", "watts": 0, "hours": 0})

    for i, app in enumerate(st.session_state.appliances):
        with st.expander(f"Item: {app['name']}"):
            app['name'] = st.text_input(f"Name", value=app['name'], key=f"n{i}")
            app['watts'] = st.number_input(f"Watts", value=app['watts'], key=f"w{i}")
            app['hours'] = st.number_input(f"Hours/Day", value=app['hours'], key=f"h{i}")

    st.button("➕ Add Appliance", on_click=add_appliance)

# --- CALCULATIONS ---
total_wattage = sum(a['watts'] for a in st.session_state.appliances)
daily_energy_wh = sum(a['watts'] * a['hours'] for a in st.session_state.appliances)

# Sizing logic
# We need enough battery to cover the Wh needed, adjusted for Depth of Discharge (DoD)
needed_battery_wh = daily_energy_wh / dod
num_batteries = math.ceil(needed_battery_wh / (100 * 12)) # Assuming 100Ah 12V units

# Solar: Daily Wh / sun hours * efficiency factor (1.25)
needed_solar_w = (daily_energy_wh * 1.3) / sun_hours
num_panels = math.ceil(needed_solar_w / 400)
solar_array_w = num_panels * 400

# Inverter: Max wattage plus 25% safety margin
inverter_w = math.ceil(total_wattage * 1.25)

# --- MAIN UI ---
st.title("☀️ Off-Grid Solar Designer")
st.markdown(f"Calculated for a total load of **{total_wattage}W** running for a total of **{daily_energy_wh:.0f} Wh/day**.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("🔋 Battery Bank")
    st.metric("100Ah 12V Batteries", f"{num_batteries} pcs")
    st.caption(f"Usable Energy: {daily_energy_wh:.0f}Wh at {dod*100:.0f}% DoD")
    
    st.subheader("☀️ Solar Array")
    st.metric("Total Solar Required", f"{solar_array_w} W")
    st.metric("400W Panels", f"{num_panels} panels")

with col2:
    st.subheader("⚡ Inverter & Setup")
    st.metric("Inverter Size", f"{inverter_w} W")
    
    # Logic text with cleaned formatting
    summary = f"""
1. **Batteries**: {num_batteries} units (wired for {sys_voltage}V).
2. **Panels**: {num_panels} x 400W panels.
3. **Controller**: MPPT rated for at least {solar_array_w / sys_voltage:.0f} Amps.
"""
    st.info(summary)

# --- CABLE TABLE ---
st.header("🔌 Cable & Wiring Guide")
inverter_dc_amps = (inverter_w / sys_voltage) / 0.85 # Including efficiency loss
pv_amps = (solar_array_w / 80) # Estimated high voltage PV string

cable_data = [
    {"Connection": "Battery to Inverter", "Amps": f"{inverter_dc_amps:.1f}A", "Recommended Cable": recommend_cable_size(inverter_dc_amps)},
    {"Connection": "Solar Panels to Controller", "Amps": f"{pv_amps:.1f}A", "Recommended Cable": "10 AWG (PV Wire)"},
    {"Connection": "Controller to Battery", "Amps": f"{solar_array_w/sys_voltage:.1f}A", "Recommended Cable": recommend_cable_size(solar_array_w/sys_voltage)}
]
st.table(cable_data)

# --- PORTABLE POWER STATIONS ---
st.header("📦 Portable Power Station Alternatives")
st.write("If a DIY build is too complex, these 'All-in-one' units can handle your daily load:")

# Logic for alternatives based on capacity
if daily_energy_wh <= 1000:
    alts = [["EcoFlow River 2 Pro", "768Wh", "$499"], ["DJI Power 1000", "1024Wh", "$699"]]
elif daily_energy_wh <= 3000:
    alts = [["EcoFlow Delta 2 Max", "2048Wh", "$1,599"], ["Anker 767", "2048Wh", "$1,699"]]
else:
    alts = [["EcoFlow Delta Pro", "3600Wh", "$2,999"], ["EcoFlow Delta Pro Ultra", "6000Wh", "$5,299"]]

cols = st.columns(len(alts))
for i, item in enumerate(alts):
    with cols[i]:
        st.markdown(f"**{item[0]}**")
        st.write(f"Capacity: {item[1]}")
        st.write(f"Price: ~{item[2]}")

st.divider()
st.warning("⚠️ **Safety Note:** This tool provides estimates. Always install fuses/breakers between all major components.")
