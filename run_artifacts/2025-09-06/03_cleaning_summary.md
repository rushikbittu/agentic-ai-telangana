# Cleaning Summary

- **Rows before:** 18630
- **Duplicates removed:** 0
- **Rows after:** 18630
- **Missing values (total) before:** 0
- **Missing values (total) after:** 0

## Missing values by column (before)

|                  |   missing_count |
|:-----------------|----------------:|
| district         |               0 |
| mandal           |               0 |
| date             |               0 |
| rain_(mm)        |               0 |
| min_humidity_(%) |               0 |
| max_humidity_(%) |               0 |
| date_yyyy_mm     |               0 |

## Missing values by column (after)

|                  |   missing_count |
|:-----------------|----------------:|
| district         |               0 |
| mandal           |               0 |
| date             |               0 |
| rain_(mm)        |               0 |
| min_humidity_(%) |               0 |
| max_humidity_(%) |               0 |
| date_yyyy_mm     |               0 |
| _qc_missing      |               0 |
| _qc_outlier_rain |               0 |
| _qc_imputed      |               0 |

## Notes on Quality Flags

- `_qc_missing`: True if the row had any missing values before cleaning.
- `_qc_outlier_rain`: True if rainfall was detected as an outlier (IQR rule).
- `_qc_imputed`: True if missing values were filled during cleaning.
