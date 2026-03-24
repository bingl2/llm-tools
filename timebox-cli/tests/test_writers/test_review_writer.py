"""review_writer 테스트."""
import pytest

from timebox.writers.review_writer import write_daily_review


class TestWriteDailyReview:
    def _sample_data(self):
        return {
            "date": "2026-03-24",
            "weekday": "화",
            "big3_results": [
                {"number": 1, "text": "API 리팩토링", "status": "done", "result_text": "완료!", "estimated_blocks": 2.0, "actual_blocks": 2.0},
                {"number": 2, "text": "프론트 버그", "status": "partial", "result_text": "70% 진행", "estimated_blocks": 1.0, "actual_blocks": 0.5},
                {"number": 3, "text": "문서 v1", "status": "todo", "result_text": "미착수", "estimated_blocks": 1.0, "actual_blocks": 0.0},
            ],
            "success_rate": "1/3",
            "estimation_accuracy": [
                {"name": "API 리팩토링", "estimated": 2.0, "actual": 2.0, "ratio": 1.0},
            ],
            "block_analysis": [
                {"time": "09:00-10:30", "block_type": "deep-work", "planned": "API 리팩토링", "actual": "API 리팩토링", "match": True},
            ],
            "block_adherence": 80.0,
            "energy_pattern": {"peak": "09:00-12:00", "low": "15:00-17:00"},
            "goal_alignment": {"direct": 2, "maintenance": 1},
            "carry_forward": {
                "big3_candidates": ["프론트 버그 수정", "문서 v1"],
                "open_loops": ["디자이너 피드백 대기"],
            },
            "one_liner": "오전 집중 좋았고, 오후에 무너짐",
            "reflection": "오늘 오전에 몰입이 잘 됐다.",
            "coach_notes": "오전 2블록 연속 몰입이 인상적입니다.",
        }

    def test_contains_date_header(self):
        md = write_daily_review(self._sample_data())
        assert "2026-03-24" in md

    def test_contains_big3_results(self):
        md = write_daily_review(self._sample_data())
        assert "## Big 3 Results" in md
        assert "API 리팩토링" in md

    def test_contains_success_rate(self):
        md = write_daily_review(self._sample_data())
        assert "1/3" in md

    def test_contains_block_analysis(self):
        md = write_daily_review(self._sample_data())
        assert "## Block Analysis" in md
        assert "Block Adherence" in md
        assert "80" in md

    def test_contains_energy_pattern(self):
        md = write_daily_review(self._sample_data())
        assert "## Energy Pattern" in md

    def test_contains_carry_forward(self):
        md = write_daily_review(self._sample_data())
        assert "## Carry Forward" in md
        assert "프론트 버그 수정" in md

    def test_contains_one_liner(self):
        md = write_daily_review(self._sample_data())
        assert "## Daily One-liner" in md
        assert "오전 집중 좋았고" in md

    def test_contains_reflection(self):
        md = write_daily_review(self._sample_data())
        assert "## Reflection" in md
        assert "오늘 오전에 몰입이 잘 됐다." in md

    def test_contains_coach_notes(self):
        md = write_daily_review(self._sample_data())
        assert "## Coach's Notes" in md
        assert "오전 2블록 연속 몰입이 인상적입니다." in md

    def test_estimation_accuracy_table(self):
        md = write_daily_review(self._sample_data())
        assert "## Estimation Accuracy" in md
        assert "1.0x" in md

    def test_status_chars(self):
        md = write_daily_review(self._sample_data())
        assert "[x]" in md
        assert "[~]" in md
        assert "[ ]" in md
