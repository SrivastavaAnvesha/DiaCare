import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

def train_diabetes_model(data_path):
    # Load and prepare data
    df = pd.read_csv(data_path)
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Create and train model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred)
    
    return model, accuracy, report

def predict_diabetes(model, input_data):
    """
    Predict diabetes risk for a single patient
    input_data: dictionary containing patient features
    """
    input_df = pd.DataFrame([input_data])
    prediction = model.predict(input_df)
    probability = model.predict_proba(input_df)
    
    return {
        'prediction': prediction[0],
        'probability': np.max(probability) * 100
    }
