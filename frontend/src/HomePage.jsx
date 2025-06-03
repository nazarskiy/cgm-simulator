import React, { useEffect, useState, useRef } from 'react';
import axios from 'axios';
import GlucosePlot from './GlucPlot';

const SPEED_OPTIONS = [
  { interval: 2000, text: '>' },    // 2s
  { interval: 1000, text: '>>' },   // 1s
  { interval: 500, text: '>>>' },   // 0.5s
];

function HomePage() {
    const username = localStorage.getItem("username");
    const userId = localStorage.getItem("userId");
    const realUserId = localStorage.getItem("realUserId");
    const syntheticUserId = localStorage.getItem("syntheticUserId");
    const isSynthetic = localStorage.getItem("isSynthetic") === "true";
    const [plotTimeMod, setPlotTimeMod] = useState('1h');
    const [statsTimeMod, setStatsTimeMod] = useState('1d');
    const [speedIndex, setSpeedIndex] = useState(0);
    const [currentDate, setCurrentDate] = useState(null);
    const updateIntervalRef = useRef(null);

    // Get the correct user ID based on data type
    const activeUserId = isSynthetic ? syntheticUserId : realUserId;

    const plotTimeOptions = [
      { label: '30 min', value: '30min' },
      { label: '1 hour', value: '1h' },
      { label: '3 hours', value: '3h' }
    ];
    const statsTimeOptions = [
      { label: '1 day', value: '1d' },
      { label: '7 days', value: '7d' },
      { label: '14 days', value: '14d' },
      { label: '30 days', value: '30d' },
      { label: '90 days', value: '90d' }
    ];

    // Add new useEffect for initial date fetch
    useEffect(() => {
        const fetchInitialDate = async () => {
            try {
                console.log("\n=== Debug: fetchInitialDate ===");
                console.log(`Username: ${username}`);
                console.log(`Active User ID: ${activeUserId}`);
                console.log(`Is Synthetic: ${isSynthetic}`);
                
                // First try to get the user's last viewed timestamp
                const lastViewedResponse = await axios.get(`http://localhost:8000/api/last_viewed/${username}`);
                console.log("Last viewed response:", lastViewedResponse.data);
                
                if (lastViewedResponse.data && lastViewedResponse.data.last_viewed_timestamp) {
                    console.log("Using last viewed timestamp:", lastViewedResponse.data.last_viewed_timestamp);
                    setCurrentDate(lastViewedResponse.data.last_viewed_timestamp);
                } else {
                    console.log("No last viewed timestamp, fetching initial data");
                    // If no last viewed timestamp, start from the beginning
                    const response = await axios.get(`http://localhost:8000/api/glucose/${activeUserId}?time_mod=${plotTimeMod}&real_data=${!isSynthetic}`);
                    if (response.data && response.data.length > 0) {
                        console.log("Using first timestamp from data:", response.data[0].timestamps);
                        setCurrentDate(response.data[0].timestamps);
                    }
                }
            } catch (error) {
                console.error('Error fetching initial date:', error);
                // If error getting last viewed, start from the beginning
                try {
                    console.log("Error occurred, trying to fetch initial glucose data");
                    const response = await axios.get(`http://localhost:8000/api/glucose/${activeUserId}?time_mod=${plotTimeMod}&real_data=${!isSynthetic}`);
                    if (response.data && response.data.length > 0) {
                        console.log("Using first timestamp from fallback data:", response.data[0].timestamps);
                        setCurrentDate(response.data[0].timestamps);
                    }
                } catch (innerError) {
                    console.error('Error fetching initial glucose data:', innerError);
                }
            }
        };

        if (activeUserId && username) {
            fetchInitialDate();
        }
    }, [activeUserId, username, plotTimeMod, isSynthetic]);

    // Update timestamp whenever currentDate changes
    useEffect(() => {
        const updateLastViewed = async () => {
            try {
                if (currentDate) {  // Only update if we have a date
                    console.log("\n=== Debug: updateLastViewed ===");
                    console.log(`Updating last viewed timestamp for ${username}:`, currentDate);
                    await axios.post('http://localhost:8000/update_last_viewed', {
                        username: username,
                        last_viewed_timestamp: currentDate
                    });
                }
            } catch (error) {
                console.error('Error updating last viewed timestamp:', error);
            }
        };

        if (username && currentDate) {
            updateLastViewed();
        }
    }, [currentDate, username]);

    // Update current date based on speed
    useEffect(() => {
        if (!currentDate) return;  // Don't start interval until we have initial date

        if (updateIntervalRef.current) {
            clearInterval(updateIntervalRef.current);
        }

        updateIntervalRef.current = setInterval(async () => {
            try {
                console.log("\n=== Debug: Interval Update ===");
                console.log("Current timestamp:", currentDate);
                
                // Get the next record's date
                const url = `http://localhost:8000/api/glucose/${activeUserId}?time_mod=${plotTimeMod}&real_data=${!isSynthetic}${currentDate ? `&last_date=${currentDate}` : ''}`;
                console.log("Fetching URL:", url);
                
                const response = await axios.get(url);
                if (response.data && response.data.length > 0) {
                    // Get the last record in the response
                    const nextRecord = response.data[response.data.length - 1];
                    if (nextRecord && nextRecord.timestamps !== currentDate) {
                        console.log("Found next timestamp:", nextRecord.timestamps);
                        setCurrentDate(nextRecord.timestamps);
                    } else {
                        console.log("No new timestamp found, reached end of data");
                        clearInterval(updateIntervalRef.current);
                    }
                }
            } catch (error) {
                console.error('Error fetching next date:', error);
            }
        }, SPEED_OPTIONS[speedIndex].interval);

        return () => {
            if (updateIntervalRef.current) {
                clearInterval(updateIntervalRef.current);
            }
        };
    }, [speedIndex, activeUserId, plotTimeMod, currentDate, isSynthetic]);

    const handleSpeedChange = () => {
        setSpeedIndex((prevIndex) => (prevIndex + 1) % SPEED_OPTIONS.length);
    };

    const handleLogout = async () => {
        try {
            await axios.post('http://localhost:8000/update_last_viewed', {
                username: username,
                last_viewed_timestamp: currentDate
            });
        } catch (error) {
            console.error('Error updating last viewed timestamp:', error);
        } finally {
            localStorage.removeItem("userId");
            window.location.href = "/";
        }
    };

    return (
        <div style={{ 
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            padding: '10px'
        }}>
            <div style={{
                width: '100%',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '0 20px'
            }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
                    <h2 style={{ marginBottom: 30}}>CGM Simulator</h2>
                    <StatsCircles 
                        userId={activeUserId} 
                        timeMod={statsTimeMod} 
                        updateInterval={SPEED_OPTIONS[speedIndex].interval}
                        currentDate={currentDate}
                        isSynthetic={isSynthetic}
                    />
                </div>
                <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
                    <div>
                        <label style={{ marginRight: 8 }}>Plot interval:</label>
                        <select
                            value={plotTimeMod}
                            onChange={e => setPlotTimeMod(e.target.value)}
                            style={{ fontSize: 16 }}
                        >
                            {plotTimeOptions.map(opt => (
                                <option key={opt.value} value={opt.value}>{opt.label}</option>
                            ))}
                        </select>
                    </div>
                    <button 
                        onClick={handleSpeedChange}
                        style={{
                            padding: '4px 12px',
                            fontSize: '16px',
                            backgroundColor: '#f0f0f0',
                            border: '1px solid #ccc',
                            borderRadius: '4px',
                            cursor: 'pointer'
                        }}
                    >
                        {SPEED_OPTIONS[speedIndex].text}
                    </button>
                </div>
                <button 
                    onClick={handleLogout}
                    style={{
                        padding: '8px 16px',
                        backgroundColor: '#f0f0f0',
                        border: '1px solid #ccc',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Log Out
                </button>
            </div>
            <div style={{ 
                width: '100%',
                height: '60vh',
                overflow: 'hidden',
                position: 'relative',
                marginBottom: 20
            }}>
                <GlucosePlot 
                    userId={activeUserId} 
                    timeMod={plotTimeMod} 
                    updateInterval={SPEED_OPTIONS[speedIndex].interval}
                    currentDate={currentDate}
                    isSynthetic={isSynthetic}
                />
            </div>
            <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                gap: 40,
                marginBottom: 20
            }}>
                <StatsRow2 
                    userId={activeUserId} 
                    timeMod={statsTimeMod} 
                    updateInterval={SPEED_OPTIONS[speedIndex].interval}
                    currentDate={currentDate}
                    isSynthetic={isSynthetic}
                />
                <div style={{ fontSize: 16 }}>
                    <label style={{ marginRight: 8 }}>Stats interval:</label>
                    <select
                        value={statsTimeMod}
                        onChange={e => setStatsTimeMod(e.target.value)}
                        style={{ fontSize: 16 }}
                    >
                        {statsTimeOptions.map(opt => (
                            <option key={opt.value} value={opt.value}>{opt.label}</option>
                        ))}
                    </select>
                </div>
            </div>
        </div>
    );
}

function StatsCircles({ userId, timeMod, updateInterval, currentDate, isSynthetic }) {
    const [stats, setStats] = useState([]);

    useEffect(() => {
        if (!userId) return;

        const fetchStats = () => {
            const url = `http://localhost:8000/api/stats/${userId}?time_mod=${timeMod}&real_data=${!isSynthetic}${currentDate ? `&last_date=${currentDate}` : ''}`;
            console.log("\n=== Debug: StatsCircles fetchStats ===");
            console.log("Fetching from URL:", url);
            axios.get(url)
                .then(res => {
                    console.log("Received stats:", res.data);
                    setStats(res.data.stats);
                })
                .catch(err => {
                    console.error("Error fetching stats:", err);
                    setStats(["Error loading stats"]);
                });
        };

        fetchStats();
    }, [userId, timeMod, currentDate, isSynthetic]);

    const row1 = [
        { value: stats[0]?.split(':')[1]?.trim(), label: 'Current Glucose', color: '#1976d2' },
        { value: stats[3]?.split(':')[1]?.trim(), label: 'Current Heart Rate', color: '#d32f2f' }
    ];

    return (
        <div style={{ display: 'flex', gap: 20 }}>
            {row1.map((item, i) =>
                <StatCircle key={i} value={item.value} label={item.label} color={item.color} />
            )}
        </div>
    );
}

function StatCircle({ value, label, color }) {
  const safeValue = value || '';
  const [mainValue, unit] = safeValue.split(' ');

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center'
    }}>
      <div style={{
        width: 50,
        height: 50,
        borderRadius: '50%',
        background: '#fff',
        border: `4px solid ${color}`,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: color,
        fontWeight: 'bold',
        fontSize: 14,
        boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
        lineHeight: 1.1,
        textAlign: 'center'
      }}>
        <div style={{ fontSize: 16 }}>{mainValue}</div>
        <div style={{ fontSize: 12 }}>{unit}</div>
      </div>
      <div style={{
        marginTop: 8,
        fontSize: 14,
        color: '#333',
        textAlign: 'center',
        width: 70
      }}>
        {label}
      </div>
    </div>
  );
}

function StatsRow2({ userId, timeMod, updateInterval, currentDate, isSynthetic }) {
    const [stats, setStats] = useState([]);

    useEffect(() => {
        if (!userId) return;

        const fetchStats = () => {
            const url = `http://localhost:8000/api/stats/${userId}?time_mod=${timeMod}&real_data=${!isSynthetic}${currentDate ? `&last_date=${currentDate}` : ''}`;
            console.log("\n=== Debug: StatsRow2 fetchStats ===");
            console.log("Fetching from URL:", url);
            axios.get(url)
                .then(res => {
                    console.log("Received stats:", res.data);
                    setStats(res.data.stats);
                })
                .catch(err => {
                    console.error("Error fetching stats:", err);
                    setStats(["Error loading stats"]);
                });
        };

        fetchStats();
    }, [userId, timeMod, currentDate, isSynthetic]);

    const row2 = [stats[1], stats[2], stats[4]];

    return (
        <div style={{
            display: 'flex',
            gap: 30,
            justifyContent: 'center'
        }}>
            {row2.map((s, i) => <div key={i} style={{ fontSize: 16 }}>{s}</div>)}
        </div>
    );
}

export default HomePage; 