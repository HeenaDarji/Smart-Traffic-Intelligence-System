import streamlit as st
import pandas as pd
import plotly.express as px
import tempfile
import os

from backend import (
    process_image_and_get_density,
    process_video_for_presentation
)

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Smart Traffic Intelligence System",
    page_icon="🚦",
    layout="wide"
)

# ================= CUSTOM CSS =================
st.markdown("""
<style>
.big-title {
    font-size: 40px;
    font-weight: 700;
    text-align: center;
}
.sub-title {
    text-align: center;
    color: #00E5FF;
}
.card {
    padding: 18px;
    border-radius: 15px;
    background: #1c1f26;
    box-shadow: 0px 0px 12px rgba(0,229,255,0.15);
    text-align: center;
}
.metric-label {
    font-size: 14px;
    color: #bbbbbb;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown('<div class="big-title">🚦 Smart Traffic Intelligence System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Traffic • Pollution • Fuel Waste Analytics</div>', unsafe_allow_html=True)
st.markdown("---")

# ================= SIDEBAR =================
with st.sidebar:
    st.header("📂 Input Panel")
    img = st.file_uploader("📸 Upload Image", ["jpg","png","jpeg"])
    vid = st.file_uploader("🎥 Upload Video", ["mp4","avi","mov"])
    run = st.button("🚀 Run Analysis")

# ================= TABS =================
tab1, tab2, tab3 = st.tabs(["📸 Image Analysis", "🎥 Video Analysis", "📊 Historical Data"])

# =====================================================
# ================= IMAGE TAB =========================
# =====================================================
with tab1:
    if run and img:

        ext = os.path.splitext(img.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
            t.write(img.read())
            path = t.name

        car,bike,bus,truck,total,density,pollution,fuel = process_image_and_get_density(path)

        st.subheader("📸 Image Traffic Results")

        c1,c2,c3,c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="card">
            <div class="metric-label">Total Vehicles</div>
            <div class="metric-value">{total}</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="card">
            <div class="metric-label">Cars</div>
            <div class="metric-value">{car}</div>
            </div>
            """, unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="card">
            <div class="metric-label">Bikes</div>
            <div class="metric-value">{bike}</div>
            </div>
            """, unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="card">
            <div class="metric-label">Heavy Vehicles</div>
            <div class="metric-value">{bus+truck}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 🌍 Impact Analysis")
        c1,c2,c3 = st.columns(3)
        c1.success(f"🚦 Density: {density}")
        c2.error(f"🌫 CO₂ Emission: {pollution} kg")
        c3.warning(f"⛽ Fuel Wasted: {fuel} L")

# =====================================================
# ================= VIDEO TAB =========================
# =====================================================
with tab2:
    if run and vid:

        ext = os.path.splitext(vid.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as t:
            t.write(vid.read())
            path = t.name

        res = process_video_for_presentation(path)

        st.subheader("🎥 Video Traffic Insights")

        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Avg Vehicles", res["average"])
        c2.metric("Cars", res["final_counts"]["mobil"])
        c3.metric("Bikes", res["final_counts"]["motor"])
        c4.metric("Bus", res["final_counts"]["bus"])
        c5.metric("Truck", res["final_counts"]["truk"])

        st.markdown("### 🌍 Impact Analysis")
        c1,c2,c3 = st.columns(3)
        c1.success(f"🚦 Density: {res['density']}")
        c2.error(f"🌫 CO₂ Emission: {res['pollution']} kg")
        c3.warning(f"⛽ Fuel Wasted: {res['fuel']} L")

        # -------- LINE GRAPH --------
        df_line = pd.DataFrame({
            "Time": list(range(len(res["timeline"]))),
            "Vehicles": res["timeline"]
        })

        st.subheader("📈 Vehicle Count Over Time")
        st.plotly_chart(px.line(df_line, x="Time", y="Vehicles"), use_container_width=True)

        # -------- BAR GRAPH --------
        final_counts = res["final_counts"]
        df_bar = pd.DataFrame({
            "Vehicle": ["Cars", "Bike", "Buses", "Trucks"],
            "Count": [
                final_counts["mobil"],
                final_counts["motor"],
                final_counts["bus"],
                final_counts["truk"]
            ]
        })

        st.subheader("📊 Vehicle Type Distribution")
        st.plotly_chart(px.bar(df_bar, x="Vehicle", y="Count"), use_container_width=True)

# =====================================================
# ================= DATA TAB ==========================
# =====================================================
with tab3:
    st.subheader("📊 Historical Traffic Dataset")
    df = pd.read_csv("traffic_data.csv")
    st.dataframe(df, use_container_width=True)

    st.subheader("⏰ Peak Hour Identification")
    peak = df[df["total"] == df["total"].max()]
    st.dataframe(peak, use_container_width=True)

    st.subheader("📊 Density Distribution")
    st.plotly_chart(px.histogram(df, x="density"), use_container_width=True)
