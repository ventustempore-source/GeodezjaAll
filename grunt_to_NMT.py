import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from math import floor
import os
import sys
import argparse
import csv

# =================================================================
# 1. DANE WEJŚCIOWE - TUTAJ WPISZ SWOJE WYNIKI
# =================================================================

# OPCJA 1: WCZYTANIE Z PLIKU
# Obsługiwane formaty:
# - CSV/TXT: każdy wiersz to "wysokość" lub "x y wysokość"
# - PDF: tabela ze współrzędnymi i wysokościami
def load_from_file(filepath):
    """
    Wczytuje dane pomiarów z pliku.
    
    Formaty obsługiwane:
    - CSV/TXT: każdy wiersz zawiera wysokość (w mm) lub "x y wysokość"
    - PDF: ekstrahuje tabelę ze współrzędnymi i wysokościami
    """
    ext = os.path.splitext(filepath)[1].lower()
    
    if ext == '.pdf':
        return load_from_pdf(filepath)
    elif ext in ['.csv', '.txt', '.tsv']:
        return load_from_csv(filepath)
    else:
        raise ValueError(f"❌ Nieznany format: {ext}. Obsługiwane: .csv, .txt, .pdf")

def arrange_points_interactive(point_dict):
    """Umożliwia interaktywne ułożenie punktów pomiarowych w siatkę"""
    print("\n" + "="*60)
    print("📐 KONFIGURACJA ROZMIESZCZENIA PUNKTÓW")
    print("="*60)
    print(f"Wczytano {len(point_dict)} punktów pomiarowych:")
    for i, (point_id, value) in enumerate(sorted(point_dict.items()), 1):
        if i <= 5:
            print(f"  {point_id}: {value}")
    if len(point_dict) > 5:
        print(f"  ... i {len(point_dict)-5} więcej")
    
    print("\nOpcje ułożenia:")
    print("  1. Automatyczne (kwadratowa siatka)")
    print("  2. Podać wymiary (liczba wierszy i kolumn)")
    print("  3. Zaawansowane (mapowanie punkt -> pozycja)")
    print("  4. Boustrophedon (Snake) pattern")
    print("  5. Specjalny układ numeracji punktów (S w centrum)")
    
    while True:
        choice = input("\nWybierz opcję [1]: ").strip() or "1"
        if choice in ['1', '2', '3', '4', '5']:
            break
        print("❌ Błędny wybór")
    
    point_list = sorted(point_dict.items(), key=lambda x: (isinstance(x[0], str), x[0]))
    point_layout = None
    
    if choice == '1':
        # Automatyczne - kwadratowa siatka
        cols = int(np.ceil(np.sqrt(len(point_list))))
        rows = int(np.ceil(len(point_list) / cols))
        print(f"✓ Automatycznie: {rows} wierszy × {cols} kolumn")
        
    elif choice == '2':
        # Podać wymiary
        while True:
            try:
                rows = int(input("Ile wierszy? "))
                cols = int(input("Ile kolumn? "))
                if rows * cols >= len(point_list):
                    break
                print(f"❌ {rows}×{cols} = {rows*cols} miejsc, a punktów: {len(point_list)}")
            except ValueError:
                print("❌ Wpisz liczby")
    
    elif choice == '3':
        # Zaawansowane mapowanie
        print("\nMapowanie punkt → pozycja (wiersz, kolumna)")
        print("Przykład: dla punktu '5' na pozycji (0,1) wpisz: 5,0,1")
        print("Wpisz 'koniec' gdy skończysz")
        
        grid_map = {}
        for pid, value in point_list:
            print(f"\nPunkt '{pid}' (wartość: {value})")
            while True:
                entry = input("  Pozycja [wiersz,kolumna] lub [Enter] aby pominąć: ").strip()
                if not entry:
                    break
                try:
                    parts = entry.split(',')
                    r, c = int(parts[0]), int(parts[1])
                    grid_map[pid] = (r, c)
                    break
                except:
                    print("  ❌ Format: wiersz,kolumna (np. 0,0)")
        
        # Oblicz wymiary na podstawie mapowania
        if grid_map:
            rows = max(r for r, c in grid_map.values()) + 1
            cols = max(c for r, c in grid_map.values()) + 1
            print(f"✓ Wymiary: {rows} wierszy × {cols} kolumn")
        else:
            rows = int(np.ceil(np.sqrt(len(point_list))))
            cols = int(np.ceil(len(point_list) / rows))
            print(f"✓ Brak mapowania - używam automatyczne: {rows}×{cols}")
            grid_map = None
    
    elif choice == '4':
        # Boustrophedon pattern
        cols = 5
        rows = 6
        print(f"✓ Boustrophedon: {rows} wierszy × {cols} kolumn")
    elif choice == '5':
        # Specjalny układ numeracji punktów ze środkiem S
        cols = 5
        rows = 6
        point_layout = [
            ['38', '39', '40', '41', '42'],
            ['33', '32', '31', '30', '29'],
            ['20', '21', '22', '23', '24'],
            ['15', '14', '13', '12', '11'],
            ['3',  '4',  'S',  '5',  '6'],
            ['73', '74', '75', '76', '77']
        ]
        print(f"✓ Wybrano specjalny układ punktów: {rows} wierszy × {cols} kolumn z S w centrum")
    
    # Utwórz siatkę
    odczyty = [[None] * cols for _ in range(rows)]
    point_ids = [[None] * cols for _ in range(rows)]
    
    if choice == '3' and grid_map:
        # Umieszczenie na podstawie mapowania
        mapped = set()
        for pid, value in point_list:
            if pid in grid_map:
                r, c = grid_map[pid]
                if 0 <= r < rows and 0 <= c < cols:
                    odczyty[r][c] = value
                    point_ids[r][c] = pid
                    mapped.add(pid)
        # Uzupełnij pozostałe punkty w pustych komórkach
        for pid, value in point_list:
            if pid in mapped:
                continue
            placed = False
            for r in range(rows):
                for c in range(cols):
                    if odczyty[r][c] is None:
                        odczyty[r][c] = value
                        point_ids[r][c] = pid
                        placed = True
                        break
                if placed:
                    break
    elif choice == '5' and point_layout is not None:
        # Wypełnij siatkę specjalnym układem numeracji punktów
        for r in range(rows):
            for c in range(cols):
                pid = point_layout[r][c]
                point_ids[r][c] = pid
                odczyty[r][c] = point_dict.get(pid)
    elif choice == '4':
        # Boustrophedon placement
        idx = 0
        for r in range(rows):
            if r % 2 == 0:  # even row, LTR
                for c in range(cols):
                    if idx < len(point_list):
                        odczyty[r][c] = point_list[idx][1]
                        point_ids[r][c] = point_list[idx][0]
                        idx += 1
            else:  # odd row, RTL
                for c in range(cols-1, -1, -1):
                    if idx < len(point_list):
                        odczyty[r][c] = point_list[idx][1]
                        point_ids[r][c] = point_list[idx][0]
                        idx += 1
    else:
        # Umieszczenie sekwencyjnie
        idx = 0
        for r in range(rows):
            for c in range(cols):
                if idx < len(point_list):
                    odczyty[r][c] = point_list[idx][1]
                    point_ids[r][c] = point_list[idx][0]
                    idx += 1
    
    return odczyty, cols, rows, point_ids

