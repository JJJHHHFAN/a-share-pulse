import unittest

from scripts.fetch_data import market_data_is_current


class MarketDateTest(unittest.TestCase):
    def test_rejects_previous_trading_day(self):
        self.assertFalse(market_data_is_current({"上证指数": [{"date": "2026-10-23"}]}, "2026-10-24"))

    def test_accepts_current_trading_day(self):
        self.assertTrue(market_data_is_current({"上证指数": [{"date": "2026-10-23"}]}, "2026-10-23"))

    def test_rejects_missing_index_series(self):
        self.assertFalse(market_data_is_current({}, "2026-10-23"))


if __name__ == "__main__":
    unittest.main()
