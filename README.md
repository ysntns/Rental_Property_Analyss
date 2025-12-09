# Rental_Property_Analyss
Data Analysis Project - Gamboo Portfolio

## Description
This project demonstrates data analysis and visualization skills using real-world datasets.

## Author
**Yasin TANIŞ**

## Quick rental summary script
Run `analysis.py` to generate a concise report about the rental listings in `RealEstateDB.csv` without needing external dependencies. You can change the output language or limit how many premium listings are shown.

```bash
# English output (default)
python analysis.py

# Türkçe çıktı
python analysis.py --lang tr --top 3
```

The script reads `RealEstateDB.csv` by default, but you can point to any compatible file with `--file /path/to/file.csv`.
