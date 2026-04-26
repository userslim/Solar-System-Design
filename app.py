""")

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
    # Ensure there's an 'f' before the triple quotes for f-string formatting
    st.markdown(f"""
**To run {wattage:.0f}W appliances 24/7 you need:**

1. **Battery Bank**: {num_batteries} × 100Ah {battery_type}  
   **Configuration**: {sys_voltage}V system – {series_strings} in series, {parallel_groups} parallel strings

2. **Solar Panels**: {num_panels} × {panel_watt}W monocrystalline

3. **Charge Controller**: MPPT rated for {solar_array_w:.0f}W / {sys_voltage}V

4. **Inverter**: {inverter_continuous_w}W pure sine wave

5. **Cables & Protection**: See diagram and table below.
""")

draw_system_diagram()

# ---- DETAILED CABLE TABLE ----
st.markdown("---")
st.header("🔌 Detailed Cable & Wiring Recommendations")

cable_info = [
    {
        "Run": f"Battery Bank → Inverter ({sys_voltage}V DC)",
        "Current": f"{inverter_dc_current:.1f} A",
        "Length": f"{battery_cable_length} ft",
        "Size": recommend_cable_size(inverter_dc_current, sys_voltage, battery_cable_length, is_dc=True),
        "Type": "Welding / UL battery cable (fine stranded, 105°C)",
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
    "Run": "Solar panels → Charge Controller (DC, PV)",
    "Current": f"{solar_current_imp:.1f} A",
    "Length": f"{solar_distance} ft",
    "Size": recommend_cable_size(solar_current_imp, 48, solar_distance, is_dc=True),
    "Type": "PV wire (UV resistant, MC4 connectors)",
    "Accessories": "DC breaker / PV disconnect"
})

cable_info.append({
    "Run": "Inverter → AC Load Panel (120V AC)",
    "Current": f"{ac_current:.1f} A",
    "Length": "10 ft",
    "Size": recommend_cable_size(ac_current, 120, 10, is_dc=False),
    "Type": "THHN/THWN-2 or NM-B (Romex), copper",
    "Accessories": "Main AC breaker, GFCI"
})

for c in cable_info:
    with st.expander(f"📏 {c['Run']} – {c['Current']}"):
        st.markdown(f"""
- **Recommended size**: **{c['Size']}**  
- **Cable type**: {c['Type']}  
- **Accessories**: {c['Accessories']}  
- *One-way distance*: {c['Length']}
""")

# ---- OFF-THE-SHELF ALTERNATIVES ----
st.markdown("---")
st.header("📦 Off-the-shelf Alternatives (EcoFlow / DJI)")

capacity_wh = daily_energy_wh
if capacity_wh <= 1024:
    alternatives = [
        ("EcoFlow RIVER 2 Pro", "1024 Wh, 1800W output", "~$499"),
        ("DJI Power 1000", "1024 Wh, 2200W output", "~$499")
    ]
elif capacity_wh <= 2048:
    alternatives = [
        ("EcoFlow DELTA 2 Max", "2048 Wh, 2400W output", "~$1599"),
        ("DJI Power 1000 (x2 + adapter)", "Expandable to 2048 Wh", "~$1000+")
    ]
elif capacity_wh <= 3600:
    alternatives = [
        ("EcoFlow DELTA Pro", "3600 Wh, 3600W output", "~$2999"),
        ("DJI Power 1000 + extra battery", "2048 Wh (combo)", "~$1249")
    ]
elif capacity_wh <= 7200:
    alternatives = [
        ("EcoFlow DELTA Pro + Extra Battery", "7200 Wh total", "~$4798"),
        ("EcoFlow DELTA Pro Ultra (1 stack)", "6100 Wh, 7200W", "~$5699")
    ]
else:
    alternatives = [
        ("EcoFlow DELTA Pro Ultra (multiple stacks)", "Customizable > 10 kWh", "Contact dealer"),
        ("DJI Power Expansion high capacity", "Multiple units parallel", "Variable")
    ]

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

colA, colB = st.columns(2)
with colA:
    st.subheader("DIY Solar System")
    st.markdown(f"""
- **Batteries**: {num_batteries} × 100Ah → {num_batteries*1200/1000:.1f} kWh nominal  
- **Solar**: {num_panels} × 400W = {solar_array_w:.0f}W array  
- **Inverter**: {inverter_continuous_w}W pure sine wave  
- **Cables**: As per table above  
- **Pros**: Fully scalable, lower long-term cost  
- **Cons**: Requires electrical knowledge, assembly  
- **Estimated DIY cost**: ~${num_batteries*150 + num_panels*200 + inverter_continuous_w*0.5:.0f}
""")

with colB:
    st.subheader("Off-the-shelf (EcoFlow/DJI)")
    st.markdown(f"""
- **Typical model**: {alternatives[0][0]} ({alternatives[0][1].split(',')[0]})  
- **Pros**: No wiring, portable, app control  
- **Cons**: Higher cost per Wh, limited expansion  
- **Best for**: Lower wattage (<1500W) or mobile use  
- **24/7 runtime**: May need extra batteries/solar (sold separately)
""")

st.markdown("---")
st.info("🔧 **Note**: All numbers are estimates. For critical 24/7 operation, add 20-30% extra battery capacity and consider 2+ days of autonomy. Always follow local electrical codes and consult a licensed electrician.")
