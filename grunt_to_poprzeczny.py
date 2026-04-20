import configparser
import os
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

def parse_point_name(name):
    """
    Analizuje nazwę punktu i zwraca pikietę bazową oraz odległość od osi.
    Zwraca: (baza, odległość) np. ('0/1', -5.0) dla '0/1_L.5'
    """
    try:
        if "_L." in name:
            base = name.split("_L.")[0]
            offset = -float(name.split("_L.")[1].replace(',', '.'))
        elif "_p." in name:
            base = name.split("_p.")[0]
            offset = float(name.split("_p.")[1].replace(',', '.'))
        else:
            base = name
            offset = 0.0
        return base, offset
    except ValueError:
        return name, 0.0

def generate_cross_sections_from_image_spec(filename):
    """Generuje profile poprzeczne odwzorowujące styl z podanego obrazu."""
    if not os.path.exists(filename):
        print(f"Błąd: Plik {filename} nie istnieje.")
        return

    config = configparser.ConfigParser()
    
    # POPRAWKA: Zabezpieczenie przed błędem kodowania typowym dla plików .niw (Windows-1250)
    try:
        config.read(filename, encoding='utf-8')
    except UnicodeDecodeError:
        config.read(filename, encoding='cp1250')

    # POPRAWKA: Elastyczne szukanie wysokości początkowej niezależnie od dokładnej nazwy sekcji
    h_start = None
    for sec in config.sections():
        if 'H_pocz' in config[sec]:
            h_start = float(config[sec]['H_pocz'])
            break

    if h_start is None:
        print("Błąd: Brak klucza H_pocz w pliku.")
        return

    # POPRAWKA: Używamy listy zamiast słownika, aby nie gubić punktów o tej samej nazwie
    elevations_list = []  
    elevations_dict = {}  # Pomocniczy słownik tylko dla głównych stacji (BS/FS)
    
    current_hi = None
    expecting_bs = True
    
    sections = sorted([s for s in config.sections() if s.isdigit()], key=int)

    for sec in sections:
        data = config[sec]
        p_name = data.get('1', 'Unknown')
        
        # Punkty wiążące (wstecz/wprzód)
        if '4' in data and '5' in data:
            reading = (float(data['4']) + float(data['5'])) / 2.0 / 1000.0
            if expecting_bs:
                if p_name not in elevations_dict: 
                    elevations_dict[p_name] = h_start
                current_hi = elevations_dict[p_name] + reading
                expecting_bs = False
                elevations_list.append((p_name, elevations_dict[p_name]))
            else:
                elev = current_hi - reading
                elevations_dict[p_name] = elev
                elevations_list.append((p_name, elev))
                expecting_bs = True
        
        # Punkty pośrednie (poprzeczne)
        elif '8' in data:
            reading = float(data['8']) / 1000.0
            if current_hi:
                elev = current_hi - reading
                elevations_list.append((p_name, elev))

    # Grupowanie punktów w przekroje
    cross_sections = {}
    seen_points = {}
    
    for name, elev in elevations_list:
        base, offset = parse_point_name(name)
        # Tworzymy unikalny "odcisk", by usunąć idealne duplikaty, 
        # ale zostawić faktycznie ponowione pomiary o innej rzędnej
        point_hash = (offset, round(elev, 3)) 
        
        if base not in cross_sections:
            cross_sections[base] = []
            seen_points[base] = set()
            
        if point_hash not in seen_points[base]:
            cross_sections[base].append((offset, elev, name))
            seen_points[base].add(point_hash)

    # Filtrujemy pikiety, które mają sensowne punkty poprzeczne (więcej niż sam środek)
    valid_sections = {base: pts for base, pts in cross_sections.items() if len(pts) > 1}

    if not valid_sections:
        print("Brak danych poprzecznych w pliku (brak punktów z '_L.' lub '_p.').")
        return

    print(f"Znaleziono {len(valid_sections)} przekrojów poprzecznych. Generowanie...")

    for base_name, points in valid_sections.items():
        points.sort(key=lambda x: x[0])
        
        offsets = [p[0] for p in points]
        elevs = [p[1] for p in points]
        
        min_elev = min(elevs)
        datum = int(min_elev) - 1
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True, 
                                       gridspec_kw={'height_ratios': [3.5, 1]})
        plt.subplots_adjust(hspace=0.0, left=0.1, right=0.95, top=0.90, bottom=0.1) 

        # --- GÓRNY WYKRES ---
        ax1.plot(offsets, elevs, marker='o', color='black', linewidth=1, markersize=3, label='Terenu')
        ax1.set_ylabel("Rzędne [m]", fontsize=10)
        ax1.grid(True, linestyle=':', alpha=0.5)
        
        ax1.set_ylim(datum, max(elevs) + 1.5) 
        x_min, x_max = min(offsets) - 5, max(offsets) + 5
        ax1.set_xlim(x_min, x_max)
        
        ax1.text(0.5, 0.96, "Profil poprzeczny\nSkala 1 : 200/200", 
                 transform=ax1.transAxes, fontsize=16, fontweight='bold', ha='center', va='top')

        ax1.axvline(x=0, color='gray', linestyle='-.', linewidth=1, alpha=0.6)

        for off, e in zip(offsets, elevs):
            ax1.plot([off, off], [datum, e], color='gray', linestyle='--', linewidth=0.5)

        # --- DOLNY WYKRES (TABELKA) ---
        ax2.set_ylim(0, 2)
        
        for y in range(3):
            ax2.plot([x_min, x_max], [y, y], color='black', linewidth=1)
            
        for off in offsets:
            ax2.plot([off, off], [0, 2], color='black', linewidth=0.5)
                
        label_x = x_min + 1.5 
        ax2.text(label_x, 1.5, "Rzędne terenu [m]", ha='left', va='center', fontsize=9)
        ax2.text(label_x, 0.5, "Odległości w terenie od hektometrów [m]", ha='left', va='center', fontsize=9)
        
        ax2.text(offsets[0] - 0.5, 2.2, f"P.p. {datum:.3f}", ha='right', va='bottom', fontsize=10, fontweight='bold')
        
        # POPRAWKA: Orientacja pozioma (rotation=0) i maskowanie linii białym tłem (bbox)
        bbox_style = dict(boxstyle="square,pad=0.2", facecolor="white", edgecolor="none")
        
        for off, e in zip(offsets, elevs):
            # Rzędne
            ax2.text(off, 1.5, f"{e:.3f}", ha='center', va='center', fontsize=8, rotation=0, bbox=bbox_style)
            # Odległości
            ax2.text(off, 0.5, f"{abs(off):.2f}", ha='center', va='center', fontsize=8, rotation=0, bbox=bbox_style)

        ax2.axis('off')
        
        safe_name = base_name.replace('/', '_').replace('+', '_')
        output_img = f'profil_poprzeczny_pik_{safe_name}_wzór.png'
        plt.savefig(output_img, bbox_inches='tight', dpi=300)
        print(f"Wygenerowano: {output_img}")

    plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    
    file_path = filedialog.askopenfilename(
        title="Wybierz plik .niw do wygenerowania profili wg wzoru",
        filetypes=[("Pliki niwelacji", "*.niw"), ("Wszystkie pliki", "*.*")]
    )
    
    if file_path:
        generate_cross_sections_from_image_spec(file_path)
    else:
        print("Operacja anulowana. Nie wybrano żadnego pliku.")