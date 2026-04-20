🎯 QUICK START - Mapa Warstwicowa NMT
====================================

## ✅ GOTOWE DO UŻYTKU!

Script już działa. Możesz teraz generować mapy warstwicowe z Twoich danych pomiarów.

---

## 🚀 Jak uruchomić?

### Opcja 1: Kliknij `run.bat` (Easiest!)
Po prostu kliknij dwukrotnie plik `run.bat` w folderze.
- Użyje domyślnych danych (4×4 siatka)
- Wygeneruje plik PDF z mapą

### Opcja 2: Wiersz poleceń (Command Line)

**a) Domyślne dane:**
```bash
run.bat
```

**b) Wczytaj dane z CSV:**
```bash
run.bat --input dane_przyklad.csv
```

**c) Zmień parametry:**
```bash
run.bat --input dane.csv --dx 3.0 --dy 3.0 --odczyt-S 1500
```

**d) Pełna ścieżka do pliku:**
```bash
run.bat --input C:\Users\YourName\Downloads\pomiary.csv
```

---

## 📁 Przygotowanie danych

### Format 1: Proste wysokości (CSV)
Plik `dane_przyklad.csv` - każda linia to jeden pomiar w mm:

```
1485
1502
1495
1510
1492
1488
1505
1512
```

Zostanie automatycznie ułożone w siatkę 4×4.

### Format 2: Ze współrzędnymi (CSV)
Plik `dane_przyklad_wsp.csv` - każda linia: `x  y  wysokość`

```
0.0  0.0   1485
2.2  0.0   1502
4.4  0.0   1495
...
```

### Format 3: PDF
Wyeksportuj tabelę z Excel/LibreOffice do PDF. Script spróbuje je ekstrahować.

```bash
run.bat --input pomiary.pdf
```

---

## ⚙️ Parametry

| Parametr | Przykład | Opis |
|----------|----------|------|
| `--input` | `dane.csv` | Plik z pomiarami |
| `--dx` | `2.20` | Rozstaw X (m) |
| `--dy` | `2.20` | Rozstaw Y (m) |
| `--odczyt-S` | `1485` | Punkt odniesienia (mm) |

---

## 📊 Wynik

Po uruchomieniu skrypt wygeneruje:
- **`Mapa_Warstwicowa_Posadzka.pdf`** - Mapa z warstwicami i pikietami
- Wyświetli podsumowanie w konsoli

Mapa zawiera:
- 🎨 Kolorową reprezentację terenu (terrain colormap)
- 📈 Linie warstwic co 5 mm z etykietami
- 🔴 Czerwone punkty pomiarowych (pikiety)
- 📝 Wartości wysokości przy każdym punkcie

---

## 🆘 Troubleshooting

**Problem: "ModuleNotFoundError: No module named 'scipy'"**
→ Spróbuj zainstalować zależności:
```bash
pip install -r requirements.txt
```

**Problem: "No module named 'pdfplumber' (tylko dla PDF)"**
→ Zainstaluj bibliotekę do obsługi PDF:
```bash
pip install pdfplumber
```

**Problem: Dane się nie wczytały**
→ Sprawdź:
- Czy plik istnieje i ma poprawną ścieżkę
- Czy format to CSV, TXT lub PDF
- Czy liczby są w formacie mm (bez jednostek)

---

## 📚 Więcej informacji

Szczegółowy poradnik: **`PORADNIK_PLIKI.md`**

---

## 🎓 Przykłady

### Generuj mapę z domyślnymi danymi:
```bash
run.bat
```

### Wczytaj Twoje pomiary:
```bash
run.bat --input C:\Users\YourName\pomiary.csv
```

### Zmień skalę siatki i punkt odniesienia:
```bash
run.bat --input dane.csv --dx 3.0 --dy 2.5 --odczyt-S 1500
```

---

**Powodzenia! 🎉**
