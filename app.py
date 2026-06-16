import streamlit as st
import pandas as pd
import requests
from requests.auth import HTTPBasicAuth
import plotly.graph_objects as go
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# =========================
# CONFIG
# =========================

org = "copavsts"

st.set_page_config(page_title="QA Dashboard", layout="wide")
@st.cache_data(ttl=1800, show_spinner=False)
def load_test_plans(project, pat):
    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)

    plans = []
    continuation_token = None

    while True:
        url = (
            f"https://dev.azure.com/{org}/{project}"
            f"/_apis/testplan/plans"
            f"?filterActivePlans=true"
            f"&includePlanDetails=false"
            f"&api-version=7.1"
        )

        if continuation_token:
            url += f"&continuationToken={continuation_token}"

        response = session.get(url, timeout=30)
        if response.status_code != 200:
            return [], response.status_code

        plans.extend(response.json().get("value", []))
        continuation_token = response.headers.get("x-ms-continuationtoken")

        if not continuation_token:
            break

    normalized_plans = [
        {
            "id": int(plan["id"]),
            "name": plan.get("name", f"Test Plan {plan['id']}")
        }
        for plan in plans
        if "id" in plan
    ]

    normalized_plans.sort(key=lambda plan: plan["name"].lower())
    return normalized_plans, None


# =========================
# Carga de querys
# =========================

@st.cache_data(ttl=1800, show_spinner=False)
def load_queries(project, pat):

    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)

    url = (
        f"https://dev.azure.com/{org}/{project}"
        f"/_apis/wit/queries"
        f"?$depth=2"
        f"&api-version=7.1"
    )

    response = session.get(url, timeout=30)

    if response.status_code != 200:
        st.error(f"Error cargando queries: HTTP {response.status_code}")

        try:
            st.json(response.json())
        except:
            st.text(response.text)

        return []


    queries = []

    def walk(node, path=""):

        current_name = node.get("name", "")

        if not node.get("isFolder", False):
            queries.append({
                "id": node["id"],
                "name": f"{path}/{current_name}" if path else current_name
            })

        for child in node.get("children", []):
            next_path = (
                f"{path}/{current_name}"
                if path else current_name
            )
            walk(child, next_path)

    root = response.json()



    for c in root.get("children", [])[:10]:
        st.write({
        "name": c.get("name"),
        "isFolder": c.get("isFolder"),
        "has_children": "children" in c,
        "id": c.get("id")
    })

    for child in root.get("value", []):
        walk(child)

    return sorted(
        queries,
        key=lambda q: q["name"].lower()
    )


# =========================
# LOGIN / CONFIG SCREEN
# =========================

if "configured" not in st.session_state:
    st.session_state.configured = False

if "test_plans" not in st.session_state:
    st.session_state.test_plans = []

if "queries" not in st.session_state:
    st.session_state.queries = []

if not st.session_state.configured:

    st.markdown("""
    <div style="
    background:#111827;
    padding:25px;
    border-radius:15px;
    border:1px solid #1f2937;
    ">
        <h2 style="color:white;text-align:center;">
        🚀 QA Dashboard Setup
        </h2>
    </div>
    """, unsafe_allow_html=True)

    pat_input = st.text_input(
        "Azure DevOps PAT",
        type="password"
    )

    project_input = st.text_input(
        "Project Name",
        value=st.session_state.get("setup_project")
    )

    if st.button("Search Test Plans"):
        st.session_state.setup_project = project_input
        st.session_state.setup_pat = pat_input

        if not pat_input.strip():
            st.warning("Enter a PAT first.")
            st.session_state.test_plans = []
        else:
            with st.spinner("Loading Azure DevOps data..."):

                plans, error_status = load_test_plans(project_input,pat_input)

                queries = load_queries(project_input,pat_input)

            st.session_state.test_plans = plans
            st.session_state.queries = queries

            if error_status:
                st.error(f"Could not load test plans. Azure DevOps returned HTTP {error_status}.")
            elif not plans:
                st.warning("No active test plans found for this project.")

    selected_plan = None

    if st.session_state.test_plans:
        selected_plan = st.selectbox(
            "Test Plan",
            options=st.session_state.test_plans,
            format_func=lambda plan: f"{plan['name']} ({plan['id']})"
        )
    selected_query = None

    if st.session_state.queries:
        selected_query = st.selectbox(
        "Bug Query",
        options=st.session_state.queries,
        format_func=lambda q: q["name"]
    )

    if st.button("Load Dashboard", disabled=(
        selected_plan is None
        or selected_query is None
    )):
        st.session_state.pat = pat_input
        st.session_state.project = project_input

        st.session_state.plan_id = int(selected_plan["id"])
        st.session_state.plan_name = selected_plan["name"]

        st.session_state.query_id = selected_query["id"]
        st.session_state.query_name = selected_query["name"]

        st.session_state.configured = True
        st.rerun()

    st.stop()

    
pat = st.session_state.pat
project = st.session_state.project
plan_id = st.session_state.plan_id
query_id = st.session_state.query_id

# =========================
# reiniciar streamlit
# =========================

st.markdown("<div style='margin-top:32px;'></div>", unsafe_allow_html=True)
top_left, sync_col, config_col = st.columns([7.4, 1.1, 1.3])

with sync_col:
    if st.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

