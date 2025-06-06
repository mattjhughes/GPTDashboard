# CSU ChatGPT Adoption Dashboard

This repository contains a Streamlit application that visualizes ChatGPT adoption statistics across the California State University (CSU) system.

## Features

- **System-wide gauge:** Shows overall adoption percentage across all campuses.
- **Interactive map:** Highlights each campus with marker size based on total users.
- **Campus cards:** Display adoption metrics for each campus in a grid view.
- **What-If mode:** Use sliders to simulate different adoption levels; values revert to the CSV when reset.

## Getting Started

1. Install dependencies using `pip`:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the dashboard with Streamlit:
   ```bash
   streamlit run dashboard.py
   ```

The app reads `CSU_Campus_Adoption_with_Coordinates.csv` by default, so ensure it is present in the repository directory when running the app.

## Usage

- Open the link provided by Streamlit (default is `http://localhost:8501`).
- Toggle **Enable What-If Mode** to adjust active user counts using the sliders under each campus card.
- Click **Reset to CSV** to restore values from the CSV file.
- Sort campus cards by campus name, adoption %, total users, or active users using the dropdown.

## Data

The CSV file should contain the following columns:

```
Campus,Total Users,Active Users,Adoption %,Latitude,Longitude
```

An example row:

```
San Diego,44957,18603,41.4%,32.7757,-117.0716
```

## License

This project is provided for demonstration purposes without a specific license.
