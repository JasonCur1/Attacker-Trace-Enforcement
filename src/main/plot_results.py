import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

CSV_FILE = "gridsearch_results.csv"
OUTPUT_DIR = "plots"

# Set to True if the curve goes vertical too fast
USE_LOG_SCALE = False 

sns.set_theme(style="whitegrid", context="paper", font_scale=1.2)
plt.rcParams['font.family'] = 'sans-serif'

def load_and_clean_data(csv_path):
    df = pd.read_csv(csv_path)
    cols = ['Translator (s)', 'Preprocessor (s)', 'Search (s)', 'Total Time (s)']
    
    # --- CHANGE 1: Handle TIMEOUTs ---
    # Replace "TIMEOUT" with 1800 (30 mins) so it doesn't get turned into NaN
    for col in cols:
        df[col] = df[col].replace('TIMEOUT', 1800)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    df = df.dropna(subset=cols)
    return df

def plot_balanced_scaling(df):
    # Filter for rows where Ext == Int == Crit
    balanced = df[
        (df['Ext PCs'] == df['Int PCs']) & 
        (df['Int PCs'] == df['Crit PCs'])
    ].copy()
    
    if balanced.empty:
        print("No balanced configurations (N,N,N) found in data.")
        return

    balanced.sort_values(by='Ext PCs', inplace=True)
    
    plt.figure(figsize=(10, 6))
    
    # Plot Total Time
    plt.plot(balanced['Ext PCs'], balanced['Total Time (s)'], 
             marker='o', markersize=8, linewidth=3, color='#333333')

    plt.title('Scaling Analysis: Balanced Network (N, N, N)', weight='bold')
    plt.xlabel('N (PCs per Segment)')
    plt.ylabel('Time (seconds)')
    
    if USE_LOG_SCALE:
        plt.yscale('log')
        plt.ylabel('Time (seconds) - Log Scale')

    plt.legend()
    plt.xticks(balanced['Ext PCs']) # Force integer ticks for N
    plt.tight_layout()
    
    plt.savefig(f"{OUTPUT_DIR}/1_balanced_scaling.png", dpi=300)
    print(f"Generated {OUTPUT_DIR}/1_balanced_scaling.png")

def plot_segment_sensitivity(df):
    plt.figure(figsize=(10, 6))
    
    # Filter: Base case is (1,1,1)
    # We find scaling where 2 are fixed at 1
    
    # Ext Scale: Int=1, Crit=1
    ext = df[(df['Int PCs'] == 1) & (df['Crit PCs'] == 1)].sort_values('Ext PCs')
    if not ext.empty:
        plt.plot(ext['Ext PCs'], ext['Total Time (s)'], marker='o', label='Scaling External')

    # Int Scale: Ext=1, Crit=1
    int_ = df[(df['Ext PCs'] == 1) & (df['Crit PCs'] == 1)].sort_values('Int PCs')
    if not int_.empty:
        plt.plot(int_['Int PCs'], int_['Total Time (s)'], marker='s', label='Scaling Internal')

    # Crit Scale: Ext=1, Int=1
    crit = df[(df['Ext PCs'] == 1) & (df['Int PCs'] == 1)].sort_values('Crit PCs')
    if not crit.empty:
        plt.plot(crit['Crit PCs'], crit['Total Time (s)'], marker='^', label='Scaling Critical')

    plt.title('Sensitivity: Impact of Adding 1 PC to Specific Segments', weight='bold')
    plt.xlabel('PCs in Segment')
    plt.ylabel('Total Time (s)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/2_segment_sensitivity.png", dpi=300)
    print(f"Generated {OUTPUT_DIR}/2_segment_sensitivity.png")

def plot_heatmap(df):
    subset = df[df['Crit PCs'] == 1]
    if len(subset) < 4: return
    
    pivot = subset.pivot_table(index='Int PCs', columns='Ext PCs', values='Total Time (s)')
    plt.figure(figsize=(8, 6))
    sns.heatmap(pivot, annot=True, fmt=".2f", cmap="YlOrRd")
    plt.title('Performance Heatmap (Fixed Crit=1)', weight='bold')
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/3_heatmap.png", dpi=300)
    print(f"Generated {OUTPUT_DIR}/3_heatmap.png")

def plot_small_multiples(df):
    """
    Creates a row of heatmaps, where each heatmap represents a fixed number of Critical PCs.
    X-Axis: External PCs
    Y-Axis: Internal PCs
    Color: Total Time (s)
    """
    # 1. Identify the unique values for the slicing variable
    crit_vals = sorted(df['Crit PCs'].unique())
    n_plots = len(crit_vals)
    
    if n_plots == 0:
        print("No data found for small multiples.")
        return

    # 2. Setup the figure with 1 row and N columns
    # We share the Y-axis and Color Scale (vmin/vmax) to make them comparable
    fig, axes = plt.subplots(1, n_plots, figsize=(5 * n_plots, 5), sharey=True)
    
    # Handle the edge case where there is only 1 unique value for Critical PCs
    if n_plots == 1:
        axes = [axes]

    # Find global min/max for consistent coloring across all maps
    vmin = df['Total Time (s)'].min()
    vmax = df['Total Time (s)'].max()

    # 3. Iterate through each value of Critical PCs and draw a heatmap
    for ax, crit_val in zip(axes, crit_vals):
        subset = df[df['Crit PCs'] == crit_val]
        
        # Create the matrix for the heatmap (Y=Int, X=Ext)
        pivot_table = subset.pivot_table(index='Int PCs', columns='Ext PCs', values='Total Time (s)')
        
        # --- CHANGE 2: Create Custom Labels ---
        # If value >= 1800 (TIMEOUT), label it ">1800", otherwise use standard float formatting
        # This allows the color to still reflect "High/Max" while the text is descriptive
        annot_labels = pivot_table.map(lambda x: ">1800" if x >= 1800 else f"{x:.2f}")

        # Draw Heatmap
        # annot=annot_labels: Uses our custom string matrix
        # annot_kws={"size": 6}: Sets font size smaller (adjust 6 as needed)
        sns.heatmap(pivot_table, ax=ax, vmin=vmin, vmax=vmax, 
                    annot=annot_labels, fmt="", # fmt="" required when annot is strings
                    cmap="YlOrRd", cbar=False,
                    annot_kws={"size": 6}) # SMALLER FONT
        
        ax.set_title(f'Critical PCs = {crit_val}', weight='bold')
        ax.set_xlabel('External PCs')
        if ax == axes[0]:
            ax.set_ylabel('Internal PCs')
        else:
            ax.set_ylabel('') # Hide Y label for inner plots
        
        ax.invert_yaxis() # Put (1,1) at the bottom-left

    # 4. Add a single common colorbar on the right
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7]) 
    norm = plt.Normalize(vmin, vmax)
    sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=norm)
    sm.set_array([])
    fig.colorbar(sm, cax=cbar_ax, label='Total Time (s)')

    plt.suptitle('Performance Heatmaps by Segment Configuration', fontsize=16, weight='bold')
    plt.subplots_adjust(right=0.9, wspace=0.1) # Adjust spacing
    
    save_path = f"{OUTPUT_DIR}/4_small_multiples.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Generated {save_path}")

# --- MAIN ---
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

df = load_and_clean_data(CSV_FILE)
if not df.empty:
    plot_balanced_scaling(df)
    plot_segment_sensitivity(df)
    plot_heatmap(df)
    plot_small_multiples(df)
else:
    print("No valid data found.")