def load_from_csv(filepath):
    """Wczytuje dane z pliku CSV/TXT (separator: spacja, przecinek lub tab)"""
    print(f"📂 Wczytywanie z pliku: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
    except UnicodeDecodeError:
        with open(filepath, 'r', encoding='latin-1') as f:
            lines = [line.strip() for line in f if line.strip()]
    
    odczyty_flat = []
    point_dict = {}  # Dla formatu punkt ID + odczyt
    coords_points = []  # Dla formatu x y wysokość
    dx_file, dy_file = None, None
    has_point_ids = False
    
    for i, line in enumerate(lines):
        # Pomiń komentarze i nagłówki
        if line.startswith('#') or line.startswith('//'):
            # Szukaj informacji o dx/dy
            if 'dx' in line.lower() and '=' in line:
                try:
                    dx_file = float(line.split('=')[1].split()[0])
                except:
                    pass
            if 'dy' in line.lower() and '=' in line:
                try:
                    dy_file = float(line.split('=')[1].split()[0])
                except:
                    pass
            continue
        
        # Pomiń nagłówki w stylu "Numer;Odczyt"
        if 'numer' in line.lower() or 'odczyt' in line.lower():
            continue
        
        # Spróbuj parsować wiersz
        parts = None
        for separator in [';', ',', '\t', ' ']:
            parts = [p.strip() for p in line.split(separator) if p.strip()]
            if len(parts) > 0:
                break
        
        if not parts:
            continue
        
        try:
            # Format: "x y wysokość"
            if len(parts) >= 3:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    z = float(parts[2])
                    coords_points.append((x, y, z))
                    continue
                except ValueError:
                    pass
            # Format: "wysokość" (jeden wiersz = jeden punkt)
            if len(parts) == 1:
                try:
                    odczyty_flat.append(float(parts[0]))
                except ValueError:
                    pass
            # Format: "ID wartość" (punkt pomiarowy + odczyt)
            elif len(parts) == 2:
                try:
                    value = float(parts[1])
                    point_dict[parts[0]] = value
                    has_point_ids = True
                except ValueError:
                    pass
        except ValueError:
            print(f"  ⚠ Wiersz {i+1} nie sparsowany: {line[:50]}")
            continue
    
    if not odczyty_flat and not point_dict and not coords_points:
        raise ValueError("❌ Brak danych do sparsowania!")
    
    if coords_points:
        print(f"✓ Wczytano {len(coords_points)} pomiarów ze współrzędnymi")
        return coords_points, dx_file, dy_file, None, True
    
    # Jeśli są identyfikatory punktów, użyj interaktywnego rozmieszczenia
    if has_point_ids and point_dict:
        print(f"✓ Wczytano {len(point_dict)} pomiarów z identyfikatorami")
        odczyty, cols, rows, point_ids_grid = arrange_points_interactive(point_dict)
        return odczyty, dx_file, dy_file, point_ids_grid, False
    else:
        print(f"✓ Wczytano {len(odczyty_flat)} pomiarów")
        
        # Zmień płaski lista na siatkę
        cols = int(np.sqrt(len(odczyty_flat)))
        if cols * cols != len(odczyty_flat):
            cols = int(np.ceil(np.sqrt(len(odczyty_flat))))
        rows = int(np.ceil(len(odczyty_flat) / cols))
        
        # Pad z None jeśli trzeba
        while len(odczyty_flat) < rows * cols:
            odczyty_flat.append(None)
        
        odczyty = []
        for r in range(rows):
            row = []
            for c in range(cols):
                idx = r * cols + c
                row.append(odczyty_flat[idx] if idx < len(odczyty_flat) else None)
            odczyty.append(row)
        point_ids_grid = None
        return odczyty, dx_file, dy_file, point_ids_grid, False

def load_from_pdf(filepath):
    """Wczytuje dane z PDF - ekstrahuje tabelę"""
    try:
        import PyPDF2
    except ImportError:
        try:
            import pdfplumber
        except ImportError:
            raise ImportError(
                "❌ Do czytania PDF potrzebna biblioteka. Zainstaluj:\n"
                "  pip install pdfplumber\n"
                "lub\n"
                "  pip install PyPDF2"
            )
    
    print(f"📄 Ekstrahowanie danych z PDF: {filepath}")
    
    # Próbuj pdfplumber (lepszy do tabel)
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            page = pdf.pages[0]
            tables = page.extract_tables()
            
            if not tables:
                # Próbuj ekstrahować tekst
                text = page.extract_text()
                # Szukaj liczb
                import re
                numbers = re.findall(r'[\d.]+', text)
                odczyty_flat = [float(n) for n in numbers if float(n) > 100]  # Wysokości > 100mm
            else:
                odczyty_flat = []
                for table in tables:
                    for row in table:
                        for cell in row:
                            if cell:
                                try:
                                    odczyty_flat.append(float(str(cell).replace(',', '.')))
                                except:
                                    pass
        
        if odczyty_flat:
            print(f"✓ Ekstrahowano {len(odczyty_flat)} wartości z PDF")
            rows = int(np.ceil(np.sqrt(len(odczyty_flat))))
            cols = int(np.ceil(len(odczyty_flat) / rows))
            
            while len(odczyty_flat) < rows * cols:
                odczyty_flat.append(None)
            
            odczyty = []
            for r in range(rows):
                row = []
                for c in range(cols):
                    idx = r * cols + c
                    row.append(odczyty_flat[idx])
                odczyty.append(row)
            
            return odczyty, None, None, None, False
        else:
            raise ValueError("Nie znaleziono danych numerycznych w PDF")
    
    except ImportError:
        raise ImportError("Zainstaluj pdfplumber: pip install pdfplumber")

# Przetwarzanie argumentów linii poleceń
parser = argparse.ArgumentParser(description='Generator mapy warstwicowej NMT')
parser.add_argument('--input', '-i', type=str, help='Ścieżka do pliku z danymi (.csv, .txt, .pdf)')
parser.add_argument('--dx', type=float, help='Odstęp między punktami X (m)')
parser.add_argument('--dy', type=float, help='Odstęp między punktami Y (m)')
parser.add_argument('--odczyt-S', type=float, help='Odczyt na punkcie odniesienia S (mm)')
args = parser.parse_args()

# Funkcja do interaktywnego wyboru pliku danych
def choose_data_file():
    """Wyświetla listę dostępnych plików danych i umożliwia ich wybór"""
    supported_extensions = ('.csv', '.txt', '.pdf', '.niw')
    data_files = [f for f in os.listdir('.') if os.path.isfile(f) and f.lower().endswith(supported_extensions)]
    
    if not data_files:
        return None
    
    print("\n" + "="*60)
    print("📁 DOSTĘPNE PLIKI DANYCH:")
    print("="*60)
    for i, fname in enumerate(data_files, 1):
        file_size = os.path.getsize(fname)
        size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} B"
        print(f"  {i:2}. {fname:<40} ({size_str})")
    
    print(f"\n  0. Użyj danych domyślnych (hardkodowane)")
    print("="*60)
    
    while True:
        try:
            choice = input("Wybierz numer pliku [0]: ").strip() or "0"
            choice = int(choice)
            
            if choice == 0:
                return None
            elif 1 <= choice <= len(data_files):
                return data_files[choice - 1]
            else:
                print(f"❌ Błędny numer. Wpisz liczbę od 0 do {len(data_files)}")
        except ValueError:
            print("❌ Wpisz prawidłową liczbę")

