# 📖 Przewodnik użytkowania - Wczytywanie danych z pliku

## Nowa funkcja
Script `grunt_to_NMT.py` może teraz wczytywać dane pomiarów z plików zamiast używać hardkodowanych wartości.

## Obsługiwane formaty

### 1. CSV/TXT z samymi wysokościami
Każdy wiersz zawiera jedną wysokość w mm. Dane zostaną ułożone w siatkę kwadratową.

**Plik: `dane_przyklad.csv`**
```
1485
1502
1495
1510
1492
...
```

### 2. CSV/TXT ze współrzędnymi i wysokościami
Format: `x y wysokość` (separatory: spacja, przecinek, tab, średnik)

**Plik: `dane_przyklad_wsp.csv`**
```
0.0  0.0   1485
2.2  0.0   1502
4.4  0.0   1495
...
```

### 3. PDF
Script ekstrahuje tabelę wartości z pliku PDF. Tabela powinna zawierać współrzędne i wysokości.

**Wymagana biblioteka**: `pdfplumber`
```bash
pip install pdfplumber
```

## Jak uruchomić

### Opcja 1: Domyślne dane (hardkodowane)
```bash
python grunt_to_NMT.py
```

### Opcja 2: Wczytaj z pliku CSV
```bash
python grunt_to_NMT.py --input dane_przyklad.csv
```

### Opcja 3: Wczytaj z pliku PDF
```bash
python grunt_to_NMT.py --input pomiary.pdf
```

### Opcja 4: Podaj parametry z linii poleceń
```bash
python grunt_to_NMT.py \
    --input dane.csv \
    --dx 2.50 \
    --dy 2.50 \
    --odczyt-S 1500
```

## Parametry linii poleceń

| Parametr | Skrót | Opis | Przykład |
|----------|-------|------|---------|
| `--input` | `-i` | Ścieżka do pliku z danymi | `-i dane.csv` |
| `--dx` | - | Odstęp X między punktami (m) | `--dx 2.20` |
| `--dy` | - | Odstęp Y między punktami (m) | `--dy 2.20` |
| `--odczyt-S` | - | Odczyt punktu odniesienia (mm) | `--odczyt-S 1485` |

## Formaty plików - szczegóły

### CSV/TXT - Komentarze
Wiersze zaczynające się od `#` lub `//` to komentarze. W komentarzach możesz podać dx i dy:

```csv
# dx = 2.20
# dy = 2.50
1485
1502
1495
```

### CSV/TXT - Separatory
Script automatycznie wykrywa separator: spacja, przecinek, tab lub średnik.

```csv
1485,1502,1495,1510
# lub
1485 1502 1495 1510
# lub
1485	1502	1495	1510
```

## Przykłady

### Uruchom z przykładowymi danymi
```bash
python grunt_to_NMT.py --input dane_przyklad.csv
```

### Zmień parametry
```bash
python grunt_to_NMT.py --input dane_przyklad.csv --dx 3.0 --dy 3.0
```

### Wczytaj własny plik
```bash
python grunt_to_NMT.py -i C:\moje_pomiary\wyniki.csv
```

## Tips

💡 **Porada**: Jeśli dane w PDF nie są dobrze ekstrahowane, najpierw wyeksportuj PDF do CSV w Excelu/LibreOffice, a następnie uruchom script.

⚠️ **Uwaga**: Aby usar PDF, zainstaluj bibliotekę:
```bash
pip install pdfplumber
```

📊 **Format siatki**: Jeśli podasz N pomiarów, zostaną ułożone w siatkę √N × √N (zaokrąglenie w górę).
