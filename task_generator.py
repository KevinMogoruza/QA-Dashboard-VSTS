import streamlit as st

from azure_devops import create_task, load_work_item



PROD_SPANISH_TASKS = [
    {
        "title": "TST PROD - ANALISIS - {id}",
        "description": (
            "Realizar un analisis tecnico detallado para identificar los "
            "requisitos, restricciones y dependencias criticas para la "
            "historia de usuario {id}."
        ),
        "activity": "Requirements",
        "effort": 2,
    },
    {
        "title": "TST PROD - EXPLORATORIO - {id}",
        "description": (
            "Llevar a cabo pruebas exploratorias y prototipado técnico con "
            "el fin de validar la viabilidad de la solución propuesta para "
            "la historia de usuario {id}."
        ),
        "activity": "Requirements",
        "effort": 2,
    },
    {
        "title": "TST PROD - DISEÑO EN DEVOPS - {id}",
        "description": (
            "Desarrollar y estructurar el diseño tecnico integral dentro del "
            "entorno de DevOps para cubrir las necesidades arquitectonicas "
            "de la historia de usuario {id}."
        ),
        "activity": "Design",
        "effort": 1,
    },
    {
        "title": "TST PROD - DISENO EN DBX - {id}",
        "description": (
            "Crear el diseño tecnico detallado y la arquitectura de datos en "
            "Databricks para la implementacion efectiva de la solucion de la "
            "historia de usuario {id}."
        ),
        "activity": "Design",
        "effort": 4,
    },
    {
        "title": "TST PROD - PRUEBAS - {id}",
        "description": (
            "Diseñar, implementar y ejecutar la suite de casos de prueba "
            "automatizados y manuales para asegurar la calidad y funcionalidad "
            "optima de la historia de usuario {id}."
        ),
        "activity": "Testing",
        "effort": 6,
    },
    {
        "title": "TST PROD - DOCUMENTACIÓN - {id}",
        "description": (
            "Preparar y redactar la documentación técnica y funcional "
            "detallada requerida para el soporte, despliegue y mantenimiento "
            "técnico de la historia de usuario {id}."
        ),
        "activity": "Documentation",
        "effort": 2,
    },
    {
        "title": "TST PROD - GESTIÓN DE BUGS - {id}",
        "description": (
            "Identificar, reportar, priorizar y mitigar los defectos o "
            "desviaciones encontradas durante las fases de desarrollo y "
            "pruebas de la historia de usuario {id}."
        ),
        "activity": "Testing",
        "effort": 1,
    },
    {
        "title": "TST PROD - PRESENTACION USUARIO FINAL - {id}",
        "description": (
            "Planificar y ejecutar la sesion de demostracion o sprint review "
            "ante los usuarios finales, validando los criterios de aceptacion "
            "y el valor entregado en la historia de usuario {id}."
        ),
        "activity": "Documentation",
        "effort": 1,
    },
]

PROD_ENGLISH_TASKS = [
    {
        "title": "TST PROD - ANALYSIS - {id}",
        "description": (
            "Perform a detailed technical analysis to identify requirements, "
            "constraints, and critical dependencies for user story {id}."
        ),
        "activity": "Requirements",
        "effort": 2,
    },
    {
        "title": "TST PROD - EXPLORATORY - {id}",
        "description": (
            "Perform exploratory testing and technical prototyping to validate "
            "the feasibility of the proposed solution for user story {id}."
        ),
        "activity": "Requirements",
        "effort": 2,
    },
    {
        "title": "TST PROD - DEVOPS DESIGN - {id}",
        "description": (
            "Develop and structure the technical design in DevOps to cover the "
            "architectural needs of user story {id}."
        ),
        "activity": "Design",
        "effort": 1,
    },
    {
        "title": "TST PROD - DBX DESIGN - {id}",
        "description": (
            "Create the detailed technical design and data architecture in "
            "Databricks for the implementation of user story {id}."
        ),
        "activity": "Design",
        "effort": 4,
    },
    {
        "title": "TST PROD - TESTING - {id}",
        "description": (
            "Design, implement, and execute automated and manual test cases to "
            "ensure the expected quality and functionality of user story {id}."
        ),
        "activity": "Testing",
        "effort": 6,
    },
    {
        "title": "TST PROD - DOCUMENTATION - {id}",
        "description": (
            "Prepare the required technical and functional documentation for "
            "support, deployment, and maintenance of user story {id}."
        ),
        "activity": "Documentation",
        "effort": 2,
    },
    {
        "title": "TST PROD - BUG MANAGEMENT - {id}",
        "description": (
            "Identify, report, prioritize, and mitigate defects found during "
            "development and testing phases for user story {id}."
        ),
        "activity": "Testing",
        "effort": 1,
    },
    {
        "title": "TST PROD - END USER PRESENTATION - {id}",
        "description": (
            "Plan and execute the demo or sprint review with end users, "
            "validating acceptance criteria and delivered value for user "
            "story {id}."
        ),
        "activity": "Documentation",
        "effort": 1,
    },
]

