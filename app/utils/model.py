"""Prediction models for synthetic data generation
"""

import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def extract_hr_steps_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract statistical features from heart rate and steps data
    Args:
        df (pd.DataFrame): Input DataFrame with heart rate and steps data
    Returns:
        pd.DataFrame: DataFrame with statistical features
    """
    return pd.DataFrame(df.groupby('user_id').agg({
        'heart_rate': ['mean', 'std'],
        'steps': ['mean', 'std']
    }).dropna())

def train_models(X_real: pd.DataFrame, y_real: pd.DataFrame,
                X_synth: pd.DataFrame, y_synth: pd.DataFrame) -> tuple:
    """Train real and synthetic models for predicting HR and steps
    Args:
        X_real (pd.DataFrame): Real user features
        y_real (pd.DataFrame): Real user HR and steps features
        X_synth (pd.DataFrame): Synthetic user features
        y_synth (pd.DataFrame): Synthetic user HR and steps features
    Returns:
        tuple: (real_model, synth_model)
    """
    real_model = RandomForestRegressor(n_estimators=100, random_state=42)
    real_model.fit(X_real, y_real)

    synth_model = RandomForestRegressor(n_estimators=100, random_state=42)
    synth_model.fit(X_synth, y_synth)

    return real_model, synth_model


def predict_hr_steps(glucose_stats: pd.DataFrame, real_model: RandomForestRegressor,
                    synth_model: RandomForestRegressor) -> pd.DataFrame:
    """Predict HR and steps features using ensemble of real and synthetic models
    Args:
        glucose_stats (pd.DataFrame): Glucose statistical features
        real_model (RandomForestRegressor): Model trained on real data
        synth_model (RandomForestRegressor): Model trained on synthetic data
    Returns:
        pd.DataFrame: DataFrame with predicted HR and steps features
    """
    pred_real = real_model.predict(glucose_stats)
    pred_synth = synth_model.predict(glucose_stats)

    # Ensemble predictions with weights
    ensemble_pred = 0.8 * pred_real + 0.2 * pred_synth

    enhanced_synth_users = glucose_stats.copy()
    enhanced_synth_users[["hr_mean", "hr_std", "steps_mean", "steps_std"]] = ensemble_pred

    return enhanced_synth_users
