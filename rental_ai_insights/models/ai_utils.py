# -*- coding: utf-8 -*-

from collections import defaultdict
from datetime import date


def group_by_year(records, date_getter, amount_getter):
    by_year = defaultdict(float)
    for rec in records:
        d = date_getter(rec)
        if not d:
            continue
        by_year[d.year] += float(amount_getter(rec) or 0.0)
    return dict(sorted(by_year.items()))


def group_by_month(records, date_getter, amount_getter):
    by_month = defaultdict(float)
    for rec in records:
        d = date_getter(rec)
        if not d:
            continue
        key = (d.year, d.month)
        by_month[key] += float(amount_getter(rec) or 0.0)
    return dict(sorted(by_month.items()))


def simple_linear_forecast(month_series, horizon=3):
    """
    month_series: list of (year, month, value) sorted by time
    horizon: number of months to forecast
    Returns list of (year, month, forecast_value)
    """
    if not month_series:
        return []
    # index t = 1..n, values y
    y = [v for (_, _, v) in month_series]
    n = len(y)
    if n == 1:
        # flat forecast
        base_val = y[0]
        return _extend_months(month_series[-1][0], month_series[-1][1], base_val, horizon)
    # compute slope and intercept via simple OLS
    # slope = cov(t,y)/var(t)
    t_vals = list(range(1, n + 1))
    t_mean = sum(t_vals) / n
    y_mean = sum(y) / n
    cov = sum((t - t_mean) * (yy - y_mean) for t, yy in zip(t_vals, y))
    var_t = sum((t - t_mean) ** 2 for t in t_vals) or 1.0
    slope = cov / var_t
    intercept = y_mean - slope * t_mean
    forecasts = []
    last_y, last_m = month_series[-1][0], month_series[-1][1]
    for h in range(1, horizon + 1):
        t_future = n + h
        y_hat = intercept + slope * t_future
        y_hat = max(0.0, y_hat)
        last_y, last_m = _next_month(last_y, last_m)
        forecasts.append((last_y, last_m, y_hat))
    return forecasts


def _next_month(y, m):
    if m == 12:
        return (y + 1, 1)
    return (y, m + 1)


def _extend_months(y, m, val, horizon):
    out = []
    for _ in range(horizon):
        y, m = _next_month(y, m)
        out.append((y, m, val))
    return out