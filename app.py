import streamlit as st
from sqlite_db import (
    create_patient,
    read_patients,
    update_patient,
    delete_patient,
    get_patient,
    get_patient_overtime_data,
    create_tables
)
import pandas as pd
import plotly.express as px
from sql_agent import execute_query

# Initialize the database and create tables if they don't exist
create_tables()

# Streamlit Page Config
st.set_page_config(page_title="CHW Application - Hypertension Management", layout="wide")

# App Title
st.title("CardioMed")
st.subheader("Community Health Worker (CHW) Application")

# Sidebar Navigation
menu = st.sidebar.selectbox("Menu", ["Create Patient", "View Patients", "Track Patient", "Alerts & Checkups"])

# Create Patient
if menu == "Create Patient":
    st.header("Add New Patient")
    with st.form("create_patient_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        contact = st.text_input("Contact")
        bp = st.text_input("Blood Pressure (e.g., 120/80)")
        risk_score = st.slider("Risk Score (0-100)", min_value=0, max_value=100)
        next_appointment = st.date_input("Next Check-Up Appointment")
        submitted = st.form_submit_button("Add Patient")

        if submitted:
            create_patient(name, age, gender, contact, bp, risk_score, next_appointment)
            st.success(f"Patient {name} added successfully!")

# View Patients
elif menu == "View Patients":
    st.header("Patient Records")
    patients = read_patients()
    #st.write(patients)  # Show the raw data for debugging

    if patients:
        df = pd.DataFrame(patients)
        st.dataframe(df)
        #st.write(df)

        # Select patient for details using the correct key for IDs
        patient_id = st.selectbox("Select Patient ID for Details", df["id"])
        selected_patient = get_patient(patient_id)

        if selected_patient:
            st.write(f"**Name:** {selected_patient['name']}")
            st.write(f"**Age:** {selected_patient['age']}")
            st.write(f"**Gender:** {selected_patient['gender']}")
            st.write(f"**Contact:** {selected_patient['contact']}")
            st.write(f"**Blood Pressure:** {selected_patient['bp']}")
            st.write(f"**Risk Score:** {selected_patient['risk_score']}")
            st.write(f"**Next Appointment:** {selected_patient['next_appointment']}")

        # Data Visualization Button
        if st.button("Visualize Patient Data"):
            fig = px.bar(df, x="name", y="risk_score", title="Risk Scores of Patients")
            st.plotly_chart(fig)

        # Connect to Clinician Button
        if st.button("Connect Patient to Clinician"):
            st.info(f"Clinician notified for patient ID {patient_id}.")

        # Chat Interface
        st.subheader("Chat with SQL Agent")
        user_question = st.text_input("Ask a question about the patient database:")
        
        if st.button("Submit"):
            # Call the execute_query function to get the response
            response = execute_query(user_question)
            st.write("CARDIOMED:", response)


# Track Patient
elif menu == "Track Patient":
    st.header("Track Patient Records Over Time")
    patients = read_patients()
    patient_id = st.selectbox("Select Patient ID to Track", [p["id"] for p in patients])
    patient_records = [p for p in patients if p["id"] == patient_id]

    if patient_records:
        patient = patient_records[0]
        st.write(f"**Name:** {patient['name']}")
        st.write(f"**Age:** {patient['age']}")
        st.write(f"**Gender:** {patient['gender']}")
        st.write(f"**Contact:** {patient['contact']}")

        # Update Patient Record
        with st.form("update_patient_form"):
            bp = st.text_input("Update Blood Pressure (e.g., 120/80)")
            risk_score = st.slider("Update Risk Score (0-100)", min_value=0, max_value=100)
            next_appointment = st.date_input("Update Next Check-Up Appointment")
            submitted = st.form_submit_button("Update Patient Record")

            if submitted:
                update_patient(patient_id, bp, risk_score, next_appointment)
                st.success(f"Patient {patient['name']} record updated successfully!")

        # Display Overtime Data
        overtime_data = get_patient_overtime_data(patient_id)
        if overtime_data:
            df = pd.DataFrame(overtime_data)
            st.dataframe(df)

            # Visualize Overtime Data
            fig = px.line(df, x="date", y="risk_score", title="Risk Score Over Time")
            st.plotly_chart(fig)

            fig = px.line(df, x="date", y="bp", title="Blood Pressure Over Time")
            st.plotly_chart(fig)


# Alerts & Checkups
elif menu == "Alerts & Checkups":
    st.header("Manage Alerts & Checkups")
    # Convert current timestamp to date for comparison
    current_timestamp = pd.Timestamp.now()
    
    overdue_patients = [p for p in read_patients() if pd.Timestamp(p["next_appointment"]) < current_timestamp]
    high_risk_patients = [p for p in read_patients() if p["risk_score"] > 85]
    
    if overdue_patients:
        st.warning("The following patients have overdue check-ups:")
        for patient in overdue_patients:
            st.write(f"{patient['name']} (ID: {patient['id']}) - Last Appointment: {patient['next_appointment']}")
    else:
        st.success("No overdue appointments!")

    
    if high_risk_patients:
        st.error("Emergency Alert: Patients with critical risk scores!")
        for patient in high_risk_patients:
            st.write(f"{patient['name']} (ID: {patient['id']}) - Risk Score: {patient['risk_score']}")

    
