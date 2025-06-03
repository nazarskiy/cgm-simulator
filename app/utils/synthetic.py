"""Synthetic data generation pipeline
"""

from datetime import timedelta
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from app.utils.clustering import extract_glucose_features, generate_synthetic_features
from app.utils.model import extract_hr_steps_features, train_models, predict_hr_steps


def generate_time_series(enhanced_synth_users: pd.DataFrame,
                        glucose_only_data: pd.DataFrame) -> pd.DataFrame:
    """Generate time series data for synthetic users
    Args:
        enhanced_synth_users (pd.DataFrame): Enhanced synthetic user features
        glucose_only_data (pd.DataFrame): Original glucose-only synthetic data
    Returns:
        pd.DataFrame: Complete synthetic time series data
    """
    time_columns = [col for col in glucose_only_data.columns if col.startswith("t_")]
    synthetic_time_series = []

    for idx, row in enhanced_synth_users.iterrows():
        hr_series = np.random.normal(row['hr_mean'], row['hr_std'], 288)
        steps_series = np.random.normal(row['steps_mean'], row['steps_std'], 288)

        hr_series = np.clip(np.round(hr_series), 40, 200)
        steps_series = np.clip(np.round(steps_series), 0, 500)

        synthetic_time_series.append({
            'user_id': idx,
            'glucose': glucose_only_data.iloc[idx][time_columns].values,
            'heart_rate': hr_series,
            'steps': steps_series
        })

    rows = []
    for user in synthetic_time_series:
        start_date = "2025-06-01 00:00:00"
        curr_date = pd.to_datetime(start_date).tz_localize(None)
        for i, _ in enumerate(time_columns):
            rows.append({
                "user_id": user["user_id"],
                "time": curr_date,
                "glucose": user["glucose"][i],
                "heart_rate": user["heart_rate"][i],
                "steps": user["steps"][i]
            })
            curr_date = curr_date + timedelta(minutes=5)

    return pd.DataFrame(rows)


def main():
    """Main function to generate synthetic dataset"""
    real_data = pd.read_csv("../../data/db.csv")
    real_data = real_data[["user_id", "time", "glucose", "heart_rate", "steps"]]

    synthetic_users, cluster_ids, _ = generate_synthetic_features(real_data)

    hr_steps_features = extract_hr_steps_features(real_data)
    hr_steps_scaler = StandardScaler()
    real_hr_steps_scaled = hr_steps_scaler.fit_transform(hr_steps_features)
    synthetic_hr_steps = np.zeros((100, 4))
    feature_stds = np.std(real_hr_steps_scaled, axis=0)

    for i in range(5):
        cluster_mask = cluster_ids == i
        cluster_size = cluster_mask.sum()
        hr_steps_cluster_center = synthetic_hr_steps[cluster_mask].mean(axis=0).reshape(1, -1)
        distances = np.linalg.norm(real_hr_steps_scaled - hr_steps_cluster_center, axis=1)
        closest_real_user_idx = np.argmin(distances)
        hr_steps_pattern = real_hr_steps_scaled[closest_real_user_idx]
        noise = np.random.normal(0, feature_stds * 0.1, (cluster_size, 4))
        synthetic_hr_steps[cluster_mask] = hr_steps_pattern + noise

    synthetic_hr_steps_original = hr_steps_scaler.inverse_transform(synthetic_hr_steps)
    synthetic_users['hr_mean'] = synthetic_hr_steps_original[:, 0]
    synthetic_users['hr_std'] = synthetic_hr_steps_original[:, 1]
    synthetic_users['steps_mean'] = synthetic_hr_steps_original[:, 2]
    synthetic_users['steps_std'] = synthetic_hr_steps_original[:, 3]

    X_real = extract_glucose_features(real_data)
    y_real = hr_steps_features
    X_synth = synthetic_users[X_real.columns]
    y_synth = synthetic_users[['hr_mean', 'hr_std', 'steps_mean', 'steps_std']]
    real_model, synth_model = train_models(X_real, y_real, X_synth, y_synth)

    glucose_only_data = pd.read_csv("../../synthetic/prepr_synt.csv")
    glucose_stats = extract_glucose_features(glucose_only_data, is_synthetic=True)
    enhanced_synth_users = predict_hr_steps(glucose_stats, real_model, synth_model)

    final_df = generate_time_series(enhanced_synth_users, glucose_only_data)
    final_df.to_csv("../../synthetic/prepr_synt_enhanced.csv", index=False)

if __name__ == "__main__":
    main()
