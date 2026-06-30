import streamlit as st

import plotly.graph_objects as go

from dashboard import render_dashboard
from task_generator import render_task_generator

from concurrent.futures import ThreadPoolExecutor

from styles import load_styles

from azure_devops import (
    load_projects,
    load_test_plans,
    load_queries,
    load_data,
    load_bugs
)

st.set_page_config(
    page_title="QA Dashboard",
    layout="wide"
)

load_styles()

#------------------------------#
#-inicializas el Session State-#
#------------------------------#

if "module" not in st.session_state:
    st.session_state.module = None

if "configured" not in st.session_state:
    st.session_state.configured = False

if "projects" not in st.session_state:
    st.session_state.projects = []

if "test_plans" not in st.session_state:
    st.session_state.test_plans = []

if "queries" not in st.session_state:
    st.session_state.queries = []

#------------------------------#
#-----------Código-------------#
#------------------------------#

if st.session_state.module is None:

    st.title("QA TOOLS")

    if st.button("📊 QA Dashboard"):
        st.session_state.module = "dashboard"
        st.rerun()

    if st.button("📝 Task Generator"):
        st.session_state.module = "tasks"
        st.rerun()

    st.stop()

back_col, _ = st.columns([1,8])

st.divider()

with back_col:
    st.divider()
    if st.button("⬅ Back"):
        st.session_state.clear()
        st.rerun()

if not st.session_state.configured:

    pat = st.text_input(
        "Azure DevOps PAT",
        type="password"
    )

    if st.button("Validate PAT"):

        if not pat.strip():
            st.warning("Please enter your Azure DevOps PAT.")
        else:
            st.session_state.pat = pat
            st.session_state.projects = load_projects(pat)
            if not st.session_state.projects:
                st.error("No projects found or invalid PAT.")

    if st.session_state.projects:

        project = st.selectbox(
        "Project",
        st.session_state.projects,
        format_func=lambda p: p["name"]
    )


        if st.session_state.module == "tasks":
            if st.button("Open Task Generator", disabled=project is None):
                st.session_state.project = project["name"]
                st.session_state.configured = True
                st.rerun()

        elif st.button("Load Test Plans",disabled=project is None):
            with st.spinner("Loading Azure DevOps data..."):


                plans, _ = load_test_plans(
                    project["name"],
                    st.session_state.pat
        )

                queries = load_queries(
                    project["name"],
                    st.session_state.pat
        )
                
            if not plans:
                st.warning("No active Test Plans found.")
            if not queries:
                st.warning("No queries found.")

            st.session_state.test_plans = plans
            st.session_state.queries = queries
            st.session_state.project = project["name"]

    selected_plan = None
    selected_query = None

    if st.session_state.module == "dashboard" and st.session_state.test_plans:

        selected_plan = st.selectbox(
        "Test Plan",
        st.session_state.test_plans,
        format_func=lambda p: p["name"]
    )


    if st.session_state.module == "dashboard" and st.session_state.queries:

        selected_query = st.selectbox(
        "Bug Query",
        st.session_state.queries,
        format_func=lambda q: q["name"]
    )

    if st.session_state.module == "dashboard" and st.button("Load Dashboard",disabled=(
        selected_plan is None or
        selected_query is None
    )
):

        st.session_state.plan_id = selected_plan["id"]
        st.session_state.plan_name = selected_plan["name"]

        st.session_state.query_id = selected_query["id"]
        st.session_state.query_name = selected_query["name"]

        st.session_state.configured = True

        st.rerun()

if not st.session_state.configured:
    st.stop()

if st.session_state.module == "tasks":
    render_task_generator(
        st.session_state.project,
        st.session_state.pat
    )
    st.stop()

with st.spinner("Loading Azure DevOps data..."):

    with ThreadPoolExecutor(max_workers=2) as executor:

        future_data = executor.submit(
            load_data,
            st.session_state.project,
            st.session_state.plan_id,
            st.session_state.pat
        )

        future_bugs = executor.submit(
            load_bugs,
            st.session_state.project,
            st.session_state.pat,
            st.session_state.query_id
        )

        df = future_data.result()
        bugs_df = future_bugs.result()
        st.success("Dashboard loaded!")
        render_dashboard(
    st.session_state.project,
    st.session_state.plan_id,
    df,
    bugs_df
)
        