# Domyślne wartości
dx_default = 2.20
dy_default = 2.20
odczyt_S_default = 1485

# WCZYTANIE DANYCH
# Jeśli nie podano --input, zapytaj użytkownika
if not args.input and len(sys.argv) == 1:
    print("\n🔍 Uruchomiono bez parametrów. Czy chcesz wybrać plik danych?")
    args.input = choose_data_file()

if args.input and os.path.exists(args.input):
    odczyty, dx_from_file, dy_from_file, point_ids_grid, has_xy = load_from_file(args.input)
    if dx_from_file:
        dx_default = dx_from_file
        print(f"  → dx z pliku: {dx_default} m")
    if dy_from_file:
        dy_default = dy_from_file
        print(f"  → dy z pliku: {dy_default} m")
else:
    # OPCJA 2: DANE HARDKODOWANE (DOMYŚLNIE)
    odczyty = [
        [1485, 1502, 1495, 1510], # Rząd 1
        [1492, 1488, 1505, 1512], # Rząd 2
        [1510, 1508, 1499, 1520], # Rząd 3
        [1525, 1515, 1510, 1530]  # Rząd 4
    ]
    point_ids_grid = None
    has_xy = False
    print("ℹ Używane dane domyślne (hardkodowane)")
    print("  Wskazówka: uruchom z --input <plik> aby wczytać dane z pliku")

