import streamlit as st

# --- ASSUMED VARIABLES (you should have these defined earlier) ---
# These are placeholder values - replace with your actual calculations
daily_energy_wh = 2400 # Example: 2.4 kWh daily usage
num_batteries = 4
series_strings = 2
parallel_groups = 2
final_voltage = 24
num_panels = 6
solar_array_w = 2400
inverter_w = 3000
inverter_dc_amps = inverter_w / final_voltage # 125A for 24V system
pv_amps = 40 # Example
pv_voltage_est = 100 # Example
charge_controller_amps = 60 # Example

# --- HELPER FUNCTIONS ---
def recommend_cable_size_advanced(amps, voltage, distance, is_dc=True):
 """Simplified cable size recommendation"""
 # This is a placeholder - implement your actual logic
 if amps > 100:
 return "2/0 AWG"
 elif amps > 60:
 return "4 AWG"
 elif amps > 30:
 return "8 AWG"
 else:
 return "10 AWG"

def draw_connection_diagram():
 """Draw system diagram"""
 st.info("📊 System connection diagram would be displayed here")
 # Add your diagram rendering code

# --- MAIN CODE STARTS HERE ---

draw_connection_diagram()

# --- DETAILED DIY INSTRUCTIONS ---
with st.expander("📋 Step-by-Step DIY Solar Setup"):
 st.markdown(f"""
**1. Assemble the battery bank** 
 - Connect {series_strings} batteries in **series** to reach {final_voltage}V. 
 - Then connect {parallel_groups} of these series strings in **parallel**. 
 - Use busbars for parallel connections. Add a Class T fuse on the positive line close to the battery.

**2. Install solar panels** 
 - Mount {num_panels} x 400W panels facing south (northern hemisphere). 
 - Wire in series/parallel to keep voltage within your MPPT range. 
 - Use MC4 connectors and UV-resistant PV wire.

**3. Charge controller** 
 - Connect PV array → MPPT controller (with DC breaker in between). 
 - Then connect controller → battery bank (with fuse).

**4. Inverter and AC wiring** 
 - Connect battery → inverter using heavy gauge cable as recommended above. 
 - Inverter AC output → load center / outlets (use GFCI breakers).

**5. Grounding & protection** 
 - Ground all metal frames, battery negative, and inverter chassis. 
 - Install a DC disconnect between solar array and controller, and an AC disconnect at the inverter output.
""")

# --- CABLE RECOMMENDATIONS WITH DISTANCE SLIDERS ---
st.header("🔌 Cable & Wiring Guide")
solar_distance = st.slider("Solar array to controller distance (ft)", 10, 150, 30, help="One‑way length")
ac_distance = st.slider("Inverter to main AC panel (ft)", 5, 100, 10, help="One‑way length")

# Calculate AC amps for inverter
inverter_ac_amps = inverter_w / 120

cable_data = [
 {"Connection": f"Battery → Inverter ({final_voltage}V DC)", 
 "Current (A)": f"{inverter_dc_amps:.1f}",
 "Recommended": recommend_cable_size_advanced(inverter_dc_amps, final_voltage, 5, is_dc=True),
 "Type": "Welding / battery cable (fine stranded)"},
 {"Connection": "Solar → Controller (PV)", 
 "Current (A)": f"{pv_amps:.1f}",
 "Recommended": recommend_cable_size_advanced(pv_amps, pv_voltage_est, solar_distance, is_dc=True),
 "Type": "PV wire, MC4 connectors"},
 {"Connection": f"Controller → Battery ({final_voltage}V DC)", 
 "Current (A)": f"{charge_controller_amps:.1f}",
 "Recommended": recommend_cable_size_advanced(charge_controller_amps, final_voltage, 10, is_dc=True),
 "Type": "Battery cable, tinned copper"},
 {"Connection": "Inverter → AC Panel (120V AC)", 
 "Current (A)": f"{inverter_ac_amps:.1f}",
 "Recommended": recommend_cable_size_advanced(inverter_ac_amps, 120, ac_distance, is_dc=False),
 "Type": "THHN / NM-B (Romex), copper"}
]
st.table(cable_data)

# --- PORTABLE POWER STATIONS (EcoFlow / DJI) ---
st.header("📦 Off-the-Shelf Alternatives")
st.write("If DIY isn't for you, these all-in-one units can run your daily load:")

daily_wh = daily_energy_wh
if daily_wh <= 1000:
 alts = [("EcoFlow RIVER 2 Pro", "1024 Wh, 1800W", "~$499"),
 ("DJI Power 1000", "1024 Wh, 2200W", "~$499")]
elif daily_wh <= 2048:
 alts = [("EcoFlow DELTA 2 Max", "2048 Wh, 2400W", "~$1599"),
 ("DJI Power 1000 (x2 + adapter)", "2048 Wh total", "~$1000+")]
elif daily_wh <= 3600:
 alts = [("EcoFlow DELTA Pro", "3600 Wh, 3600W", "~$2999"),
 ("EcoFlow DELTA Pro + extra batt", "7200 Wh", "~$4798")]
else:
 alts = [("EcoFlow DELTA Pro Ultra", "6000-21kWh modular", "Contact dealer"),
 ("DJI Power expansion system", "Multiple units parallel", "Variable")]

cols = st.columns(min(3, len(alts)))
for i, (name, specs, price) in enumerate(alts):
 with cols[i % len(cols)]:
 st.markdown(f"**{name}**")
 st.write(f"Capacity: {specs}")
 st.write(f"Price: {price}")

st.caption("💡 Expandable systems allow extra battery modules or solar input for 24/7 operation.")

# --- SUMMARY COMPARISON ---
st.divider()
st.header("📊 DIY vs. Off-the-Shelf")
colA, colB = st.columns(2)

with colA:
 st.subheader("DIY Solar System")
 st.markdown(f"""
- **Batteries:** {num_batteries} x 100Ah → {num_batteries * 1.2:.1f} kWh nominal 
- **Solar:** {num_panels} x 400W = {solar_array_w}W 
- **Inverter:** {inverter_w}W pure sine wave 
- **Cost estimate:** ~${(num_batteries*150) + (num_panels*200) + (inverter_w*0.5):.0f} 
- **Pros:** Fully scalable, lower cost per Wh, replaceable parts 
- **Cons:** Requires electrical knowledge, assembly time, maintenance
""")

with colB:
 st.subheader("Off-the-Shelf (EcoFlow/DJI)")
 st.markdown(f"""
- **Typical model:** {alts[0][0]} ({alts[0][1].split(',')[0]}) 
- **Pros:** No wiring, portable, app control, expandable with extra batteries 
- **Cons:** Higher $/Wh, limited to proprietary batteries 
- **Best for:** Lower wattage (<1500W), mobile use, or simplified backup
""")

# --- SAFETY NOTE ---
st.warning("⚠️ **Safety Note:** Always install fuses/breakers between every major component. Use copper wire rated for the environment. Consult a licensed electrician for final connection to household wiring.")
st.caption("🔧 **Disclaimer:** All numbers are estimates. Actual needs vary with location, temperature, and system losses. Add 20-30% margin for critical 24/7 loads.")
