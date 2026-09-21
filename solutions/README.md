# Stage 1: Forecasting U.S. Inflation

RStudio project for Stage 1: download FRED data, construct quarterly CPI inflation, explore 1960Q1-1999Q4, and run a PELT/BIC mean change-point analysis.

## Open in RStudio

1. Double-click `stage1-inflation.Rproj`, or use File, Open Project.
2. Open `stage1_report.qmd`.
3. Render to PDF.

Packages: `ggplot2`, `dplyr`, `readr`, `tidyr`, `tibble`, `patchwork`, `scales`, `zoo`, `changepoint`, `knitr`. The first render needs internet so FRED CSVs can be saved in `data/`.
