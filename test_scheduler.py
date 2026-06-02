import unittest
import os
from datetime import date, timedelta
from scheduler import InterviewScheduler

# Use a separate test DB
import database
database.DB_FILE = "test_data.json"


class TestInterviewScheduler(unittest.TestCase):

    def setUp(self):
        # Fresh scheduler for each test
        if os.path.exists("test_data.json"):
            os.remove("test_data.json")
        self.s = InterviewScheduler()

        # Common test data
        self.candidate = self.s.add_candidate(
            "Alice Kumar", "alice@example.com", "9876543210", "Software Engineer"
        )
        self.interviewer = self.s.add_interviewer(
            "Bob Smith", "bob@example.com", "Engineering", "Python, System Design"
        )
        self.tomorrow = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    def tearDown(self):
        if os.path.exists("test_data.json"):
            os.remove("test_data.json")

    # -- Candidate Tests --
    def test_add_candidate(self):
        self.assertEqual(self.candidate.name, "Alice Kumar")
        self.assertEqual(self.candidate.role, "Software Engineer")

    def test_get_all_candidates(self):
        self.s.add_candidate("Bob", "bob2@x.com", "1234567890", "Designer")
        candidates = self.s.get_all_candidates()
        self.assertEqual(len(candidates), 2)

    def test_delete_candidate(self):
        result = self.s.delete_candidate(self.candidate.candidate_id)
        self.assertTrue(result)
        self.assertIsNone(self.s.get_candidate(self.candidate.candidate_id))

    def test_delete_nonexistent_candidate(self):
        result = self.s.delete_candidate("INVALID_ID")
        self.assertFalse(result)

    # -- Interviewer Tests --
    def test_add_interviewer(self):
        self.assertEqual(self.interviewer.name, "Bob Smith")
        self.assertEqual(self.interviewer.department, "Engineering")

    def test_get_all_interviewers(self):
        self.s.add_interviewer("Carol", "carol@x.com", "HR", "Behavioral")
        self.assertEqual(len(self.s.get_all_interviewers()), 2)

    # -- Slot Tests --
    def test_create_slot(self):
        slot, msg = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:00", 60
        )
        self.assertIsNotNone(slot)
        self.assertTrue(slot.is_available)

    def test_slot_conflict(self):
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "10:00", 60)
        slot2, msg = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:30", 60
        )
        self.assertIsNone(slot2)
        self.assertIn("conflict", msg.lower())

    def test_no_conflict_different_times(self):
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "09:00", 60)
        slot2, msg = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:00", 60
        )
        self.assertIsNotNone(slot2)

    def test_invalid_date_format(self):
        slot, msg = self.s.create_slot(
            self.interviewer.interviewer_id, "26-05-2025", "10:00"
        )
        self.assertIsNone(slot)

    def test_delete_slot(self):
        slot, _ = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "11:00", 60
        )
        result = self.s.delete_slot(slot.slot_id)
        self.assertTrue(result)

    def test_get_available_slots(self):
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "10:00", 60)
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "11:00", 60)
        available = self.s.get_available_slots()
        self.assertEqual(len(available), 2)

    # -- Booking Tests --
    def test_book_slot(self):
        slot, _ = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:00", 60
        )
        booking, msg = self.s.book_slot(
            self.candidate.candidate_id, slot.slot_id
        )
        self.assertIsNotNone(booking)
        self.assertEqual(booking.status, "confirmed")

    def test_double_booking_same_slot(self):
        slot, _ = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:00", 60
        )
        self.s.book_slot(self.candidate.candidate_id, slot.slot_id)
        c2 = self.s.add_candidate("Dave", "dave@x.com", "1111111111", "PM")
        booking2, msg = self.s.book_slot(c2.candidate_id, slot.slot_id)
        self.assertIsNone(booking2)
        self.assertIn("already booked", msg.lower())

    def test_candidate_double_booking_same_date(self):
        slot1, _ = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:00", 60
        )
        slot2, _ = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "14:00", 60
        )
        self.s.book_slot(self.candidate.candidate_id, slot1.slot_id)
        booking2, msg = self.s.book_slot(self.candidate.candidate_id, slot2.slot_id)
        self.assertIsNone(booking2)
        self.assertIn("already has an interview", msg.lower())

    def test_cancel_booking(self):
        slot, _ = self.s.create_slot(
            self.interviewer.interviewer_id, self.tomorrow, "10:00", 60
        )
        booking, _ = self.s.book_slot(self.candidate.candidate_id, slot.slot_id)
        ok, msg = self.s.cancel_booking(booking.booking_id)
        self.assertTrue(ok)

        # Slot should be available again
        refreshed = self.s.get_available_slots()
        self.assertTrue(any(s.slot_id == slot.slot_id for s in refreshed))

    def test_cancel_invalid_booking(self):
        ok, msg = self.s.cancel_booking("INVALID")
        self.assertFalse(ok)

    # -- Auto-Schedule Tests --
    def test_auto_schedule(self):
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "10:00", 60)
        booking, msg = self.s.auto_schedule(self.candidate.candidate_id)
        self.assertIsNotNone(booking)

    def test_auto_schedule_no_slots(self):
        booking, msg = self.s.auto_schedule(self.candidate.candidate_id)
        self.assertIsNone(booking)
        self.assertIn("No available slots", msg)

    def test_auto_schedule_with_preferred_date(self):
        day_after = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "10:00", 60)
        self.s.create_slot(self.interviewer.interviewer_id, day_after, "10:00", 60)
        booking, msg = self.s.auto_schedule(self.candidate.candidate_id, day_after)
        self.assertIsNotNone(booking)

    # -- Summary Test --
    def test_schedule_summary(self):
        self.s.create_slot(self.interviewer.interviewer_id, self.tomorrow, "10:00", 60)
        summary = self.s.get_schedule_summary()
        self.assertEqual(summary["total_candidates"], 1)
        self.assertEqual(summary["total_interviewers"], 1)
        self.assertEqual(summary["total_slots"], 1)
        self.assertEqual(summary["available_slots"], 1)
        self.assertEqual(summary["booked_slots"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
