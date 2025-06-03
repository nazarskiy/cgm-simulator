from app.utils.stats import update_stats
from datetime import timedelta
import numpy as np
import pandas as pd
import pytest

glucose_mean = 100
glucose_std = 10
start_date = "2025-06-01 00:00:00"

@pytest.fixture
def sample_data():
    """Sample data for testing"""
    np.random.seed(42)
    curr_date = pd.to_datetime(start_date)
    dates = [curr_date + timedelta(minutes=5*i) for i in range(2016)]  # 2016 * 5min = 1 week
    glucose = np.random.normal(glucose_mean, glucose_std, len(dates))
    heart_rate = np.zeros_like(glucose)
    steps = np.random.randint(0, 100, len(dates))
    return pd.DataFrame({
        "timestamps": dates,
        "glucose": glucose,
        "heart_rate": heart_rate,
        "steps": steps
    })

def check_glucose_stats(sample_data: pd.DataFrame, last_date: str):
    """Helper function to check glucose stats"""
    stats = update_stats(sample_data, "1d", last_date)

    # Parse stats from returned strings
    avg_glucose = float(stats[1].split(":")[1].split()[0])
    std_glucose = float(stats[2].split(":")[1].split()[0])

    assert abs(avg_glucose - glucose_mean) < 10 #std is 10
    assert abs(std_glucose - glucose_std) < 1

def check_steps_stats(sample_data: pd.DataFrame, last_date: str):
    """Helper function to check steps stats"""
    stats = update_stats(sample_data, "1d", last_date)

    total_steps = int(stats[4].split(":")[1].strip())
    last_date = pd.to_datetime(last_date).tz_localize(None) + timedelta(minutes=5)
    start = last_date - timedelta(days=1)
    mask = (sample_data["timestamps"] > start) & (sample_data["timestamps"] <= last_date)
    expected_steps = sample_data.loc[mask, "steps"].sum()

    assert total_steps == expected_steps

@pytest.mark.parametrize("day_offset", range(7))
def test_stats_with_different_dates(sample_data: pd.DataFrame, day_offset: int):
    """Test stats for different dates in the sample data"""
    last_date = pd.to_datetime(start_date) + timedelta(days=day_offset + 1) - timedelta(minutes=10)
    check_glucose_stats(sample_data, str(last_date))
    check_steps_stats(sample_data, str(last_date))

