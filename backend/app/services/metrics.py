"""Fund performance metrics calculator."""

from datetime import timedelta

import numpy as np
import pandas as pd

from app.schemas.fund import FundMetrics, FundNAVHistory


class MetricsCalculator:
    """Calculator for fund performance metrics."""

    # Risk-free rate for Sharpe ratio (中国10年期国债收益率约2.5%)
    RISK_FREE_RATE = 0.025
    TRADING_DAYS_PER_YEAR = 252

    def calculate_metrics(
        self,
        nav_history: FundNAVHistory,
        fund_name: str | None = None,
    ) -> FundMetrics:
        """
        Calculate comprehensive fund metrics from NAV history.

        Args:
            nav_history: Fund NAV history data
            fund_name: Optional fund name override

        Returns:
            FundMetrics with calculated values
        """
        if not nav_history.data:
            return FundMetrics(
                code=nav_history.code,
                name=fund_name or nav_history.name,
            )

        # Convert to DataFrame for easier calculation
        df = pd.DataFrame([{"date": p.date, "nav": p.nav} for p in nav_history.data])
        df = df.sort_values("date").reset_index(drop=True)
        df["date"] = pd.to_datetime(df["date"])

        # Calculate daily returns
        df["daily_return"] = df["nav"].pct_change()

        # Get current values
        latest_date = df["date"].max()

        # Calculate period returns
        return_1m = self._calculate_period_return(df, latest_date, 30)
        return_3m = self._calculate_period_return(df, latest_date, 90)
        return_6m = self._calculate_period_return(df, latest_date, 180)
        return_1y = self._calculate_period_return(df, latest_date, 365)
        return_3y = self._calculate_period_return(df, latest_date, 365 * 3)
        return_5y = self._calculate_period_return(df, latest_date, 365 * 5)

        # YTD return
        return_ytd = self._calculate_ytd_return(df, latest_date)

        # Inception return
        return_inception = self._calculate_inception_return(df)

        # Risk metrics
        max_drawdown = self._calculate_max_drawdown(df)
        volatility = self._calculate_volatility(df)
        sharpe_ratio = self._calculate_sharpe_ratio(df)

        # Annualized returns
        return_1y_annualized = return_1y  # 1 year is already annualized
        return_3y_annualized = self._annualize_return(return_3y, 3) if return_3y else None

        return FundMetrics(
            code=nav_history.code,
            name=fund_name or nav_history.name,
            return_1m=return_1m,
            return_3m=return_3m,
            return_6m=return_6m,
            return_1y=return_1y,
            return_3y=return_3y,
            return_5y=return_5y,
            return_ytd=return_ytd,
            return_inception=return_inception,
            max_drawdown=max_drawdown,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            return_1y_annualized=return_1y_annualized,
            return_3y_annualized=return_3y_annualized,
        )

    def _calculate_period_return(self, df: pd.DataFrame, end_date: pd.Timestamp, days: int) -> float | None:
        """Calculate return for a specific period."""
        start_date = end_date - timedelta(days=days)

        # Find closest available dates
        df_period = df[df["date"] >= start_date]
        if len(df_period) < 2:
            return None

        start_nav = df_period["nav"].iloc[0]
        end_nav = df_period["nav"].iloc[-1]

        if start_nav <= 0:
            return None

        return round((end_nav / start_nav - 1) * 100, 2)

    def _calculate_ytd_return(self, df: pd.DataFrame, latest_date: pd.Timestamp) -> float | None:
        """Calculate year-to-date return."""
        year_start = pd.Timestamp(latest_date.year, 1, 1)
        df_ytd = df[df["date"] >= year_start]

        if len(df_ytd) < 2:
            return None

        start_nav = df_ytd["nav"].iloc[0]
        end_nav = df_ytd["nav"].iloc[-1]

        if start_nav <= 0:
            return None

        return round((end_nav / start_nav - 1) * 100, 2)

    def _calculate_inception_return(self, df: pd.DataFrame) -> float | None:
        """Calculate return since inception."""
        if len(df) < 2:
            return None

        start_nav = df["nav"].iloc[0]
        end_nav = df["nav"].iloc[-1]

        if start_nav <= 0:
            return None

        return round((end_nav / start_nav - 1) * 100, 2)

    def _calculate_max_drawdown(self, df: pd.DataFrame) -> float | None:
        """
        Calculate maximum drawdown.

        Max drawdown = (Peak - Trough) / Peak
        """
        if len(df) < 2:
            return None

        # Calculate running maximum
        df = df.copy()
        df["peak"] = df["nav"].expanding().max()
        df["drawdown"] = (df["nav"] - df["peak"]) / df["peak"]

        max_dd = df["drawdown"].min()
        return round(max_dd * 100, 2)

    def _calculate_volatility(self, df: pd.DataFrame) -> float | None:
        """
        Calculate annualized volatility (standard deviation of returns).
        """
        if len(df) < 30:  # Need at least 30 data points
            return None

        daily_returns = df["daily_return"].dropna()
        if len(daily_returns) < 30:
            return None

        # Annualized volatility = daily std * sqrt(252)
        daily_std = daily_returns.std()
        annual_vol = daily_std * np.sqrt(self.TRADING_DAYS_PER_YEAR)

        return round(annual_vol * 100, 2)

    def _calculate_sharpe_ratio(self, df: pd.DataFrame) -> float | None:
        """
        Calculate Sharpe ratio.

        Sharpe = (Return - Risk-free rate) / Volatility
        """
        if len(df) < 252:  # Need at least 1 year of data
            return None

        daily_returns = df["daily_return"].dropna()
        if len(daily_returns) < 252:
            return None

        # Annualized return
        total_return = (df["nav"].iloc[-1] / df["nav"].iloc[0]) - 1
        years = len(daily_returns) / self.TRADING_DAYS_PER_YEAR
        annual_return = (1 + total_return) ** (1 / years) - 1

        # Annualized volatility
        annual_vol = daily_returns.std() * np.sqrt(self.TRADING_DAYS_PER_YEAR)

        if annual_vol <= 0:
            return None

        sharpe = (annual_return - self.RISK_FREE_RATE) / annual_vol
        return round(sharpe, 2)

    def _annualize_return(self, total_return: float, years: int) -> float | None:
        """Convert total return to annualized return."""
        if total_return is None or years <= 0:
            return None

        # Annualized return = (1 + total_return)^(1/years) - 1
        total_return_decimal = total_return / 100
        annual_return = (1 + total_return_decimal) ** (1 / years) - 1
        return round(annual_return * 100, 2)


# Singleton instance
_metrics_calculator: MetricsCalculator | None = None


def get_metrics_calculator() -> MetricsCalculator:
    """Get singleton metrics calculator instance."""
    global _metrics_calculator
    if _metrics_calculator is None:
        _metrics_calculator = MetricsCalculator()
    return _metrics_calculator