# Odległość między punktami siatki (w metrach)
dx = args.dx if args.dx else dx_default
dy = args.dy if args.dy else dy_default

print(f"  Rozstaw siatki: dx={dx}m, dy={dy}m")

# Odczyt na punkcie odniesienia S (w mm)
odczyt_S = args.odczyt_S if args.odczyt_S else odczyt_S_default
print(f"  Punkt odniesienia S: {odczyt_S}mm")

# Dane autora (do ramki na mapie)
AUTOR = "Imię Nazwisko, Grupa X"

# =================================================================
# 2. OBLICZENIA GEODEZYJNE (WSPÓŁRZĘDNE I WYSOKOŚCI)
# =================================================================

x_list, y_list, h_list, point_ids = [], [], [], []

if has_xy:
    # Wczytano współrzędne bezpośrednio z pliku
    y_values = [y for _, y, _ in odczyty]
    # Jeśli dane Y rosną w dół szkicu (np. 0, 2.2, 4.4), zamieniamy je na wartości ujemne
    if all(y >= 0 for y in y_values) and len(set(y_values)) > 1 and min(y_values) == 0:
        odczyty = [(x, -y, z) for x, y, z in odczyty]
        print("  → Zinterpretowano współrzędne Y jako rosnące w dół szkicu i przekonwertowano je na wartości ujemne")

    for x, y, val in odczyty:
        # Wyznaczanie współrzędnych X, Y
        x_list.append(x)
        y_list.append(y)
        
        # Obliczanie wysokości H w metrach (H = Odczyt_S - Odczyt_bieżący)
        h = (odczyt_S - val) / 1000.0
        h_list.append(h)
        point_ids.append(f'P{len(point_ids)+1}')
