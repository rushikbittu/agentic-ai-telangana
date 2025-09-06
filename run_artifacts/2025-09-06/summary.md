# Dataset Summary & Insights

## Schema Map (original → standardized)

| Original | Standardized |
|---|---|
| District | district |
| Mandal | mandal |
| Date | date |
| Rain (mm) | rain_(mm) |
| Min Humidity (%) | min_humidity_(%) |
| Max Humidity (%) | max_humidity_(%) |

## Summary Statistics (numeric)

|------------------|
| district         |
| mandal           |
| date             |
| rain_(mm)        |
| min_humidity_(%) |
| max_humidity_(%) |
| date_yyyy_mm     |
| _qc_missing      |
| _qc_outlier_rain |
| _qc_imputed      |

## Missing Values

|                  |   missing_count |   missing_pct |
|:-----------------|----------------:|--------------:|
| district         |               0 |             0 |
| mandal           |               0 |             0 |
| date             |               0 |             0 |
| rain_(mm)        |               0 |             0 |
| min_humidity_(%) |               0 |             0 |
| max_humidity_(%) |               0 |             0 |
| date_yyyy_mm     |               0 |             0 |
| _qc_missing      |               0 |             0 |
| _qc_outlier_rain |               0 |             0 |
| _qc_imputed      |               0 |             0 |

## Outlier Counts (IQR method)

| column           |   iqr_outliers |
|:-----------------|---------------:|
| rain_(mm)        |           3165 |
| min_humidity_(%) |            193 |
| max_humidity_(%) |             22 |

## Rainfall Insights

- **Overall average `rain_(mm)`:** 3.31

**Top districts by average rainfall (top 10):**

| district             |   avg_rain |
|:---------------------|-----------:|
| Adilabad             |       7.17 |
| Kumuram Bheem        |       7.1  |
| Nizamabad            |       5.29 |
| Kamareddy            |       4.89 |
| Mulugu               |       4.83 |
| Nirmal               |       4.71 |
| Bhadradri Kothagudem |       4.32 |
| Jagtial              |       4.04 |
| Khammam              |       3.94 |
| Warangal             |       3.8  |

**Monthly rainfall plot saved:** `plot_monthly_rainfall.png`