TST_SPANISH_TASKS = [
    {
        "title": "TST - Analisis - {title} - {id}",
        "description": (
            "Descripción breve de lo que se va a probar"
        ),
        "activity": "Requirements",
        "effort": 1,
    },
    {
        "title": "TST - Diseño de casos de pruebas - {title} - {id}",
        "description": (
            "Los casos de prueba realizados están disponibles en la siguiente "
            "dirección: {reference_url}"
        ),
        "activity": "Design",
        "effort": 1,
    },
    {
        "title": "TST - Ejecución de casos de pruebas - {title} - {id}",
        "description": (
            "Se ejecutarán los casos de pruebas mencionados en la tarea Diseño "
            "de Casos de Pruebas para esta Historia, se actualizará el test "
            "Plan y las gráficas correspondientes: {reference_url}"
        ),
        "activity": "Testing",
        "effort": 1,
    },
    {
        "title": "TST - Documentación de casos de pruebas - {title} - {id}",
        "description": (
            "Se documentaran los casos de pruebas con las evidencias recolectas "
            "durante la fase de ejecución de pruebas, las evidencias se podrán "
            "encontrar en la siguiente dirección: {reference_url}"
        ),
        "activity": "Documentation",
        "effort": 1,
    },
]

TST_ENGLISH_TASKS = [
    {
        "title": "TST - Analysis - {title} - {id}",
        "description": (
            "Brief description of what will be tested. The completed test case "
            "designs are available at the following address: {reference_url}"
        ),
        "activity": "Requirements",
        "effort": 1,
    },
    {
        "title": "TST - Test case design - {title} - {id}",
        "description": (
            "The completed test cases are available at the following address: "
            "{reference_url}"
        ),
        "activity": "Design",
        "effort": 1,
    },
    {
        "title": "TST - Test case execution - {title} - {id}",
        "description": (
            "The test cases mentioned in the Test Case Design task for this "
            "story will be executed. The test plan and the corresponding "
            "charts will be updated: {reference_url}"
        ),
        "activity": "Testing",
        "effort": 1,
    },
    {
        "title": "TST - Test case documentation - {title} - {id}",
        "description": (
            "The test cases will be documented with the evidence collected "
            "during the test execution phase. The evidence will be available "
            "at the following address: {reference_url}"
        ),
        "activity": "Documentation",
        "effort": 1,
    },
]

TST_ENGLISH_QA_TASKS = [
    {
        "title": "TST - Analysis - {title} - {id}",
        "description": (
            "Brief description of what will be tested. The completed test case "
            "designs are available at the following address: {reference_url}"
        ),
        "activity": "Requirements",
        "effort": 1,
    },
    {
        "title": "TST - Test case design - {title} - {id}",
        "description": (
            "The completed test cases are available at the following address: "
            "{reference_url}"
        ),
        "activity": "Design",
        "effort": 1,
    },
    {
        "title": "TST - Test case execution - {title} - {id}",
        "description": (
            "The test cases mentioned in the Test Case Design task for this "
            "story will be executed. The test plan and the corresponding "
            "charts will be updated: {reference_url}"
        ),
        "activity": "Testing",
        "effort": 1,
    },
]

TST_SPANISH_QA_TASKS = [
    {
        "title": "TST - Analisis - {title} - {id}",
        "description": (
            "Descripción breve de lo que se va a probar"
        ),
        "activity": "Requirements",
        "effort": 1,
    },
    {
        "title": "TST - Diseño de casos de pruebas - {title} - {id}",
        "description": (
            "Los casos de prueba realizados están disponibles en la siguiente "
            "dirección: {reference_url}"
        ),
        "activity": "Design",
        "effort": 1,
    },
    {
        "title": "TST - Ejecución de casos de pruebas - {title} - {id}",
        "description": (
            "Se ejecutarán los casos de pruebas mencionados en la tarea Diseño "
            "de Casos de Pruebas para esta Historia, se actualizará el test "
            "Plan y las gráficas correspondientes: {reference_url}"
        ),
        "activity": "Testing",
        "effort": 1,
    },
]

TASK_CATALOGS = {
    "DATOS - TST PROD - Español": PROD_SPANISH_TASKS,
    "DATOS - TST PROD - English": PROD_ENGLISH_TASKS,
    "QA General - TST - Español": TST_SPANISH_TASKS,
    "QA General - TST - English": TST_ENGLISH_TASKS,
    "QA Iniciativa - TST - English": TST_ENGLISH_QA_TASKS,
    "QA Iniciativa - TST - Español": TST_SPANISH_QA_TASKS,

}



def _render_tag_editor():

    if "task_tags" not in st.session_state:
        st.session_state.task_tags = []

    with st.form("tag_form", clear_on_submit=True):

        tag_col, add_col = st.columns([4,1])

        with tag_col:
            new_tag = st.text_input("Add tag")

        with add_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "Add",
                use_container_width=True
            )

        if submitted:

            clean_tag = new_tag.strip()

            if not clean_tag:
                st.warning("Enter a tag.")

            elif clean_tag in st.session_state.task_tags:
                st.warning("Tag already exists.")

            else:
                st.session_state.task_tags.append(clean_tag)

    if not st.session_state.task_tags:
        return ""

    for index, tag in enumerate(st.session_state.task_tags):

        tag_label, remove_button = st.columns([5,1])

        tag_label.markdown(f"`{tag}`")

        if remove_button.button("Remove", key=f"remove_tag_{index}"):

            st.session_state.task_tags.pop(index)
            st.rerun()

    return "; ".join(st.session_state.task_tags)


