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
.main,
.stApp{
    background-color:#0b1220 !important;
    color:#e5e7eb !important;
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

/* Textos generales */
h1, h2, h3, h4, h5, h6,
p, span, label,
[data-testid="stMarkdownContainer"],
[data-testid="stWidgetLabel"],
[data-testid="stExpander"]{
    color:#e5e7eb !important;
}

/* Sidebar y paneles */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"],
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"]{
    background:#0b1220 !important;
}

/* Formularios y contenedores nativos */
[data-testid="stForm"],
[data-testid="stExpander"],
[data-testid="stPopover"],
[data-testid="stAlert"]{
    background:#111827 !important;
    border:1px solid #1f2937 !important;
    border-radius:8px !important;
    color:#e5e7eb !important;
}

/* Inputs, selects y textareas */
.stTextInput input,
.stTextArea textarea,
.stNumberInput input,
.stDateInput input,
.stTimeInput input,
[data-baseweb="select"] > div,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea{
    background:#111827 !important;
    color:#e5e7eb !important;
    border-color:#334155 !important;
    caret-color:#38bdf8 !important;
}

.stTextInput input::placeholder,
.stTextArea textarea::placeholder{
    color:#64748b !important;
}

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"]{
    background:#111827 !important;
    color:#e5e7eb !important;
}

[role="option"]{
    background:#111827 !important;
    color:#e5e7eb !important;
}

[role="option"]:hover{
    background:#1f2937 !important;
}

/* Tablas y dataframes */
[data-testid="stDataFrame"],
[data-testid="stTable"],
.stDataFrame,
.stTable{
    background:#111827 !important;
    color:#e5e7eb !important;
}

div[data-testid="stDataFrame"] div{
    color:#e5e7eb;
}

/* Divisores */
hr{
    border-color:#1f2937 !important;
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
