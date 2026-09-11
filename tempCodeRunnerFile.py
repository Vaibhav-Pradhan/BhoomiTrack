from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
import os

app = Flask(__name__)


# Database connection
def get_db_connection():
    connection = sqlite3.connect("database.db")

    connection.row_factory = sqlite3.Row

    return connection


# Create database tables
def create_database():

    connection = sqlite3.connect("database.db")

    cursor = connection.cursor()


    # Projects table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS projects (
        project_id INTEGER PRIMARY KEY,
        project_name TEXT,
        project_type TEXT,
        state TEXT,
        district TEXT,
        authority TEXT,
        budget INTEGER,
        status TEXT
    )
    """)


    # Land table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS land (
        land_id INTEGER PRIMARY KEY,
        project_id INTEGER,
        survey_number TEXT,
        village TEXT,
        district TEXT,
        state TEXT,
        area REAL,
        land_type TEXT,
        latitude REAL,
        longitude REAL,
        acquisition_status TEXT
    )
    """)


    # Land owners table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS landowners (
        owner_id INTEGER PRIMARY KEY,
        land_id INTEGER,
        owner_name TEXT,
        contact TEXT,
        ownership_type TEXT,
        document_status TEXT,
        verification_status TEXT
    )
    """)


    # Acquisition table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS acquisition (
        acquisition_id INTEGER PRIMARY KEY,
        land_id INTEGER,
        notification_date TEXT,
        verification_date TEXT,
        approval_date TEXT,
        acquisition_date TEXT,
        current_stage TEXT,
        remarks TEXT
    )
    """)


    # Compensation table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS compensation (
        compensation_id INTEGER PRIMARY KEY,
        land_id INTEGER,
        market_value INTEGER,
        compensation_amount INTEGER,
        payment_status TEXT,
        payment_date TEXT
    )
    """)
    # Documents table

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        document_id INTEGER PRIMARY KEY,
        land_id INTEGER,
        document_name TEXT,
        document_type TEXT,
        document_status TEXT,
        upload_date TEXT
    )
    """)

    connection.commit()

    connection.close()


# Import CSV data
def import_csv_data():

    connection = sqlite3.connect("database.db")


    csv_files = {

        "projects": "dataset/projects.csv",

        "land": "dataset/land.csv",

        "landowners": "dataset/landowners.csv",

        "acquisition": "dataset/acquisition.csv",

        "compensation": "dataset/compensation.csv"

    }


    for table, file_path in csv_files.items():

        if os.path.exists(file_path):

            data = pd.read_csv(file_path)

            data.to_sql(
                table,
                connection,
                if_exists="replace",
                index=False
            )


    connection.close()

# Home page
@app.route("/")
def dashboard():

    connection = get_db_connection()

    total_projects = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    total_land = connection.execute(
        "SELECT COUNT(*) FROM land"
    ).fetchone()[0]

    acquired_land = connection.execute(
        """
        SELECT COUNT(*)
        FROM land
        WHERE acquisition_status IN ('Acquired', 'Completed')
        """
    ).fetchone()[0]

    pending_land = connection.execute(
        """
        SELECT COUNT(*)
        FROM land
        WHERE acquisition_status NOT IN ('Acquired', 'Completed')
        """
    ).fetchone()[0]

    connection.close()

    return render_template(
        "dashboard.html",
        total_projects=total_projects,
        total_land=total_land,
        acquired_land=acquired_land,
        pending_land=pending_land
    )

# =========================================================
# PROJECTS
# =========================================================

@app.route("/projects")
def projects():

    connection = get_db_connection()

    projects = connection.execute(
        "SELECT * FROM projects"
    ).fetchall()

    connection.close()

    return render_template(
        "projects.html",
        projects=projects
    )

# Add Project
@app.route("/add-project", methods=["GET", "POST"])
def add_project():

    if request.method == "POST":

        project_name = request.form["project_name"]
        project_type = request.form["project_type"]
        state = request.form["state"]
        district = request.form["district"]
        authority = request.form["authority"]
        budget = request.form["budget"]
        status = request.form["status"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO projects
            (
                project_name,
                project_type,
                state,
                district,
                authority,
                budget,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_name,
                project_type,
                state,
                district,
                authority,
                budget,
                status
            )
        )

        connection.commit()
        connection.close()

        return redirect("/projects")

    return render_template("add_project.html")


# Land Records page
@app.route("/land")
def land():

    connection = get_db_connection()

    land_records = connection.execute("""
        SELECT *
        FROM land
        ORDER BY land_id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "land.html",
        land_records=land_records
    )
