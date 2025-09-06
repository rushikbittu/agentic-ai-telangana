# Standardization Summary

## Column Mapping (original → standardized)

| Original | Standardized |
|---|---|
| District | district |
| Mandal | mandal |
| Date | date |
| Rain (mm) | rain_(mm) |
| Min Humidity (%) | min_humidity_(%) |
| Max Humidity (%) | max_humidity_(%) |

## Dtypes after standardization

| Column | Dtype |
|---|---|
| district | object |
| mandal | object |
| date | datetime64[ns] |
| rain_(mm) | float64 |
| min_humidity_(%) | float64 |
| max_humidity_(%) | float64 |
| date_yyyy_mm | object |

- **Parsed date columns:** date
- Added corresponding `YYYY-MM` helper columns.
- **Percent-like columns coerced to float:** min_humidity_(%), max_humidity_(%)
