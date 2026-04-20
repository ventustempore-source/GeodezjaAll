import configparser
import re
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

def generate_visual_profile(filename):
    if not os.path.exists(filename):
        print(f"Błąd: Plik {filename} nie istnieje.")
        return

    config = configparser.ConfigParser()
    config.read(filename, encoding='utf-8')

    h_start = float(config['Niwelacja']['H_pocz'])
    
    elevations = {}
    current_hi = None
    expecting_bs = True
    
    sections = sorted([s for s in config.sections() if s.isdigit()], key=int)

    for sec in sections:
        data = config[sec]
        p_name = data.get('1', 'Unknown')
        
        if '4' in data and '5' in data:
            reading = (float(data['4']) + float(data['5'])) / 2.0 / 1000.0
            if expecting_bs:
                if p_name not in elevations: elevations[p_name] = h_start
                current_hi = elevations[p_name] + reading
                expecting_bs = False
            else:
                elevations[p_name] = current_hi - reading
                expecting_bs = True
        
        elif '8' in data:
            reading = float(data['8']) / 1000.0
            if current_hi:
                elevations[p_name] = current_hi - reading

    graph_data = []
    for name, elev in elevations.items():
        if "_p." in name or "_L." in name: continue
        
        match = re.match(r'0/(\d+)(?:\+(\d+))?', name)
        if match:
            dist = int(match.group(1)) * 100 + (int(match.group(2)) if match.group(2) else 0)
            graph_data.append((dist, elev, name))
        
    graph_data.sort()
    
    if not graph_data:
        print("Brak odpowiednich danych do wygenerowania profilu.")
        return

    distances = [d for d, e, n in graph_data]
    elevations_list = [e for d, e, n in graph_data]
    
    min_elev = min(elevations_list)
    datum = int(min_elev) - 5
    
    max_d = max(distances)
    mid_dist = int(round((max_d / 2) / 100.0)) * 100 
    
    pages = [(0, mid_dist), (mid_dist, max_d)]
    
    for page_num, (start_dist, end_dist) in enumerate(pages, 1):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11.69, 8.27), sharex=True, 
                                       gridspec_kw={'height_ratios': [3.5, 1]})
        plt.subplots_adjust(hspace=0.0, left=0.08, right=0.95, top=0.95, bottom=0.05) 

        ax1.plot(distances, elevations_list, marker='o', color='black', linewidth=1, markersize=3)
        ax1.set_ylabel("Rzędne [m]", fontsize=10)
        ax1.grid(True, linestyle=':', alpha=0.5)
        ax1.set_ylim(datum, max(elevations_list) + 2)
        
        ax1.text(0.02, 0.95, f"Profil podłużny trasy - Arkusz {page_num}/2\nSkala 1 : 2000/200", 
                 transform=ax1.transAxes, fontsize=11, ha='left', va='top')

        for d, e in zip(distances, elevations_list):
            if start_dist <= d <= end_dist:
                ax1.plot([d, d], [datum, e], color='gray', linestyle='--', linewidth=0.5)

        ax2.set_ylim(-1.5, 4)
        x_min = start_dist - 60
        x_max = end_dist + 10
        ax2.set_xlim(x_min, x_max)
        
        for y in range(5):
            ax2.plot([x_min, x_max], [y, y], color='black', linewidth=1)
            
        for d in distances:
            if start_dist <= d <= end_dist:
                is_hectometer = (d % 100 == 0)
                if is_hectometer:
                    ax2.plot([d, d], [0, 4], color='black', linewidth=1)
                else:
                    ax2.plot([d, d], [2, 4], color='black', linewidth=0.5)
                
        label_x = x_min + 2
        ax2.text(label_x, 3.5, "Rzędne terenu [m]", ha='left', va='center', fontsize=9)
        ax2.text(label_x, 2.5, "Odległości w terenie od hektometrów [m]", ha='left', va='center', fontsize=9)
        ax2.text(label_x, 1.5, "Hektometraż - wartość", ha='left', va='center', fontsize=9)
        ax2.text(label_x, 0.5, "Hektometraż - symbol", ha='left', va='center', fontsize=9)
        ax2.text(label_x, -1.0, "Legenda wartości", ha='left', va='center', fontsize=9)
        
        ax2.text(label_x + 10, 4.2, f"P.p. {datum:.3f}", ha='left', va='bottom', fontsize=10, fontweight='bold')
        
        bbox_style = dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none")
        
        for d, e, n in graph_data:
            if start_dist <= d <= end_dist:
                ax2.text(d, 3.5, f"{e:.3f}", ha='center', va='center', fontsize=8, bbox=bbox_style)
                
                if d % 100 != 0:
                    ax2.text(d, 2.5, f"{float(d % 100):.2f}", ha='center', va='center', fontsize=7, bbox=bbox_style)
                    
                if d % 100 == 0:
                    km = d // 1000
                    m = d % 1000
                    ax2.text(d, 1.5, f"{km}+{m}", ha='center', va='center', fontsize=8, bbox=bbox_style)
                    ax2.scatter([d], [0.5], s=80, facecolors='none', edgecolors='black', linewidth=1, zorder=3)
                    ax2.text(d, -0.8, n, ha='center', va='top', fontsize=7, bbox=bbox_style)

        ax2.axis('off')
        
        output_img = f'profil_niwelacyjny_A4_str{page_num}.png'
        plt.savefig(output_img, bbox_inches='tight', dpi=300)

        figManager = plt.get_current_fig_manager()
        try:
            figManager.window.state('zoomed')
        except Exception:
            try:
                figManager.window.showMaximized()
            except Exception:
                try:
                    figManager.frame.Maximize(True)
                except Exception:
                    pass

    plt.show()

if __name__ == "__main__":
    # Create the root window but keep it hidden
    root = tk.Tk()
    root.withdraw()
    
    # Open the file selection dialog
    file_path = filedialog.askopenfilename(
        title="Wybierz plik .niw",
        filetypes=[("Pliki niwelacji", "*.niw"), ("Wszystkie pliki", "*.*")]
    )
    
    # If a file was selected, generate the profile. Otherwise, let the user know.
    if file_path:
        generate_visual_profile(file_path)
    else:
        print("Operacja anulowana. Nie wybrano żadnego pliku.")