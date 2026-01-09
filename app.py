import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import io

# Import logic from your other file
from layout_generator import LayoutGenerator, SITE_WIDTH, SITE_HEIGHT, PLAZA_SIZE, DEFAULT_TOWER_B_WIDTH

# --- PAGE CONFIG & CSS ---
st.set_page_config(
    page_title="AI Architect | Layout Generator", 
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for a "Pro" look
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background-color: #f0f2f6;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    h1 {
        color: #2c3e50;
    }
    .stButton>button {
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #34495e;
        border-color: #34495e;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2000/2000788.png", width=60)
    st.title("Control Panel")
    st.markdown("---")
    
    st.subheader("1. Building Specs")
    tower_b_width = st.slider("Tower B Width (m)", 20, 60, 40)
    
    st.subheader("2. Density Targets")
    col_a, col_b = st.columns(2)
    with col_a:
        num_a_req = st.number_input("Tower A Qty", 1, 30, 8)
    with col_b:
        num_b_req = st.number_input("Tower B Qty", 1, 30, 5)

    st.markdown("---")
    st.subheader("3. AI Settings")
    
    # --- UPDATED SLIDER HERE ---
    # Changed from select_slider to standard slider for 1-step increments
    attempts = st.slider(
        "Optimization Depth",
        min_value=1,
        max_value=100,
        value=20,
        step=1,
        help="Higher values take longer but find better layouts."
    )
    
    st.markdown("###") # Spacer
    generate_btn = st.button("🚀 GENERATE LAYOUT", use_container_width=True)

# --- MAIN DASHBOARD ---

st.title("🏗️ Generative Site Planner")
st.markdown("Automatic layout generation respecting **setbacks**, **spacing**, and **zoning rules**.")

if generate_btn:
    # 1. GENERATION PHASE
    progress_text = "🤖 AI is exploring layout variations..."
    my_bar = st.progress(0, text=progress_text)
    
    best_layout = None
    best_score = -float('inf')
    
    for i in range(attempts):
        # Update logic
        gen = LayoutGenerator(num_a_req, num_b_req, tower_b_width)
        gen.generate()
        stats = gen.get_stats()
        
        # Scoring Logic
        score = stats['Total Area']
        if stats['Mix Rule Met']:
            score += 10000 
        else:
            score -= (stats['Mix Violations'] * 3000)
            
        if score > best_score:
            best_score = score
            best_layout = {'gen': gen, 'stats': stats}
            
        my_bar.progress((i + 1) / attempts, text=f"Checking variation {i+1}/{attempts}...")
    
    my_bar.empty()

    # 2. VISUALIZATION PHASE
    if best_layout:
        gen = best_layout['gen']
        stats = best_layout['stats']
        
        # Top Stats Row
        st.markdown("### 📊 Performance Metrics")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tower A Count", f"{stats['Count A']}/{num_a_req}", delta_color="normal")
        m2.metric("Tower B Count", f"{stats['Count B']}/{num_b_req}", delta_color="normal")
        m3.metric("Total GFA", f"{stats['Total Area']} m²")
        
        if stats['Mix Rule Met']:
            m4.metric("Neighbour Rule", "COMPLIANT", delta="Passed")
        else:
            m4.metric("Neighbour Rule", "NON-COMPLIANT", delta=f"-{stats['Mix Violations']}", delta_color="inverse")

        st.markdown("---")

        # Tabs for different views
        tab1, tab2 = st.tabs(["🗺️ Master Plan", "📋 Compliance Details"])

        with tab1:
            # Matplotlib Plotting with "Architectural" style
            fig, ax = plt.subplots(figsize=(14, 9))
            
            # Background Site
            site = patches.Rectangle((0,0), SITE_WIDTH, SITE_HEIGHT, color='#ecf0f1', zorder=0)
            ax.add_patch(site)
            
            # Boundary Dashed Line
            margin = patches.Rectangle((10,10), SITE_WIDTH-20, SITE_HEIGHT-20, 
                                     linewidth=1.5, linestyle='--', edgecolor='#7f8c8d', facecolor='none', label='Setback Line')
            ax.add_patch(margin)
            
            # Plaza
            p_start = (SITE_WIDTH/2 - PLAZA_SIZE/2)
            plaza = patches.Rectangle((p_start, 70-20), PLAZA_SIZE, PLAZA_SIZE, 
                                    color='#27ae60', alpha=0.2, hatch='..', label='Central Plaza')
            ax.add_patch(plaza)
            ax.text(SITE_WIDTH/2, SITE_HEIGHT/2, "NO BUILD\nZONE", 
                   ha='center', va='center', color='#27ae60', fontsize=8, fontweight='bold')

            # Buildings
            for b in gen.buildings:
                # Color Palette: Tower A = Navy, Tower B = Brick Red
                color = '#2c3e50' if b.type == 'A' else '#c0392b'
                rect = patches.Rectangle((b.x, b.y), b.width, b.height, 
                                       facecolor=color, edgecolor='white', linewidth=1, alpha=0.9, zorder=5)
                ax.add_patch(rect)
                
                # Center label
                ax.text(b.x + b.width/2, b.y + b.height/2, b.type, 
                       color='white', ha='center', va='center', fontsize=8, fontweight='bold', zorder=6)

            ax.set_xlim(-5, SITE_WIDTH + 5)
            ax.set_ylim(-5, SITE_HEIGHT + 5)
            ax.set_aspect('equal')
            ax.axis('off') # Clean look
            
            # Custom Legend
            from matplotlib.lines import Line2D
            legend_elements = [
                patches.Patch(facecolor='#2c3e50', label='Tower A (30x20)'),
                patches.Patch(facecolor='#c0392b', label=f'Tower B ({tower_b_width}x20)'),
                patches.Patch(facecolor='#27ae60', alpha=0.2, hatch='..', label='Plaza Area'),
                Line2D([0], [0], color='#7f8c8d', linestyle='--', label='10m Setback'),
            ]
            ax.legend(handles=legend_elements, loc='upper right', frameon=True, fancybox=True, framealpha=1)
            
            st.pyplot(fig)
            
            # Save Image Button
            img_buf = io.BytesIO()
            fig.savefig(img_buf, format='png', bbox_inches='tight', dpi=150)
            st.download_button(
                label="📥 Download Master Plan",
                data=img_buf.getvalue(),
                file_name="site_layout.png",
                mime="image/png"
            )

        with tab2:
            st.info("ℹ️ **Rule Explanations**")
            st.markdown("""
            * **Rule 1 & 3 (Boundaries):** All buildings must be 10m away from the property line.
            * **Rule 2 (Spacing):** 15m minimum gap between any two buildings.
            * **Rule 4 (Neighbour Mix):** Every 'Tower A' needs a 'Tower B' within 60m walking distance.
            * **Rule 5 (Plaza):** The center 40x40m area is reserved for public space.
            """)
            
            if not stats['Mix Rule Met']:
                st.error(f"❌ **Validation Failed:** {stats['Mix Violations']} units of Tower A are too isolated from Tower B.")
            else:
                st.success("✅ **Validation Passed:** All zoning rules are satisfied.")

    else:
        st.error("Could not find a valid layout. Try reducing the building count or increasing optimization depth.")

else:
    # Initial State / Welcome Screen
    st.info("👈 Please configure the building parameters in the sidebar and click **GENERATE LAYOUT**.")