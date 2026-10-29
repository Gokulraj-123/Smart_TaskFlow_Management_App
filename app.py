
import sqlite3
from datetime import date

import streamlit as st

#PAGE SETUP
st.set_page_config(
    page_title="TaskFlow",
    page_icon="✅",
    layout="wide"
)

#CUSTOM DESIGN
st.markdown("""
<style>
    .stApp {
        background-color: #F5F7FC;
    }

    h1, h2, h3 {
        color: #172554;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
    }

    div[data-testid="stForm"] {
        background-color: white;
        padding: 18px;
        border: 1px solid #E5E7EB;
        border-radius: 14px;
    }

    .hero {
        background: linear-gradient(120deg, #312E81, #6366F1);
        padding: 28px;
        border-radius: 18px;
        color: white;
        margin-bottom: 20px;
    }

    .hero h2 {
        color: white;
        margin-bottom: 6px;
    }

    .hero p {
        color: #E0E7FF;
    }

    div.stButton > button[kind="primary"] {
        background-color: #4F46E5;
        border-color: #4F46E5;
    }
</style>
""", unsafe_allow_html=True)

#DATABASE SETUP
DB_FILE = "tasks.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def create_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                priority TEXT NOT NULL,
                due_date TEXT,
                completed INTEGER DEFAULT 0
            )
        """)


def get_tasks():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        rows = connection.execute("""
            SELECT * FROM tasks
            ORDER BY completed ASC, id DESC
        """).fetchall()

        return [dict(row) for row in rows]


def add_task(title, priority, due_date):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO tasks (title, priority, due_date)
            VALUES (?, ?, ?)
        """, (title, priority, due_date))


def update_task(task_id, title, priority, due_date):
    with get_connection() as connection:
        connection.execute("""
            UPDATE tasks
            SET title = ?, priority = ?, due_date = ?
            WHERE id = ?
        """, (title, priority, due_date, task_id))


def set_completed(task_id, completed):
    with get_connection() as connection:
        connection.execute("""
            UPDATE tasks
            SET completed = ?
            WHERE id = ?
        """, (int(completed), task_id))


def delete_task(task_id):
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )


create_database()

#SIDEBAR NAVIGATION
st.sidebar.title("✅ TaskFlow")
st.sidebar.caption("Your personal productivity space")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "My Tasks"]
)

st.sidebar.divider()
st.sidebar.info(
    "Tip: Give important tasks a deadline "
    "and a priority."
)

#ADD TASK FORM
st.title("TaskFlow")
st.caption("Plan your work. Track your progress. Get things done.")

with st.expander("＋ Create a new task", expanded=True):
    with st.form("create_task", clear_on_submit=True):

        title = st.text_input(
            "Task name",
            placeholder="Example: Learn Python functions"
        )

        col1, col2 = st.columns(2)

        with col1:
            priority = st.selectbox(
                "Priority",
                ["Low", "Medium", "High"]
            )

        with col2:
            due = st.date_input(
                "Due date",
                value=None,
                format="YYYY-MM-DD"
            )

        submitted = st.form_submit_button(
            "Add task",
            type="primary",
            use_container_width=True
        )

        if submitted:
            if title.strip():
                due_text = due.isoformat() if due else None

                add_task(
                    title.strip(),
                    priority,
                    due_text
                )

                st.success("Task saved!")
                st.rerun()
            else:
                st.warning("Please enter a task name.")

#LOAD TASKS AND CALCULATE STATISTICS
tasks = get_tasks()

today = date.today().isoformat()

total = len(tasks)

completed = sum(
    task["completed"] for task in tasks
)

active = total - completed

overdue = sum(
    1 for task in tasks
    if not task["completed"]
    and task["due_date"]
    and task["due_date"] < today
)

progress = completed / total if total else 0

