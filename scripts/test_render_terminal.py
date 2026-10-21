import unittest
from datetime import date
from render_terminal import streaks


class StreakTests(unittest.TestCase):
    def check(self, values, expected):
        days = [{"date": f"2026-10-{day:02d}", "contributionCount": count} for day, count in values]
        self.assertEqual(streaks(days, date(2026, 10, 21)), expected)

    def test_empty(self):
        self.check([], (0, 0))

    def test_empty_today_preserves_yesterday_streak(self):
        self.check([(19, 1), (20, 3), (21, 0)], (2, 2))

    def test_inactive_yesterday_breaks_current_streak(self):
        self.check([(18, 2), (19, 1), (20, 0), (21, 0)], (0, 2))

    def test_today_starts_new_streak(self):
        self.check([(18, 1), (19, 2), (20, 0), (21, 4)], (1, 2))

    def test_missing_date_breaks_streak(self):
        self.check([(18, 1), (20, 2), (21, 1)], (2, 2))

    def test_future_days_are_ignored(self):
        self.check([(20, 1), (21, 1), (22, 0)], (2, 2))


if __name__ == '__main__':
    unittest.main()