else:
    for r_idx, row in enumerate(odczyty):
        for c_idx, val in enumerate(row):
            if val is not None:
                # Wyznaczanie współrzędnych X, Y
                x_list.append(c_idx * dx)
                y_list.append(-r_idx * dy) # Minus, aby kolejne rzędy rysowały się niżej
                
                # Obliczanie wysokości H w metrach (H = Odczyt_S - Odczyt_bieżący)
                h = (odczyt_S - val) / 1000.0
                h_list.append(h)

                if point_ids_grid is not None:
                    pid = point_ids_grid[r_idx][c_idx]
                    point_ids.append(pid if pid is not None else f'P{len(point_ids)+1}')
                else:
                    point_ids.append(f'P{len(point_ids)+1}')

# SPRAWDZENIE: Czy są jakiekolwiek pomiary?
if len(h_list) < 4:
    raise ValueError(f"❌ BŁĄD: Zarejestrowano tylko {len(h_list)} pomiarów. Potrzeba minimum 4 punktów do interpolacji!")

points = np.column_stack((x_list, y_list))
h_values = np.array(h_list)

print(f"✓ Pomiary: {len(h_list)} punktów")
print(f"  Wysokości: min={min(h_list):.4f}m, max={max(h_list):.4f}m, rozstęp={max(h_list)-min(h_list):.4f}m")

# =================================================================
# 3. TWORZENIE MODELU NMT (INTERPOLACJA)
# =================================================================

# Stworzenie gęstej siatki obliczeniowej (200x200 punktów)
grid_x, grid_y = np.mgrid[min(x_list):max(x_list):200j, 
                          min(y_list):max(y_list):200j]

# Interpolacja metodą Cubic (odpowiednik spline w C-GEO) - wygładza teren
grid_z = griddata(points, h_values, (grid_x, grid_y), method='cubic')

# SPRAWDZENIE: Czy interpolacja się powiodła?
nan_count = np.isnan(grid_z).sum()
if nan_count > grid_z.size * 0.5:
    print(f"⚠ UWAGA: {nan_count/grid_z.size*100:.1f}% wartości to NaN. Spróbuj 'linear' zamiast 'cubic'")
    grid_z = griddata(points, h_values, (grid_x, grid_y), method='linear')

# =================================================================
# 4. GENEROWANIE MAPY WARSTWICOWEJ
# =================================================================

# Obliczenie rzeczywistych wymiarów w metrach
real_width = max(x_list) - min(x_list)
real_height = max(y_list) - min(y_list)

# Dla skali 1:100, 1 cm na papierze = 1 m w rzeczywistości
# Figure size w calach (1 cal = 2.54 cm)
scale_factor = 100  # skala 1:100
cm_per_unit = 100 / scale_factor  # 1 cm = 100/100 = 1 m
inches_per_unit = cm_per_unit / 2.54

