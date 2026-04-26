"""
    st.markdown(diagram_text.format(
        num_panels,
        recommend_cable_size_simple(pv_amps),
        recommend_cable_size_advanced(pv_amps, pv_voltage_est, 30, is_dc=True),
        charge_controller_amps, final_voltage,
        recommend_cable_size_advanced(charge_controller_amps, final_voltage, 10, is_dc=True),
        parallel_groups, series_strings,
        num_batteries, battery_type.split()[0], final_voltage,
        recommend_cable_size_advanced(inverter_dc_amps, final_voltage, 5, is_dc=True),
        inverter_w,
        recommend_cable_size_advanced(inverter_w/120, 120, 10, is_dc=False),
        total_wattage
    ))
draw_connection_diagram()

# --- DETAILED DIY INSTRUCTIONS ---
with st.expander("📋 Step-by-Step DIY Solar Setup"):
    instructions = """
**1. Assemble the battery bank**  
   - Connect {} batteries in **series** to reach {}V.  
   - Then connect {} of those series strings in **parallel**.  
   - Use busbars for parallel connections. Add a Class T fuse on the positive line close to the battery.

**2. Install solar panels**  
   - Mount {} x 400W panels facing south (northern hemisphere).  
   - Wire in series/parallel to keep voltage within your MPPT range.  
   - Use MC4 connectors and UV-resistant PV wire.

**3. Charge controller**  
   - Connect PV array -> MPPT controller (with DC breaker in between).  
   - Then connect controller -> battery bank (with fuse).

**4. Inverter and AC wiring**  
   - Connect battery -> inverter using heavy gauge cable as recommended above.  
   - Inverter AC output -> load center / outlets (use GFCI breakers).

**5. Grounding & protection**  
   - Ground all metal frames, battery negative, and inverter chassis.  
   - Install a DC disconnect between solar array and controller, and an AC disconnect at the inverter output.
"""
    st.markdown(instructions.format(series_strings, final_voltage, parallel_groups, num_panels))

# --- CABLE RECOMMENDATIONS WITH DISTANCE SLIDERS ---
st.header("🔌 Cable & Wiring Guide")
solar_distance = st.slider("Solar array to controller distance (ft)", 10, 150, 30, help="One-way length")
ac_distance = st.slider("Inverter to main AC panel (ft)", 5, 100, 10, help="One-way length")

cable_data = [
    {"Connection": "Battery -> Inverter ({}V DC)".format(final_voltage),
     "Current (A)": "{:.1f}".format(inverter_dc_amps),
     "Recommended": recommend_cable_size_advanced(inverter_dc_amps, final_voltage, 5, is_dc=True),
     "Type": "Welding / battery cable (fine stranded)"},
    {"Connection": "Solar -> Controller (PV)",
     "Current (A)": "{:.1f}".format(pv_amps),
     "Recommended": recommend_cable_size_advanced(pv_amps, pv_voltage_est, solar_distance, is_dc=True),
     "Type": "PV wire, MC4 connectors"},
    {"Connection": "Controller -> Battery ({}V DC)".format(final_voltage),
     "Current (A)": "{:.1f}".format(charge_controller_amps),
     "Recommended": recommend_cable_size_advanced(charge_controller_amps, final_voltage, 10, is_dc=True),
     "Type": "Battery cable, tinned copper"},
    {"Connection": "Inverter -> AC Panel (120V AC)",
     "Current (A)": "{:.1f}".format(inverter_w/120),
     "Recommended": recommend_cable_size_advanced(inverter_w/120, 120, ac_distance, is_dc=False),
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
        st.markdown("**{}**".format(name))
        st.write("Capacity: {}".format(specs))
        st.write("Price: {}".format(price))

st.caption("💡 Expandable systems allow extra battery modules or solar input for 24/7 operation.")

# --- SUMMARY COMPARISON ---
st.divider()
st.header("📊 DIY vs. Off-the-Shelf")
colA, colB = st.columns(2)

with colA:
    st.subheader("DIY Solar System")
    diy_text = """
- **Batteries:** {} x 100Ah -> {:.1f} kWh nominal  
- **Solar:** {} x 400W = {}W  
- **Inverter:** {}W pure sine wave  
- **Cost estimate:** ~${:.0f}  
- **Pros:** Fully scalable, lower cost per Wh, replaceable parts  
- **Cons:** Requires electrical knowledge, assembly time, maintenance
"""
    st.markdown(diy_text.format(
        num_batteries, num_batteries * 1.2,
        num_panels, solar_array_w,
        inverter_w,
        (num_batteries*150) + (num_panels*200) + (inverter_w*0.5)
    ))

with colB:
    st.subheader("Off-the-Shelf (EcoFlow/DJI)")
    offthe_shelf_text = """
- **Typical model:** {} ({})  
- **Pros:** No wiring, portable, app control, expandable with extra batteries  
- **Cons:** Higher $/Wh, limited to proprietary batteries  
- **Best for:** Lower wattage (<1500W), mobile use, or simplified backup
"""
    st.markdown(offthe_shelf_text.format(
        alts[0][0], alts[0][1].split(',')[0]
    ))

# --- SAFETY NOTE ---
st.warning("⚠️ **Safety Note:** Always install fuses/breakers between every major component. Use copper wire rated for the environment. Consult a licensed electrician for final connection to household wiring.")
st.caption("🔧 **Disclaimer:** All numbers are estimates. Actual needs vary with location, temperature, and system losses. Add 20-30% margin for critical 24/7 loads.")
