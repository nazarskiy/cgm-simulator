import React, { useEffect, useState } from "react";
import Plot from "react-plotly.js";
import axios from "axios";

// Helper: how many hours/minutes for each timeMod
const TIME_MOD_HOURS = {
  "30min": 0.5,
  "1h": 1,
  "3h": 3
};

function GlucosePlot({ userId, timeMod = "1h", updateInterval = 2000, currentDate, isSynthetic }) {
  const [data, setData] = useState([]);

  // Fetch data when currentDate changes
  useEffect(() => {
    if (!userId) return;

    const fetchData = () => {
      const url = `http://localhost:8000/api/glucose/${userId}?time_mod=${timeMod}&real_data=${!isSynthetic}${currentDate ? `&last_date=${currentDate}` : ''}`;
      console.log("\n=== Debug: GlucPlot fetchData ===");
      console.log("Fetching from URL:", url);
      axios.get(url)
        .then(res => {
          console.log("Received data:", res.data);
          console.log("Number of records:", res.data.length);
          setData(res.data);
        })
        .catch(err => console.error("Error fetching glucose data:", err));
    };

    fetchData();
  }, [userId, timeMod, currentDate, isSynthetic]);

  const x = data.map(d => d.timestamps);
  const y = data.map(d => d.glucose);
  console.log("\n=== Debug: GlucPlot data processing ===");
  console.log("Number of x values:", x.length);
  console.log("Number of y values:", y.length);
  console.log("First few x values:", x.slice(0, 5));
  console.log("First few y values:", y.slice(0, 5));

  return (
    <Plot
      data={[
        {
          x: x,
          y: y,
          type: "scatter",
          mode: "lines+markers",
          name: "Glucose Level",
          line: { color: "#1f77b4", width: 2 }
        }
      ]}
      layout={{
        title: "Glucose Level Monitoring",
        xaxis: {
          title: "Time",
          type: "date",
          tickformat: "%H:%M",
          showgrid: false,
          nticks: Math.min(12, x.length)
        },
        yaxis: {
          title: "mg/dL",
          showgrid: false,
          range: [0, 400],
          tickmode: "linear",
          tick0: 0,
          dtick: 50
        },
        hovermode: "x unified",
        showlegend: false,
        shapes: [
          {
            type: "rect",
            xref: "paper",
            yref: "y",
            x0: 0,
            x1: 1,
            y0: 70,
            y1: 180,
            fillcolor: "rgba(0,200,0,0.15)",
            line: { width: 0 },
            layer: "below"
          },
          {
            type: "rect",
            xref: "paper",
            yref: "y",
            x0: 0,
            x1: 1,
            y0: 300,
            y1: 400,
            fillcolor: "rgba(200,0,0,0.15)",
            line: { width: 0 },
            layer: "below"
          }
        ]
      }}
      style={{ width: "100%", height: "400px" }}
      config={{ responsive: true }}
    />
  );
}

export default GlucosePlot;