with config_col:
    if st.button("Change Config", use_container_width=True):
        st.cache_data.clear()
        st.session_state.configured = False

        for key in ["pat", "project", "plan_id"]:
            if key in st.session_state:
                del st.session_state[key]

        st.rerun()

# =========================
# DATA
# =========================
@st.cache_data(ttl=1800, show_spinner=False)
def load_data(project, plan_id, pat):

    from requests.adapters import HTTPAdapter

    adapter = HTTPAdapter(
        pool_connections=100,
        pool_maxsize=100
    )

    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)
    session.mount("https://", adapter)

    url = (
        f"https://dev.azure.com/{org}/{project}"
        f"/_apis/testplan/Plans/{plan_id}/Suites"
        f"?api-version=7.1-preview.1"
    )

    response = session.get(url, timeout=30)
    if response.status_code != 200:
        return pd.DataFrame(columns=[
            "suite_id", "suite", "passed", "failed", "notrun",
            "Test Points", "Run %", "Pass %", "Fail %"
        ])

    suites = response.json().get("value", [])

    def normalize_outcome(point):
        results = point.get("results") or {}
        outcome = (
            str(results.get("outcome", "notrun"))
            .strip()
            .lower()
            .replace(" ", "")
        )

        if outcome in ["", "notrun", "unspecified", "none"]:
            return "notrun"

        if outcome not in ["passed", "failed"]:
            return "notrun"

        return outcome

    def pct(numerator, denominator):
        if not denominator:
            return "0"

        value = int((numerator / denominator * 100) * 10) / 10
        return f"{value:.1f}".rstrip("0").rstrip(".")

    def get_suite_summary(suite):
        suite_id = suite["id"]
        suite_name = suite["name"]

        url_points = (
            f"https://dev.azure.com/{org}/{project}"
            f"/_apis/testplan/Plans/{plan_id}"
            f"/Suites/{suite_id}/TestPoint"
            f"?api-version=7.1-preview.2"
        )

        with requests.Session() as local:
            local.auth = HTTPBasicAuth('', pat)
            local.mount("https://", adapter)

            response = local.get(url_points, timeout=30)

        if response.status_code != 200:
            points = []
        else:
            points = response.json().get("value", [])

        counts = {"passed": 0, "failed": 0, "notrun": 0}
        for point in points:
            counts[normalize_outcome(point)] += 1

        test_points = counts["passed"] + counts["failed"] + counts["notrun"]
        executed = counts["passed"] + counts["failed"]

        return {
            "suite_id": suite_id,
            "suite": suite_name,
            "passed": counts["passed"],
            "failed": counts["failed"],
            "notrun": counts["notrun"],
            "Test Points": test_points,
            "Run %": pct(executed, test_points),
            "Pass %": pct(counts["passed"], executed),
            "Fail %": pct(counts["failed"], executed),
        }

    workers = max(1, min(65, len(suites)))

    with ThreadPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(get_suite_summary, suites))

    return pd.DataFrame(rows, columns=[
        "suite_id", "suite", "passed", "failed", "notrun",
        "Test Points", "Run %", "Pass %", "Fail %"
    ])
@st.cache_data(ttl=1800)
def load_bugs(project, pat, queries):

    columns = ["ID", "Title", "State", "Priority"]

    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)

    wiql_url = (
    f"https://dev.azure.com/{org}/{project}"
    f"/_apis/wit/wiql/{queries}"
    f"?api-version=7.1"
)
    st.write(wiql_url)

    response = session.get(
    wiql_url,
    timeout=30
)

    if response.status_code != 200:
        return pd.DataFrame(columns=columns)

    ids = [
        str(x["id"])
        for x in response.json().get("workItems", [])
    ]

    if not ids:
        return pd.DataFrame(columns=columns)

    detail_url = (
        f"https://dev.azure.com/{org}"
        f"/_apis/wit/workitems"
        f"?ids={','.join(ids[:200])}"
        f"&fields=System.Id,System.Title,System.State,Microsoft.VSTS.Common.Priority"
        f"&api-version=7.1"
    )

    response = session.get(detail_url, timeout=30)

    if response.status_code != 200:
        return pd.DataFrame(columns=columns)

    items = response.json().get("value", [])

    return pd.DataFrame([
        {
            "ID": item["id"],
            "Title": item["fields"].get("System.Title", ""),
            "State": item["fields"].get("System.State", ""),
            "Priority": item["fields"].get(
                "Microsoft.VSTS.Common.Priority",
                "N/A"
            )
        }
        for item in items
    ], columns=columns)
with st.spinner("Loading Azure DevOps data..."):

    with ThreadPoolExecutor(max_workers=2) as executor:

        future_data = executor.submit(
            load_data,
            project,
            plan_id,
            pat
        )

        future_bugs = executor.submit(
            load_bugs,
            project,
            pat,
            query_id
        )

        df = future_data.result()
        bugs_df = future_bugs.result()

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

# =========================
# STYLE (MODERNO DARK UI)
# =========================



st.markdown("""
<style>
body {
    background-color: #0b1220;
}
.block-container {
    padding-top: 2rem;
}
.card {
    background-color: #111827;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #1f2937;
    text-align: center;
}
.title {
    font-size: 28px;
    font-weight: 700;
    color: white;
}
.subtitle {
    color: #94a3b8;
    margin-bottom: 20px;
}
.metric-value {
    font-size: 22px;
    font-weight: bold;
    color: white;
}
.metric-label {
    color: #94a3b8;
    font-size: 12px;
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
