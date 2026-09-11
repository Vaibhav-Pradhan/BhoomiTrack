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

# Add Land Record
@app.route("/add-land", methods=["GET", "POST"])
def add_land():

    if request.method == "POST":

        project_id = request.form["project_id"]
        survey_number = request.form["survey_number"]
        village = request.form["village"]
        district = request.form["district"]
        state = request.form["state"]
        area = request.form["area"]
        land_type = request.form["land_type"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        acquisition_status = request.form["acquisition_status"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO land
            (
                project_id,
                survey_number,
                village,
                district,
                state,
                area,
                land_type,
                latitude,
                longitude,
                acquisition_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                project_id,
                survey_number,
                village,
                district,
                state,
                area,
                land_type,
                latitude,
                longitude,
                acquisition_status
            )
        )

        connection.commit()
        connection.close()

        return redirect("/land")

    return render_template("add_land.html")

# Land Owners page
@app.route("/owners")
def owners():

    connection = get_db_connection()

    owners = connection.execute("""
        SELECT *
        FROM landowners
        ORDER BY owner_id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "owners.html",
        owners=owners
    )

# Add Land Owner
@app.route("/add-owner", methods=["GET", "POST"])
def add_owner():

    if request.method == "POST":

        land_id = request.form["land_id"]
        owner_name = request.form["owner_name"]
        contact = request.form["contact"]
        ownership_type = request.form["ownership_type"]
        document_status = request.form["document_status"]
        verification_status = request.form["verification_status"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO landowners
            (
                land_id,
                owner_name,
                contact,
                ownership_type,
                document_status,
                verification_status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                land_id,
                owner_name,
                contact,
                ownership_type,
                document_status,
                verification_status
            )
        )

        connection.commit()
        connection.close()

        return redirect("/owners")

    return render_template("add_owner.html")

# Acquisition page
@app.route("/acquisition")
def acquisition():

    connection = get_db_connection()

    acquisition_records = connection.execute("""
        SELECT *
        FROM acquisition
        ORDER BY acquisition_id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "acquisition.html",
        acquisition_records=acquisition_records
    )
# Add Acquisition Record
@app.route("/add-acquisition", methods=["GET", "POST"])
def add_acquisition():

    if request.method == "POST":

        land_id = request.form["land_id"]
        notification_date = request.form["notification_date"]
        verification_date = request.form["verification_date"]
        approval_date = request.form["approval_date"]
        acquisition_date = request.form["acquisition_date"]
        current_stage = request.form["current_stage"]
        remarks = request.form["remarks"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO acquisition
            (
                land_id,
                notification_date,
                verification_date,
                approval_date,
                acquisition_date,
                current_stage,
                remarks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                land_id,
                notification_date,
                verification_date,
                approval_date,
                acquisition_date,
                current_stage,
                remarks
            )
        )

        connection.commit()
        connection.close()

        return redirect("/acquisition")

    return render_template("add_acquisition.html")

# Compensation page
@app.route("/compensation")
def compensation():

    connection = get_db_connection()

    compensation_records = connection.execute("""
        SELECT *
        FROM compensation
        ORDER BY compensation_id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "compensation.html",
        compensation_records=compensation_records
    )

# Add Compensation
@app.route("/add-compensation", methods=["GET", "POST"])
def add_compensation():

    if request.method == "POST":

        land_id = request.form["land_id"]
        market_value = request.form["market_value"]
        compensation_amount = request.form["compensation_amount"]
        payment_status = request.form["payment_status"]
        payment_date = request.form["payment_date"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO compensation
            (
                land_id,
                market_value,
                compensation_amount,
                payment_status,
                payment_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                land_id,
                market_value,
                compensation_amount,
                payment_status,
                payment_date
            )
        )

        connection.commit()
        connection.close()

        return redirect("/compensation")

    return render_template("add_compensation.html")

# Documents page
@app.route("/documents")
def documents():

    connection = get_db_connection()

    documents = connection.execute("""
        SELECT *
        FROM documents
        ORDER BY document_id DESC
    """).fetchall()

    connection.close()

    return render_template(
        "documents.html",
        documents=documents
    )
# Add Document
@app.route("/add-document", methods=["GET", "POST"])
def add_document():

    if request.method == "POST":

        land_id = request.form["land_id"]
        document_name = request.form["document_name"]
        document_type = request.form["document_type"]
        document_status = request.form["document_status"]
        upload_date = request.form["upload_date"]

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO documents
            (
                land_id,
                document_name,
                document_type,
                document_status,
                upload_date
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                land_id,
                document_name,
                document_type,
                document_status,
                upload_date
            )
        )

        connection.commit()
        connection.close()

        return redirect("/documents")

    return render_template("add_document.html")

@app.route("/map")
def land_map():

    connection = get_db_connection()

    rows = connection.execute(
        """
        SELECT
            land_id,
            project_id,
            survey_number,
            village,
            district,
            state,
            area,
            land_type,
            latitude,
            longitude,
            acquisition_status
        FROM land
        WHERE latitude IS NOT NULL
        AND longitude IS NOT NULL
        """
    ).fetchall()

    # SQLite Row ko normal Python dictionary mein convert karna
    land_records = [dict(row) for row in rows]

    connection.close()

    return render_template(
        "map.html",
        land_records=land_records
    )
# =========================================================
# REPORTS & ANALYTICS
# =========================================================

@app.route("/reports")
def reports():

    connection = get_db_connection()

    # Total projects
    total_projects = connection.execute(
        "SELECT COUNT(*) FROM projects"
    ).fetchone()[0]

    # Total land
    total_land = connection.execute(
        "SELECT COUNT(*) FROM land"
    ).fetchone()[0]

    # Acquired land
    acquired_land = connection.execute(
        """
        SELECT COUNT(*)
        FROM land
        WHERE acquisition_status IN ('Acquired', 'Completed')
        """
    ).fetchone()[0]

    # Pending land
    pending_land = connection.execute(
        """
        SELECT COUNT(*)
        FROM land
        WHERE acquisition_status NOT IN ('Acquired', 'Completed')
        """
    ).fetchone()[0]

    # Land type statistics
    land_types = connection.execute(
        """
        SELECT land_type, COUNT(*) AS total
        FROM land
        GROUP BY land_type
        """
    ).fetchall()

    connection.close()

    return render_template(
        "reports.html",
        total_projects=total_projects,
        total_land=total_land,
        acquired_land=acquired_land,
        pending_land=pending_land,
        land_types=land_types
    )

# Start Flask
if __name__ == "__main__":

    create_database()

    import_csv_data()

    app.run(debug=True)