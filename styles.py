import streamlit as st

def load_styles():


# =========================
# STYLE (MODERNO DARK UI)
# =========================



    st.markdown("""
<style>

/* Fondo oscuro permanente */
html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
.main{
    background-color:#0b1220 !important;
}

/* Mantener tu espaciado */
.block-container{
    padding-top:2rem;
}

/* Tus cards */
.card{
    background-color:#111827;
    padding:18px;
    border-radius:12px;
    border:1px solid #1f2937;
    text-align:center;
}

/* Textos */
.title{
    font-size:28px;
    font-weight:700;
    color:white;
}

.subtitle{
    color:#94a3b8;
    margin-bottom:20px;
}

.metric-value{
    font-size:22px;
    font-weight:bold;
    color:white;
}

.metric-label{
    color:#94a3b8;
    font-size:12px;
}

/* Botones Refresh y Change Config */
.stButton > button{
    background:#38bdf8 !important;
    color:white !important;
    border:none !important;
    border-radius:8px;
    font-weight:600;
}

.stButton > button:hover{
    background:#0ea5e9 !important;
}

.stButton > button:active{
    background:#0284c7 !important;
}

</style>
""", unsafe_allow_html=True)