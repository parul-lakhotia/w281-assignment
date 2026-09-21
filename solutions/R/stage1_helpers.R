# Stage 1 helpers: FRED download, quarterly conversion, inflation, trailing stats.

fred_csv_url <- function(series_id) {
  paste0("https://fred.stlouisfed.org/graph/fredgraph.csv?id=", series_id)
}

download_fred_series <- function(series_id, dest_file) {
  dir.create(dirname(dest_file), recursive = TRUE, showWarnings = FALSE)
  utils::download.file(fred_csv_url(series_id), dest_file, quiet = TRUE)
  dest_file
}

read_fred_csv <- function(path, series_id) {
  df <- readr::read_csv(path, show_col_types = FALSE)
  names(df) <- c("date", "value")
  df$date <- as.Date(df$date)
  df$value <- suppressWarnings(as.numeric(df$value))
  df$series_id <- series_id
  df
}

end_of_quarter_months <- function(dates) {
  as.integer(format(dates, "%m")) %in% c(3L, 6L, 9L, 12L)
}

to_quarter <- function(dates) {
  zoo::as.yearqtr(dates)
}

annualized_qoq_inflation <- function(price) {
  400 * log(price / dplyr::lag(price))
}

trailing_stat <- function(x, width, fun) {
  zoo::rollapply(x, width = width, FUN = fun, align = "right", fill = NA)
}

segment_table <- function(cpi_q, cpt_obj) {
  n <- length(cpi_q$infl)
  cps <- changepoint::cpts(cpt_obj)
  ends <- c(cps, n)
  starts <- c(1L, cps + 1L)
  means <- changepoint::param.est(cpt_obj)$mean
  data.frame(
    segment = seq_along(starts),
    start_quarter = as.character(cpi_q$qtr[starts]),
    end_quarter = as.character(cpi_q$qtr[ends]),
    mean_inflation = as.numeric(means),
    stringsAsFactors = FALSE
  )
}