#DASHBOARD PAGE
if page == "Dashboard":

    st.markdown("""
    <div class="hero">
        <h2>Your day, organized.</h2>
        <p>Small steps every day lead to big results.</p>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("All tasks", total)
    m2.metric("Active", active)
    m3.metric("Completed", completed)
    m4.metric("Overdue", overdue)

    st.subheader("Your progress")

    st.progress(progress)

    st.write(
        f"**{progress * 100:.0f}% complete** "
        f"· {completed} of {total} tasks finished"
    )

    if total and completed == total:
        st.success("Amazing! You completed every task.")

    st.divider()
    st.subheader("Recent tasks")

    if not tasks:
        st.info("Your workspace is empty. Create your first task above.")

    for task in tasks[:5]:
        col1, col2, col3 = st.columns([5, 2, 2])

        with col1:
            if task["completed"]:
                st.write(f"~~{task['title']}~~")
            else:
                st.write(task["title"])

        with col2:
            st.caption(
                "Completed" if task["completed"] else "In progress"
            )

        with col3:
            st.caption(
                f"{task['priority']} priority"
            )

    st.caption("Showing up to five tasks. Open My Tasks to manage everything.")

#TASK MANAGEMENT PAGE

elif page == "My Tasks":

    st.subheader("Manage your tasks")

    search = st.text_input(
        "🔎 Search tasks",
        placeholder="Type a task name..."
    )

    col1, col2 = st.columns(2)

    with col1:
        status_filter = st.selectbox(
            "Status",
            ["All", "Active", "Completed", "Overdue"]
        )

    with col2:
        priority_filter = st.selectbox(
            "Priority",
            ["All", "High", "Medium", "Low"]
        )

    filtered_tasks = []

    for task in tasks:

        if search.lower() not in task["title"].lower():
            continue

        if status_filter == "Active" and task["completed"]:
            continue

        if status_filter == "Completed" and not task["completed"]:
            continue

        is_overdue = (
            not task["completed"]
            and task["due_date"] is not None
            and task["due_date"] < today
        )

        if status_filter == "Overdue" and not is_overdue:
            continue

        if (
            priority_filter != "All"
            and task["priority"] != priority_filter
        ):
            continue

        filtered_tasks.append(task)

    st.caption(f"{len(filtered_tasks)} matching tasks")

    if not filtered_tasks:
        st.info("No matching tasks. Try changing your filters.")

    for task in filtered_tasks:

        with st.container(border=True):

            left, right = st.columns([5, 1])

            with left:
                new_completed = st.checkbox(
                    task["title"],
                    value=bool(task["completed"]),
                    key=f"completed_{task['id']}"
                )

                if new_completed != bool(task["completed"]):
                    set_completed(task["id"], new_completed)
                    st.rerun()

                due_label = task["due_date"] or "No deadline"

                if (
                    not task["completed"]
                    and task["due_date"]
                    and task["due_date"] < today
                ):
                    st.error(f"Overdue · Due {due_label}")
                else:
                    st.caption(
                        f"Due: {due_label} · "
                        f"Priority: {task['priority']}"
                    )

            with right:
                if st.button(
                    "Delete",
                    key=f"delete_{task['id']}"
                ):
                    delete_task(task["id"])
                    st.rerun()

            with st.expander("Edit task"):

                with st.form(f"edit_{task['id']}"):

                    edited_title = st.text_input(
                        "Task name",
                        value=task["title"],
                        key=f"title_{task['id']}"
                    )

                    edited_priority = st.selectbox(
                        "Priority",
                        ["Low", "Medium", "High"],
                        index=["Low", "Medium", "High"].index(
                            task["priority"]
                        ),
                        key=f"priority_{task['id']}"
                    )

                    old_due = (
                        date.fromisoformat(task["due_date"])
                        if task["due_date"]
                        else None
                    )

                    edited_due = st.date_input(
                        "Due date",
                        value=old_due,
                        key=f"due_{task['id']}",
                        format="YYYY-MM-DD"
                    )

                    save = st.form_submit_button("Save changes")

                    if save:
                        if edited_title.strip():
                            due_text = (
                                edited_due.isoformat()
                                if edited_due
                                else None
                            )

                            update_task(
                                task["id"],
                                edited_title.strip(),
                                edited_priority,
                                due_text
                            )

                            st.success("Changes saved!")
                            st.rerun()
                        else:
                            st.warning("Task name cannot be empty.")

# FOOTER
st.sidebar.divider()
st.sidebar.caption("TaskFlow · Built with Python")
