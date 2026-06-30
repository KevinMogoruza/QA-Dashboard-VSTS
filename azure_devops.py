import streamlit as st
import pandas as pd
import requests

from requests.auth import HTTPBasicAuth
from concurrent.futures import ThreadPoolExecutor
from config import org, CACHE_TIME


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

@st.cache_data(ttl=CACHE_TIME, show_spinner=False)
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




    for child in root.get("value", []):
        walk(child)

    return sorted(
        queries,
        key=lambda q: q["name"].lower()
    )



# =========================
# Funcion para cargar proyectos
# =========================
@st.cache_data(ttl=CACHE_TIME)
def load_projects(pat):

    session = requests.Session()
    session.auth = HTTPBasicAuth("", pat)

    url = (
        f"https://dev.azure.com/{org}"
        f"/_apis/projects"
        f"?api-version=7.1"
    )

    response = session.get(url, timeout=30)

    if response.status_code != 200:
        return []

    projects = response.json().get("value", [])

    return sorted(
        projects,
        key=lambda p: p["name"].lower()
    )

# =========================
# DATA
# =========================
@st.cache_data(ttl=CACHE_TIME, show_spinner=False)
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
@st.cache_data(ttl=CACHE_TIME)
def load_bugs(project, pat, queries):

    columns = ["ID", "Title", "State", "Priority"]

    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)

    wiql_url = (
    f"https://dev.azure.com/{org}/{project}"
    f"/_apis/wit/wiql/{queries}"
    f"?api-version=7.1"
)

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


def create_task(
    project,
    pat,
    title,
    description="",
    assigned_to="",
    activity="",
    effort=None,
    priority=None,
    area_path="",
    iteration_path="",
    tags="",
    parent_id=None
):
    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)

    operations = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": title.strip()
        }
    ]

    optional_fields = {
        "/fields/System.Description": description.strip(),
        "/fields/System.AssignedTo": assigned_to.strip(),
        "/fields/System.AreaPath": area_path.strip(),
        "/fields/System.IterationPath": iteration_path.strip(),
        "/fields/System.Tags": tags.strip(),
        "/fields/Microsoft.VSTS.Common.Activity": activity.strip(),
        "/fields/System.State": "To Do",
    }

    for path, value in optional_fields.items():
        if value:
            operations.append({
                "op": "add",
                "path": path,
                "value": value
            })

    if priority:
        operations.append({
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Priority",
            "value": int(priority)
        })

    if effort is not None:
        operations.extend([
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.OriginalEstimate",
                "value": float(effort)
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.RemainingWork",
                "value": float(effort)
            }
        ])

    if parent_id:
        operations.append({
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Reverse",
                "url": (
                    f"https://dev.azure.com/{org}"
                    f"/_apis/wit/workItems/{int(parent_id)}"
                ),
                "attributes": {
                    "comment": "Tarea tecnica creada automaticamente."
                }
            }
        })

    url = (
        f"https://dev.azure.com/{org}/{project}"
        f"/_apis/wit/workitems/$Task"
        f"?api-version=7.1"
    )

    response = session.patch(
        url,
        json=operations,
        headers={
            "Content-Type": "application/json-patch+json"
        },
        timeout=30
    )

    if response.status_code not in (200, 201):
        return None, response.status_code, response.text

    task = response.json()
    return {
        "id": task.get("id"),
        "url": task.get("_links", {}).get("html", {}).get("href", ""),
        "title": task.get("fields", {}).get("System.Title", title)
    }, None, None


def load_work_item(project, pat, work_item_id):
    session = requests.Session()
    session.auth = HTTPBasicAuth('', pat)

    fields = ",".join([
        "System.Id",
        "System.Title",
        "System.AreaPath",
        "System.IterationPath",
        "System.AssignedTo",
        "System.Tags",
    ])

    url = (
        f"https://dev.azure.com/{org}/{project}"
        f"/_apis/wit/workitems/{int(work_item_id)}"
        f"?fields={fields}"
        f"&api-version=7.1"
    )

    response = session.get(url, timeout=30)

    if response.status_code != 200:
        return None, response.status_code, response.text

    item = response.json()
    item_fields = item.get("fields", {})
    assigned = item_fields.get("System.AssignedTo", {})

    if isinstance(assigned, dict):
        assigned_to = assigned.get("uniqueName") or assigned.get("displayName", "")
    else:
        assigned_to = str(assigned or "")

    return {
        "id": item.get("id"),
        "title": item_fields.get("System.Title", ""),
        "area_path": item_fields.get("System.AreaPath", ""),
        "iteration_path": item_fields.get("System.IterationPath", ""),
        "assigned_to": assigned_to,
        "tags": item_fields.get("System.Tags", ""),
    }, None, None