def _render_story_editor():
    if "story_ids" not in st.session_state:
        st.session_state.story_ids = []

    with st.form("story_form", clear_on_submit=True):

        id_col, add_col = st.columns([4,1])

        with id_col:
            new_story = st.text_input("User Story ID")

        with add_col:
            st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button(
                "Add Story",
                use_container_width=True
            )

        if submitted:

            value = new_story.strip()

            if not value:
                st.warning("Enter a Story ID.")

            elif not value.isdigit():
                st.warning("Story ID must be numeric.")

            else:
                story = int(value)

                if story in st.session_state.story_ids:
                    st.warning("Story ID already added.")

                else:
                    st.session_state.story_ids.append(story)

    if not st.session_state.story_ids:
        return []

    for i, story in enumerate(st.session_state.story_ids):

        c1, c2 = st.columns([5,1])

        c1.markdown(f"`{story}`")

        if c2.button("Remove", key=f"remove_story_{i}"):

            st.session_state.story_ids.pop(i)
            st.rerun()

    return st.session_state.story_ids


def _format_template(value, context):
    return value.format_map(context)


def _preview_tasks(templates):
    preview_context = {
        "id": "ID",
        "title": "HIST",
        "reference_url": "URL",
    }
    preview_rows = [
        {
            "Title": _format_template(template["title"], preview_context),
            "Activity": template["activity"],
            "Effort": template["effort"],
        }
        for template in templates
    ]
    st.dataframe(preview_rows, use_container_width=True, hide_index=True)


def render_task_generator(project, pat):
    st.title("Task Generator")

    st.markdown(
        """
        <div style="
        background:#111827;
        padding:15px;
        border-radius:15px;
        border:1px solid #1f2937;
        margin-bottom:15px;
        ">
            <h3 style="color:white;margin:0;text-align:center;">
            Automatic Technical Tasks
            </h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    catalog_name = st.selectbox(
        "Task catalog",
        list(TASK_CATALOGS.keys())
    )
    templates = TASK_CATALOGS[catalog_name]

    email = st.text_input(
    "Assigned To (Email)",
    placeholder="usuario@copaair.com",
    help="Correo del usuario al que se asignarán las tareas."
)

    story_ids = _render_story_editor()

    reference_url = st.text_input(
        "Reference URL (opcional)",
        help="Dirección URL para las evidencias |OPCIONAL|."
    )

    tags = _render_tag_editor()

    st.divider()
    _preview_tasks(templates)

    submitted = st.button(
        "Generate Tasks",
        type="primary",
        use_container_width=True
    )

    if not submitted:
        return

    if not story_ids:
        st.warning("Please enter at least one user story ID.")
        return
    
    if not email.strip():
        st.warning("Please enter an email.")
        return

    results = []
    errors = []

    with st.spinner("Creating automatic tasks in Azure DevOps..."):
        for story_id in story_ids:
            story, error_status, error_text = load_work_item(
                project,
                pat,
                story_id
            )

            if error_status:
                errors.append({
                    "Story": story_id,
                    "Task": "Story lookup",
                    "Error": f"HTTP {error_status}: {error_text}",
                })
                continue

            assigned_to = email.strip()
            context = {
                "id": story_id,
                "title": story["title"],
                "reference_url": reference_url.strip(),
            }

            for template in templates:
                task, task_error_status, task_error_text = create_task(
                    project=project,
                    pat=pat,
                    title=_format_template(template["title"], context),
                    description=_format_template(template["description"], context),
                    assigned_to=assigned_to,
                    activity=template["activity"],
                    effort=template["effort"],
                    area_path=story["area_path"],
                    iteration_path=story["iteration_path"],
                    tags=tags,
                    parent_id=story_id
                )

                if task_error_status:
                    errors.append({
                        "Story": story_id,
                        "Task": _format_template(template["title"], context),
                        "Error": f"HTTP {task_error_status}: {task_error_text}",
                    })
                    continue

                results.append({
                    "Story": story_id,
                    "Task ID": task["id"],
                    "Title": task["title"],
                    "Assigned To": assigned_to,
                    "Area Path": story["area_path"],
                    "Iteration Path": story["iteration_path"],
                    "URL": task["url"],
                })

    if results:
        st.success(f"Created {len(results)} tasks.")
        st.dataframe(results, use_container_width=True, hide_index=True)
        if st.button("OK", type="primary"):
            st.session_state.story_ids = []
            st.session_state.task_tags = []
            st.rerun()

    if errors:
        st.error(f"{len(errors)} errors found while creating tasks.")
        st.dataframe(errors, use_container_width=True, hide_index=True)

    if results and not errors:
        st.session_state.story_ids = []
        st.session_state.task_tags = []
