""")
draw_connection_diagram()

# --- DETAILED DIY INSTRUCTIONS ---
with st.expander("📋 Step-by-Step DIY Solar Setup"):
    st.markdown(f"""
**1. Assemble the battery bank**  
   - Connect {series_strings} batteries in **series** to reach {final_voltage}V.  
   - Then connect {parallel_groups} of those series strings in **parallel**.  
   - Use busbars for parallel connections. Add a Class T fuse on the positive line close to the battery.

**2. Install solar panels**  
   - # Ensure the string starts with an 'f' and uses standard spaces
st.write(f"- Mount {num_panels} * 400W panels facing south.")  
   - Wire in series/parallel to keep voltage within your MPPT range.  
   - Use MC4 connectors and UV-resistant PV wire.

**3. Charge controller**  
   - Connect PV array -> MPPT controller (with DC breaker in between).  
   - Then connect controller -> battery bank (with fuse).

**4. Inverter and AC wiring**  
   - Connect battery -> inverter using heavy gauge cable (as recommended above).  
   - Inverter AC output -> load center / outlets (use GFCI breakers).

**5. Grounding & protection**  
   - Ground all metal frames, battery negative, and inverter chassis.  
   - Install a DC disconnect between solar array and controller, and an AC disconnect at the inverter output.
""")

# --- CABLE RECOMMENDATIONS (with distance) ---
st.header("🔌 Cable & Wiring Guide")
solar_distance = st.slider("Solar array to controller distance (ft)", 10, 150, 30, help="One-way length")
ac_distance = st.slider("Inverter to main AC panel (ft)", 5, 100, 10, help="One-way length")

cable_data = [
    {"Connection": f"Battery -> Inverter ({final_voltage}V DC)", "Current (A)": f"{inverter_dc_amps:.1f}", 
     "Recommended": recommend_cable_size_advanced(inverter_dc_amps, final_voltage, 5, is_dc=True),
     "Type": "Welding / battery cable (fine stranded)"},
    {"Connection": f"Solar -> Controller (PV)", "Current (A)": f"{pv_amps:.1f}", 
     "Recommended": recommend_cable_size_advanced(pv_amps, pv_voltage_est, solar_distance, is_dc=True),
     "Type": "PV wire, MC4 connectors"},
    {"Connection": f"Controller -> Battery ({final_voltage}V DC)", "Current (A)": f"{charge_controller_amps:.1f}", 
     "Recommended": recommend_cable_size_advanced(charge_controller_amps, final_voltage, 10, is_dc=True),
     "Type": "Battery cable, tinned copper"},
    {"Connection": f"Inverter -> AC Panel (120V AC)", "Current (A)": f"{inverter_w/120:.1f}", 
     "Recommended": recommend_cable_size_advanced(inverter_w/120, 120, ac_distance, is_dc=False),
     "Type": "THHN / NM-B (Romex), copper"}
]
st.table(cable_data)

# --- PORTABLE POWER STATIONS (EcoFlow/DJI) ---
st.header("📦 Off-the-Shelf Alternatives")
st.write("If DIY isn't for you, these all-in-one units can run your daily load:")

daily_wh = daily_energy_wh
if daily_wh <= 1000:
    alts = [
        ("EcoFlow RIVER 2 Pro", "1024 Wh, 1800W", "~$499"),
        ("DJI Power 1000", "1024 Wh, 2200W", "~$499")
    ]
elif daily_wh <= 2048:
    alts = [
        ("EcoFlow DELTA 2 Max", "2048 Wh, 2400W", "~$1599"),
        ("DJI Power 1000 (x2 + adapter)", "2048 Wh total", "~$1000+")
    ]
elif daily_wh <= 3600:
    alts = [
        ("EcoFlow DELTA Pro", "3600 Wh, 3600W", "~$2999"),
        ("EcoFlow DELTA Pro + extra batt", "7200 Wh", "~$4798")
    ]
else:
    alts = [
        ("EcoFlow DELTA Pro Ultra", "6000-21kWh modular", "Contact dealer"),
        ("DJI Power expansion system", "Multiple units parallel", "Variable")
    ]

cols = st.columns(min(3, len(alts)))
for i, (name, specs, price) in enumerate(alts):
    with cols[i % len(cols)]:
        st.markdown(f"**{name}**")
        st.write(f"Capacity: {specs}")
        st.write(f"Price: {price}")

# --- SUMMARY COMPARISON ---
st.divider()
st.header("📊 DIY vs. Off-the-Shelf")
colA, colB = st.columns(2)
with colA:
    st.subheader("DIY Solar System")
    st.markdown(f"""
- **Batteries**: {num_batteries} x 100Ah -> {num_batteries * 1.2:.1f} kWh nominal
- **Solar**: {num_panels} x 400W = {solar_array_w:.0f}W array
- **Inverter**: {inverter_w}W pure sine wave  
- **Cost estimate (rough):** ~${num_batteries*150 + num_panels*200 + inverter_w*0.5:.0f}  
- **Pros:** Scalable, repairable, lower cost per Wh  
- **Cons:** Requires electrical knowledge, assembly time
""")
with colB:
    st.subheader("Off-the-Shelf (EcoFlow/DJI)")
    st.markdown(f"""
- **Typical model:** {alts[0][0]} ({alts[0][1].split(',')[0]})  
- **Pros:** No wiring, portable, app control, expandable  
- **Cons:** Higher $/Wh, limited to manufacturer batteries  
- **Best for:** Lower wattage (<1500W) or backup/mobile use
""")

# --- SAFETY NOTE ---
st.warning("⚠️ **Safety Note:** Always install appropriate fuses/breakers between every major component. Use only copper wire rated for the environment. Consult a licensed electrician for final connection to household wiring.")
st.caption("🔧 **Disclaimer:** All numbers are estimates. Actual needs may vary based on location, temperature, and system losses. Add 20-30% margin for critical loads.")
