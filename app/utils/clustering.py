"""Clustering and density estimation utilities for synthetic data generation
"""

import pandas as pd
from sklearn.neighbors import KernelDensity
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans


def extract_glucose_features(df: pd.DataFrame, is_synthetic: bool = False) -> pd.DataFrame:
    """Extract statistical features from glucose data
    Args:
        df (pd.DataFrame): Input DataFrame with glucose data
        is_synthetic (bool): Whether the input data is synthetic
    Returns:
        pd.DataFrame: DataFrame with statistical features
    """
    if is_synthetic:
        time_columns = [col for col in df.columns if col.startswith('t_')]
        return pd.DataFrame({
            'mean': df[time_columns].mean(axis=1),
            'std': df[time_columns].std(axis=1),
            'min': df[time_columns].min(axis=1),
            'max': df[time_columns].max(axis=1),
            'median': df[time_columns].median(axis=1),
            'skew': df[time_columns].skew(axis=1).fillna(0)
        })
    return pd.DataFrame(df.groupby('user_id')['glucose'].agg(
            ['mean', 'std', 'min', 'max', 'median', 'skew']
    ).dropna())


def generate_synthetic_features(real_data: pd.DataFrame, n_samples: int = 100) -> tuple:
    """Generate synthetic user features using KDE and K-means
    Args:
        real_data (pd.DataFrame): Real user data
        n_samples (int): Number of synthetic samples to generate
    Returns:
        tuple: (synthetic_features, cluster_ids, scaler)
    """
    user_features = extract_glucose_features(real_data)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(user_features)

    kde = KernelDensity(kernel='gaussian', bandwidth=0.5)
    kde.fit(X_scaled)

    samples = kde.sample(n_samples)
    synthetic_glucose_features = scaler.inverse_transform(samples)
    synthetic_users = pd.DataFrame(synthetic_glucose_features, columns=user_features.columns)

    kmeans = KMeans(n_clusters=5, random_state=42)
    cluster_ids = kmeans.fit_predict(samples)

    return synthetic_users, cluster_ids, scaler
