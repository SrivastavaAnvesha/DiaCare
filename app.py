import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import sqlite3
from src.models.diabetes_model import predict_diabetes
from src.models.ulcer_model import create_ulcer_model
from src.utils.report_generator import ReportGenerator
from src.database.database_manager import DatabaseManager
import tensorflow as tf
from tensorflow.keras.preprocessing import image as keras_image
from tensorflow.keras.preprocessing import image as keras_image

# Initialize database
db = DatabaseManager('diacare_db.sqlite3')
report_gen = ReportGenerator('reports')

# Load models
@st.cache_resource
def load_models():
    diabetes_model = joblib.load('model/diabetes_model.pkl')
    ulcer_model = tf.keras.models.load_model('model/foot_ulcer_model.h5')
    return diabetes_model, ulcer_model

# UI Configuration
st.set_page_config(
    page_title="DiaCare AI",
    page_icon="🥼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {background-color: #f5f5f5;}
    .stApp {max-width: 1200px; margin: 0 auto;}
    .stButton>button {
        background-color: #0077b6;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .css-1d391kg {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    h1 {color: #023e8a;}
    h2 {color: #0077b6;}
    h3 {color: #0096c7;}
</style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🥼 DiaCare AI")
page = st.sidebar.selectbox(
    "Choose a Module",
    ["Home", "Diabetes Risk Assessment", "Foot Ulcer Detection", "Patient Records"]
)

# Load models
try:
    diabetes_model, ulcer_model = load_models()
except Exception as e:
    st.error(f"Error loading models: {str(e)}")
    st.stop()

# Home Page
if page == "Home":
    st.title("Welcome to DiaCare AI")
    st.subheader("Smart Healthcare Assistant")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🔬 Features
        - Diabetes Risk Assessment
        - Foot Ulcer Detection
        - Patient Record Management
        - Automated Report Generation
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Statistics
        - AI-Powered Analysis
        - Real-time Results
        - Secure Data Storage
        - Professional Reports
        """)

# Diabetes Risk Assessment
elif page == "Diabetes Risk Assessment":
    st.title("Diabetes Risk Assessment")
    
    with st.form("diabetes_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Patient Name")
            age = st.number_input("Age", 18, 100, 25)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            pregnancies = st.number_input("Number of Pregnancies", 0, 20, 0)
            glucose = st.number_input("Glucose Level (mg/dL)", 0, 300, 120)
            
        with col2:
            blood_pressure = st.number_input("Blood Pressure (mm Hg)", 0, 200, 70)
            skin_thickness = st.number_input("Skin Thickness (mm)", 0, 100, 20)
            insulin = st.number_input("Insulin Level (mu U/ml)", 0.0, 846.0, 79.0)
            bmi = st.number_input("BMI", 0.0, 67.1, 20.0)
            diabetes_pedigree = st.number_input("Diabetes Pedigree Function", 0.0, 2.5, 0.5)
            
        submitted = st.form_submit_button("Analyze")
        
    if submitted:
        # Prepare data for model prediction
        model_input_data = {
            'Pregnancies': pregnancies,
            'Glucose': glucose,
            'BloodPressure': blood_pressure,
            'SkinThickness': skin_thickness,
            'Insulin': insulin,
            'BMI': bmi,
            'DiabetesPedigreeFunction': diabetes_pedigree,
            'Age': age
        }

        # Prepare data for database (lowercase keys)
        db_input_data = {
            'pregnancies': pregnancies,
            'glucose': glucose,
            'blood_pressure': blood_pressure,
            'skin_thickness': skin_thickness,
            'insulin': insulin,
            'bmi': bmi,
            'diabetes_pedigree': diabetes_pedigree,
        }

        # Run Prediction
        result = predict_diabetes(diabetes_model, model_input_data)

        # Save to database
        patient_id = db.add_patient(name, age, gender)
        db.add_diabetes_record(patient_id, db_input_data, result['prediction'], result['probability'])

        # Display results
        st.success("Analysis Complete!")
        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Risk Level",
                "High Risk" if result['prediction'] == 1 else "Low Risk",
                delta="Attention Needed" if result['prediction'] == 1 else "Normal"
            )

        with col2:
            st.metric(
                "Confidence",
                f"{result['probability']:.1f}%"
            )

        # Generate report - Convert model_input_data keys to lowercase for report
        report_data = {
            'pregnancies': pregnancies,
            'glucose': glucose,
            'blood_pressure': blood_pressure,
            'skin_thickness': skin_thickness,
            'insulin': insulin,
            'bmi': bmi,
            'diabetes_pedigree': diabetes_pedigree,
            'age': age,
            'prediction': result['prediction'],
            'probability': result['probability']
        }
        
        report_path = report_gen.generate_report(
            {'name': name, 'age': age, 'gender': gender},
            diabetes_result=report_data
        )

        with open(report_path, "rb") as file:
            st.download_button(
                label="Download Report",
                data=file,
                file_name=f"{name}_diabetes_report.pdf",
                mime="application/pdf"
            )

# Foot Ulcer Detection
elif page == "Foot Ulcer Detection":
    st.title("Foot Ulcer Detection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Patient Name")
        age = st.number_input("Age", 18, 100, 25)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        
    with col2:
        uploaded_file = st.file_uploader("Upload Foot Image", type=['jpg', 'png', 'jpeg'])
        
    if uploaded_file and name:
        # Use the project directory to create a temporary path
        project_root = os.getcwd() 
        temp_dir = os.path.join(project_root, 'temp')

        # Create 'temp' directory if it doesn't exist
        os.makedirs(temp_dir, exist_ok=True)
    
        # Save and process image
        image_path = os.path.join(temp_dir, uploaded_file.name)
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        # Prepare image for model - use 128x128 as expected by the model
        img = tf.keras.preprocessing.image.load_img(
            image_path, target_size=(128, 128)
        )
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)
        # Normalize pixel values to [0, 1]
        img_array = img_array / 255.0
        
        # Get prediction
        try:
            predictions = ulcer_model.predict(img_array)
            # Handle both binary classification outputs
            if predictions.shape[1] > 1:
                score = float(predictions[0][1])  # Probability of ulcer class
            else:
                score = float(predictions[0][0])  # Single output
            
            result = {
                'prediction': "Ulcer Detected" if score > 0.5 else "Normal",
                'probability': score * 100 if score > 0.5 else (1 - score) * 100,
                'image_path': image_path
            }
        except Exception as e:
            st.error(f"Error during prediction: {str(e)}")
            st.info(f"Input shape: {img_array.shape}. Please check if the model file is correct.")
            st.stop()
        
        # Save to database
        patient_id = db.add_patient(name, age, gender)
        db.add_ulcer_record(
            patient_id,
            image_path,
            result['prediction'],
            result['probability']
        )
        
        # Display results
        st.success("Analysis Complete!")
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image_path, caption="Analyzed Image", use_column_width=True)
            
        with col2:
            st.metric(
                "Detection Result",
                result['prediction'],
                delta="Attention Needed" if result['prediction'] == "Ulcer Detected" else "Normal"
            )
            st.metric(
                "Confidence",
                f"{result['probability']:.1f}%"
            )
        
        # Generate report
        report_path = report_gen.generate_report(
            {'name': name, 'age': age, 'gender': gender},
            ulcer_result=result
        )
        
        with open(report_path, "rb") as file:
            st.download_button(
                label="Download Report",
                data=file,
                file_name=f"{name}_ulcer_report.pdf",
                mime="application/pdf"
            )

# Patient Records
elif page == "Patient Records":
    st.title("Patient Records")
    
    # Simple search by name
    search_name = st.text_input("Search Patient by Name")
    
    if search_name:
        conn = sqlite3.connect('diacare_db.sqlite3')
        df = pd.read_sql_query(
            "SELECT * FROM patients WHERE name LIKE ?",
            conn,
            params=[f"%{search_name}%"]
        )
        
        if not df.empty:
            st.write("Found Patients:")
            for _, row in df.iterrows():
                with st.expander(f"{row['name']} (ID: {row['id']})"):
                    records = db.get_patient_records(row['id'])
                    
                    st.write("### Patient Information")
                    st.write(f"Age: {row['age']}")
                    st.write(f"Gender: {row['gender']}")
                    
                    if records['diabetes_records']:
                        st.write("### Diabetes Records")
                        for record in records['diabetes_records']:
                            st.write(f"Date: {record['created_at']}")
                            st.write(f"Risk: {'High' if record['prediction'] == 1 else 'Low'}")
                            st.write(f"Confidence: {record['probability']:.1f}%")
                    
                    if records['ulcer_records']:
                        st.write("### Foot Ulcer Records")
                        for record in records['ulcer_records']:
                            st.write(f"Date: {record['created_at']}")
                            st.write(f"Result: {record['prediction']}")
                            st.write(f"Confidence: {record['probability']:.1f}%")
                            if os.path.exists(record['image_path']):
                                st.image(record['image_path'], width=200)
        else:
            st.info("No patients found with that name.")

# Report Manager Page
elif page == "Report Manager":
    st.title("Generated Reports")

    reports_dir = 'reports'

    if not os.path.exists(reports_dir):
        st.warning("No reports have been generated yet.")
    else:
        report_files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]

        if not report_files:
            st.info("The reports folder is empty.")
        else:
            st.subheader("Download Previous Reports")
            for filename in sorted(report_files, reverse=True):
                file_path = os.path.join(reports_dir, filename)
                with open(file_path, "rb") as file:
                    st.download_button(
                        label=f"Download: {filename}",
                        data=file,
                        file_name=filename,
                        mime="application/pdf",
                        key=filename
                    )