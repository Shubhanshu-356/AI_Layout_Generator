# 🏗️ AI Site Layout Generator

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg) ![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B.svg) ![License](https://img.shields.io/badge/License-MIT-green.svg)

A generative design tool that automatically optimizes building layouts on a construction site. This application uses a **Monte Carlo search algorithm** to place buildings while strictly adhering to complex geometric zoning rules, spacing constraints, and proximity requirements.

---

## 📋 Project Premise

The goal is to generate valid site plans for a **200m × 140m** rectangular site. The AI must place two types of buildings (Tower A and Tower B) while respecting a set of urban planning constraints.

### The Rules
The algorithm guarantees compliance with the following logic:
1. **Site Boundaries:** All buildings are fully inside the site.
2. **Setbacks:** No building is placed within **10m** of the site boundary.
3. **Spacing:** A minimum gap of **15m** is maintained between any two buildings.
4. **Central Plaza:** A **40m × 40m** zone in the center is strictly reserved as a no-build area.
5. **Neighbour-Mix:** Every "Tower A" must have at least one "Tower B" within a **60m** walking distance.

---

## 🛠️ Tech Stack

* **Frontend:** [Streamlit](https://streamlit.io/) (Interactive Web UI)
* **Visualization:** [Matplotlib](https://matplotlib.org/) (2D Plotting & Patch rendering)
* **Geometry Engine:** [Shapely](https://shapely.readthedocs.io/) (Polygon collision & distance calculation)
* **Logic:** Python (Randomized Greedy Search / Monte Carlo Optimization)

---

## 🚀 Installation & Setup

### 1. Prerequisites
Ensure you have Python installed. You will need the following libraries:
```bash
pip install streamlit matplotlib shapely
```

### 2. Project Structure
Ensure your project folder is organized as follows:
```
/project-folder
│
├── .gitignore             # Configuration to ignore temp files (venv, __pycache__)
├── app.py                 # The Frontend (Streamlit UI)
├── layout_generator.py    # The Backend Logic (Geometry Engine)
└── README.md              # Project Documentation
```

### 3. Running the App
Navigate to your project folder in the terminal and run:
```bash
streamlit run app.py
```

The application will open automatically in your web browser at `http://localhost:8501`.

---

## 🎮 How to Use

1. **Building Specs:**
   * Adjust the width of Tower B using the slider (defaults to 20m).

2. **Density Targets:**
   * Set the desired number of Tower A and Tower B.
   * Recommended Start: 6 Tower A, 4 Tower B.

3. **AI Settings (Optimization Depth):**
   * Low (5-20): Fast generation, good for testing.
   * High (50-100): Slower, but tries harder to fit high-density layouts and satisfy the "Neighbour-Mix" rule.

4. **Generate:**
   * Click 🚀 **GENERATE LAYOUT**.
   * View the results in the "Master Plan" tab.
   * Download the final layout image using the "Download" button.

---

## 🧠 How It Works (The Logic)

The core logic resides in `layout_generator.py`. It uses a **Randomized Greedy Strategy**:

1. **Initialization:** The site boundary and the central "Forbidden Plaza" zone are defined.

2. **Placement Loop:**
   * The AI shuffles the list of requested buildings.
   * It picks a random coordinate (x, y) and a random orientation (horizontal/vertical).
   * **Validation Check:** It instantly checks if the spot violates any of the 5 rules (boundary, spacing, plaza overlap).
   * If valid, the building is placed. If not, it retries up to 1,500 times per building.

3. **Optimization:** The app runs this entire process multiple times (controlled by "Optimization Depth") and selects the layout with the highest score (most buildings placed + compliance with the Neighbour-Mix rule).

---

## 📄 License

This project is open-source and free to use for educational purposes.
