import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime


def render_dashboard(
    project,
    plan_id,
    df,
    bugs_df
):
    # =========================
    # METRICS
    # =========================
    total = int(df["Test Points"].sum()) if not df.empty else 0
    passed = int(df["passed"].sum()) if not df.empty else 0
    failed = int(df["failed"].sum()) if not df.empty else 0
    notrun = int(df["notrun"].sum()) if not df.empty else 0

    executed = passed + failed
    run_rate = round((executed / total) * 100, 1) if total else 0

    total_bugs = len(bugs_df)

    if bugs_df.empty:
        state_counts = pd.Series(dtype="int64")
        priority_counts_all = pd.Series(dtype="int64")
    else:
        state_counts = bugs_df["State"].value_counts()
        priority_counts_all = bugs_df["Priority"].astype(str).value_counts()

    active_bugs = (
        state_counts.get("Active", 0)
        + state_counts.get("New", 0)
        + state_counts.get("Committed", 0)
    )

    closed_bugs = (
        state_counts.get("Closed", 0)
        + state_counts.get("Resolved", 0)
        + state_counts.get("Done", 0)
    )

    critical_bugs = priority_counts_all.get("1", 0)

    
    _, sync_col, config_col = st.columns([7.4, 1.1, 1.3])

    with sync_col:
        if st.button("Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    
    
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








    # =========================
    # HEADER
    # =========================
    st.markdown(f"""
    <div style="
    background:#111827;
    padding:15px;
    border-radius:15px;
    border:1px solid #1f2937;
    margin-top:20px;
    margin-bottom:15px;
    ">
    <h2 style="color:white;margin:0;">
    🚨 QA REPORT
    </h2>
    <p style="color:#94a3b8;margin:5px 0 0 0;">
    {project} • Test Plan {plan_id} • {datetime.now().strftime('%Y-%m-%d')}
    </p>
    </div>
    """, unsafe_allow_html=True)





    # =========================
    # KPI ROW (CENTRADO PRO)
    # =========================
    c1, c2, c3, c4, c5 = st.columns(5)

    c1.markdown(f"<div class='card'><div class='metric-value'>{total}</div><div class='metric-label'>TOTAL</div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><div class='metric-value' style='color:#00e676'>{passed}</div><div class='metric-label'>PASSED</div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><div class='metric-value' style='color:#ff5252'>{failed}</div><div class='metric-label'>FAILED</div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><div class='metric-value' style='color:#facc15'>{notrun}</div><div class='metric-label'>NOT RUN</div></div>", unsafe_allow_html=True)
    c5.markdown(f"<div class='card'><div class='metric-value' style='color:#3b82f6'>{run_rate}%</div><div class='metric-label'>RUN RATE</div></div>", unsafe_allow_html=True)

    st.divider()


    # =========================
    # MAIN LAYOUT
    # =========================
    left, right = st.columns([1.6, 1])

    bug_col1, bug_col2 = st.columns(2)

    # =========================
    # SUITES TABLE (UI CLEAN PRO)
    # =========================

    suite_df = df.copy()
    suite_df.index = range(1, len(suite_df) + 1)

    with left:
        st.markdown("""
        <div style="
        background:#111827;
        padding:15px;
        border-radius:15px;
        border:1px solid #1f2937;
        margin-top:10px;
        margin-bottom:15px;
        ">
            <h3 style="
            color:white;
            margin:0;
            text-align:center;
            ">
            📋 TEST SUITES SUMMARY
            </h3>
        </div>
        """, unsafe_allow_html=True)

        numeric_columns = [
            "suite_id", "passed", "failed", "notrun",
            "Test Points", "Run %", "Pass %", "Fail %"
        ]

        suite_table = suite_df.style.set_properties(
            subset=[column for column in numeric_columns if column in suite_df.columns],
            **{"text-align": "center"}
        )

        st.dataframe(
            suite_table,
            use_container_width=True,
            height=500
        )


    st.markdown("""
        <div style="
        background:#111827;
        padding:15px;
        border-radius:15px;
        border:1px solid #1f2937;
        margin-top:10px;
        margin-bottom:15px;
        ">
            <h3 style="
            color:white;
            margin:0;
            text-align:center;
            ">
            🐞 Bug Analytics
            </h3>
        </div>
        """, unsafe_allow_html=True)
    b1,b2,b3,b4 = st.columns(4)

    b1.markdown(
        f"<div class='card'><div class='metric-value'>{total_bugs}</div><div class='metric-label'>TOTAL BUGS</div></div>",
        unsafe_allow_html=True
    )

    b2.markdown(
        f"<div class='card'><div class='metric-value' style='color:#22c55e'>{active_bugs}</div><div class='metric-label'>ACTIVE</div></div>",
        unsafe_allow_html=True
    )

    b3.markdown(
        f"<div class='card'><div class='metric-value' style='color:#3b82f6'>{closed_bugs}</div><div class='metric-label'>CLOSED</div></div>",
        unsafe_allow_html=True
    )

    b4.markdown(
        f"<div class='card'><div class='metric-value' style='color:#ef4444'>{critical_bugs}</div><div class='metric-label'>CRITICAL</div></div>",
        unsafe_allow_html=True
    )

    st.divider()

    bug_col1, bug_col2 = st.columns(2)

    # =========================
    # DONUT PRO (CENTER FOCUS)
    # =========================
    with right:

        st.markdown("""
        <div style="
        background:#111827;
        padding:15px;
        border-radius:15px;
        border:1px solid #1f2937;
        margin-top:10px;
        margin-bottom:15px;
        ">
            <h3 style="
            color:white;
            margin:0;
            text-align:center;
            ">
            📊 EXECUTION OVERVIEW
            </h3>
        </div>
        """, unsafe_allow_html=True)
        fig = go.Figure(data=[go.Pie(
        labels=[
            f"Passed ({passed})",
            f"Failed ({failed})",
            f"Not Run ({notrun})"
        ],
        values=[passed, failed, notrun],
        hole=0.75,

        marker=dict(
            colors=[
                "#22c55e",
                "#ef4444",
                "#f59e0b"
            ],
            line=dict(
                color="#0b1220",
                width=6
            )
        )
    )])

        run_rate = round((passed + failed) / total * 100, 1) if total else 0

        st.markdown("""
    <style>
    [data-testid="stPlotlyChart"] {
        background-color: #111827;
        border: 1px solid #1f2937;
        border-radius: 15px;
        padding: 0px;
        overflow: hidden;
    }
    </style>
    """, unsafe_allow_html=True)
        
        fig.update_layout(
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220",
            font_color="white",
            height=420,
            showlegend=True,
            legend=dict(
                orientation="h",
                y=-0.12,
                x=0.5,
                xanchor="center"
            ),
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=55
            )
        )
        
        fig.update_traces(
            textinfo="none",
            hoverinfo="label+percent+value",
            domain=dict(x=[0.08, 0.92], y=[0.08, 0.98])
        )

        fig.add_annotation(
        text=f"<b>{run_rate}%</b><br>RUN RATE",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(
            size=35,
            color="white"
        )
    )

        st.plotly_chart(fig, use_container_width=True)
        

    # =========================
    # DONUT BUGS (UI CLEAN PRO)
    # =========================  

    with bug_col1:

        st.subheader("Status")

        state_labels = [
        f"{state} ({count})"
        for state, count in zip(
            state_counts.index,
            state_counts.values
        )
    ]

        fig_state = go.Figure(
        data=[
            go.Pie(
                labels=state_labels,
                values=state_counts.values,
                hole=0.75,

                marker=dict(
                    colors=[
                        "#22c55e",  # verde
                        "#ef4444",  # rojo
                        "#f59e0b",  # amarillo
                        "#3b82f6",  # azul
                        "#8b5cf6",  # morado
                        "#06b6d4"   # cyan
                    ],
                    line=dict(
                        color="#1C1313",
                        width=4
                    )
                )
            )
        ]
    )

        fig_state.update_layout(
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220",
            font_color="white",
            height=420,
            showlegend=True,
            legend=dict(
                orientation="h",
                y=-0.12,
                x=0.5,
                xanchor="center"
            ),
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=55
            )
        )

        fig_state.update_traces(
            textinfo="none",
            hoverinfo="label+percent+value",
            domain=dict(x=[0.08, 0.92], y=[0.08, 0.98])
        )

        fig_state.add_annotation(
            text=f"<b>{total_bugs}</b><br>Total Bugs",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                size=24,
                color="white"
            )
        )

        st.plotly_chart(
            fig_state,
            use_container_width=True
        )

    with bug_col2:

        st.subheader("Priority")

        priority_counts = (
            bugs_df["Priority"]
            .astype(str)
            .value_counts()
            .sort_index()
        )

        fig_priority = go.Figure()

        priority_labels = [
        f"P{priority} ({count})"
        for priority, count in zip(
            priority_counts.index,
            priority_counts.values
        )
    ]

        fig_priority.add_bar(
        x=priority_labels,
        y=priority_counts.values,
        text=priority_counts.values,
        textposition="outside"
    )

        fig_priority.update_layout(
            paper_bgcolor="#0b1220",
            plot_bgcolor="#0b1220",
            font_color="white",
            height=420,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=55
            )
        )

        st.plotly_chart(fig_priority, use_container_width=True)

        
    bugs_display = bugs_df.copy()

    bugs_display.index = range(
        1,
        len(bugs_display) + 1
    )

    st.dataframe(
        bugs_display,
        use_container_width=True,
        height=350
    )