fig_width_inches = real_width * inches_per_unit
fig_height_inches = real_height * inches_per_unit

# Minimalne wymiary dla czytelności
min_width, min_height = 10, 12
fig_width_inches = max(fig_width_inches, min_width)
fig_height_inches = max(fig_height_inches, min_height)

plt.figure(figsize=(fig_width_inches, fig_height_inches))

# Rysowanie barwnego modelu NMT
plt.imshow(grid_z.T, extent=(min(x_list), max(x_list), min(y_list), max(y_list)),
           origin='lower', cmap='terrain', alpha=0.6)
plt.colorbar(label='Wysokość H [m]')

# Automatyczne wyznaczanie poziomów warstwic (co 5mm)
start_level = floor(min(h_list) * 100) / 100
stop_level = max(h_list) + 0.005
poziomy = np.arange(start_level, stop_level, 0.005)

# Rysowanie linii warstwic
warstwice = plt.contour(grid_x, grid_y, grid_z, levels=poziomy, colors='black', linewidths=0.7)
plt.clabel(warstwice, inline=True, fontsize=8, fmt='%.3f')

# Nanoszenie pikiet (punktów pomiarowych)
plt.scatter(x_list, y_list, c='red', s=15, marker='o')
for i, h_val in enumerate(h_list):
    plt.text(x_list[i]+0.1, y_list[i]+0.1, f"{h_val:.3f}", fontsize=7)

# Tytuł i ramka z opisem (zgodnie z instrukcją)
plt.title('MAPA WARSTWICOWA POSADZKI - Skala 1:100 (Model Cyfrowy)', pad=20, fontsize=14)
plt.xlabel('X [m]')
plt.ylabel('Y [m]')

# Dodanie ramki z danymi autora w prawym dolnym rogu
plt.text(max(x_list), min(y_list)-0.5, f"Autor: {AUTOR}\nData: 2024\nUkład lokalny", 
         bbox=dict(facecolor='white', alpha=0.8), ha='right', fontsize=9)

plt.axis('equal')
plt.grid(alpha=0.2)

# Zapis do pliku i wyświetlenie
output_file = 'Mapa_Warstwicowa_Posadzka.pdf'
try:
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"✓ Mapa została wygenerowana i zapisana do: {output_file}")
    print(f"  Rozmiar pliku: {os.path.getsize(output_file) / 1024:.1f} KB")
except Exception as e:
    print(f"❌ BŁĄD przy zapisie: {e}")

# =================================================================
# 5. GENEROWANIE ROZMIESZCZENIA PUNKTÓW POMIAROWYCH
# =================================================================

plt.figure(figsize=(fig_width_inches, fig_height_inches))

# Tło siatki
plt.grid(True, alpha=0.3)

# Rysowanie punktów pomiarowych
plt.scatter(x_list, y_list, c='blue', s=50, marker='o', edgecolors='black', linewidth=2)

# Numeracja punktów (lub identyfikatory źródłowe)
for i, (x, y) in enumerate(zip(x_list, y_list)):
    label = point_ids[i] if point_ids else f'P{i+1}'
    plt.text(x, y + real_height*0.02, label, ha='center', va='bottom', 
             fontsize=10, fontweight='bold', bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.8))

# Dodanie współrzędnych dla każdego punktu
for i, (x, y) in enumerate(zip(x_list, y_list)):
    plt.text(x, y - real_height*0.03, f'({x:.1f}, {y:.1f})', ha='center', va='top', 
             fontsize=8, bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

# Ustawienie zakresu osi
plt.xlim(min(x_list) - real_width*0.1, max(x_list) + real_width*0.1)
plt.ylim(min(y_list) - real_height*0.1, max(y_list) + real_height*0.1)

# Tytuł i etykiety
plt.title('ROZMIESZCZENIE PUNKTÓW POMIAROWYCH - Skala 1:100', pad=20, fontsize=14)
plt.xlabel('X [m]')
plt.ylabel('Y [m]')

# Dodanie informacji o skali
plt.text(max(x_list), min(y_list) - real_height*0.15, 
         f"Skala: 1:100\nAutor: {AUTOR}\nData: 2024", 
         bbox=dict(facecolor='white', alpha=0.9), ha='right', fontsize=9)

plt.axis('equal')

# Zapis do pliku
point_placement_file = 'Rozmieszczenie_Punktow_Pomiarowych.pdf'
try:
    plt.savefig(point_placement_file, dpi=150, bbox_inches='tight')
    print(f"✓ Rozmieszczenie punktów zostało wygenerowane i zapisane do: {point_placement_file}")
    print(f"  Rozmiar pliku: {os.path.getsize(point_placement_file) / 1024:.1f} KB")
except Exception as e:
    print(f"❌ BŁĄD przy zapisie rozmieszczenia punktów: {e}")

# =================================================================
# 6. GENEROWANIE MAPY WARSTWICOWEJ BEZ NUMERÓW PUNKTÓW
# =================================================================

plt.figure(figsize=(fig_width_inches, fig_height_inches))

# Rysowanie interpolowanych linii warstwic
warstwice_only = plt.contour(grid_x, grid_y, grid_z, levels=poziomy, colors='black', linewidths=0.8)
plt.clabel(warstwice_only, inline=True, fontsize=8, fmt='%.3f')

# Nanoszenie punktów pomiarowych z tylko wartościami wysokości
plt.scatter(x_list, y_list, c='red', s=20, marker='o')
for i, h_val in enumerate(h_list):
    plt.text(x_list[i]+0.1, y_list[i]+0.1, f"{h_val:.3f}", fontsize=7)

plt.title('MAPA WARSTWICOWA - Interpolowane warstwice i wysokości punktów', pad=20, fontsize=14)
plt.xlabel('X [m]')
plt.ylabel('Y [m]')
plt.axis('equal')
plt.grid(alpha=0.2)

contour_only_file = 'Mapa_Warstwicowa_Interpolowana.pdf'
try:
    plt.savefig(contour_only_file, dpi=150, bbox_inches='tight')
    print(f"✓ Mapa interpolowanych warstwic została zapisana do: {contour_only_file}")
    print(f"  Rozmiar pliku: {os.path.getsize(contour_only_file) / 1024:.1f} KB")
except Exception as e:
    print(f"❌ BŁĄD przy zapisie mapy interpolowanej: {e}")

# =================================================================
# 7. GENEROWANIE HYPSOMETRYCZNEGO MODELU GRID (3D)
# =================================================================

from mpl_toolkits.mplot3d import Axes3D

hypsometry_levels = np.arange(np.floor(min(h_list)), np.ceil(max(h_list)) + 1.0, 1.0)
fig = plt.figure(figsize=(fig_width_inches, fig_height_inches))
ax = fig.add_subplot(111, projection='3d')

# Normalizuj wartości dla kolorowania
norm = plt.Normalize(vmin=np.min(grid_z), vmax=np.max(grid_z))
colors = plt.cm.terrain(norm(grid_z))

# Rysowanie powierzchni 3D
surf = ax.plot_surface(grid_x, grid_y, grid_z, cmap='terrain', alpha=0.9, 
                       linewidth=0, antialiased=True)

# Nanoszenie punktów pomiarowych na powierzchni
ax.scatter(x_list, y_list, h_list, c='red', s=50, marker='o', edgecolors='black')

# Etykiety osi
ax.set_xlabel('X [m]')
ax.set_ylabel('Y [m]')
ax.set_zlabel('Wysokość H [m]')
ax.set_title('GRID Model - Hypsometryczny model posadzki (3D, interwał 1 m)', pad=20, fontsize=14)

# Pasek kolorów
fig.colorbar(surf, ax=ax, label='Wysokość H [m]', shrink=0.5)

# Ustawienie kąta patrzenia
ax.view_init(elev=25, azim=45)

grid_model_file = 'Grid_Model_Hypsometryczny_3D.pdf'
try:
    plt.savefig(grid_model_file, dpi=150, bbox_inches='tight')
    print(f"✓ Hypsometryczny model GRID (3D) został zapisany do: {grid_model_file}")
    print(f"  Rozmiar pliku: {os.path.getsize(grid_model_file) / 1024:.1f} KB")
except Exception as e:
    print(f"❌ BŁĄD przy zapisie hypsometrycznego modelu 3D: {e}")

plt.show()