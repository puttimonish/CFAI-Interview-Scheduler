from datetime import datetime, timedelta
from models import Candidate, Interviewer, InterviewSlot, Booking
from database import Database


class InterviewScheduler:
    def __init__(self):
        self.db = Database()

    # ---------- Candidate ----------
    def add_candidate(self, name, email, phone, role):
        candidate = Candidate(name=name, email=email, phone=phone, role=role)
        return self.db.save_candidate(candidate)

    def get_all_candidates(self):
        return self.db.get_all_candidates()

    def get_candidate(self, candidate_id):
        return self.db.get_candidate(candidate_id)

    def delete_candidate(self, candidate_id):
        return self.db.delete_candidate(candidate_id)

    # ---------- Interviewer ----------
    def add_interviewer(self, name, email, department, expertise):
        interviewer = Interviewer(
            name=name, email=email,
            department=department, expertise=expertise
        )
        return self.db.save_interviewer(interviewer)

    def get_all_interviewers(self):
        return self.db.get_all_interviewers()

    def get_interviewer(self, interviewer_id):
        return self.db.get_interviewer(interviewer_id)

    # ---------- Slots ----------
    def create_slot(self, interviewer_id, date_str, start_time_str, duration_minutes=60):
        interviewer = self.db.get_interviewer(interviewer_id)
        if not interviewer:
            return None, "Interviewer not found"

        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            return None, "Invalid date/time format. Use YYYY-MM-DD and HH:MM"

        start_dt = datetime.combine(date, start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)

        # Conflict check
        existing = self.db.get_slots_by_interviewer(interviewer_id)
        for s in existing:
            s_start = datetime.combine(s.date, s.start_time)
            s_end = datetime.combine(s.date, s.end_time)
            if start_dt < s_end and end_dt > s_start:
                return None, f"Slot conflicts with existing slot at {s.start_time}"

        slot = InterviewSlot(
            interviewer_id=interviewer_id,
            date=date,
            start_time=start_time,
            end_time=end_dt.time(),
            duration_minutes=duration_minutes
        )
        saved = self.db.save_slot(slot)
        return saved, "Slot created successfully"

    def get_available_slots(self, date_str=None, role=None):
        slots = self.db.get_available_slots()
        if date_str:
            try:
                filter_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                slots = [s for s in slots if s.date == filter_date]
            except ValueError:
                pass
        return slots

    def get_all_slots(self):
        return self.db.get_all_slots()

    def delete_slot(self, slot_id):
        return self.db.delete_slot(slot_id)

    # ---------- Booking ----------
    def book_slot(self, candidate_id, slot_id):
        candidate = self.db.get_candidate(candidate_id)
        if not candidate:
            return None, "Candidate not found"

        slot = self.db.get_slot(slot_id)
        if not slot:
            return None, "Slot not found"

        if not slot.is_available:
            return None, "Slot is already booked"

        # Check candidate doesn't already have a booking on same date
        candidate_bookings = self.db.get_bookings_by_candidate(candidate_id)
        for b in candidate_bookings:
            booked_slot = self.db.get_slot(b.slot_id)
            if booked_slot and booked_slot.date == slot.date:
                return None, "Candidate already has an interview on this date"

        booking = Booking(
            candidate_id=candidate_id,
            slot_id=slot_id,
            booked_at=datetime.now()
        )
        saved_booking = self.db.save_booking(booking)
        self.db.mark_slot_unavailable(slot_id)
        return saved_booking, "Interview booked successfully"

    def cancel_booking(self, booking_id):
        booking = self.db.get_booking(booking_id)
        if not booking:
            return False, "Booking not found"
        self.db.delete_booking(booking_id)
        self.db.mark_slot_available(booking.slot_id)
        return True, "Booking cancelled successfully"

    def get_all_bookings(self):
        return self.db.get_all_bookings()

    def get_booking_details(self, booking_id):
        booking = self.db.get_booking(booking_id)
        if not booking:
            return None
        candidate = self.db.get_candidate(booking.candidate_id)
        slot = self.db.get_slot(booking.slot_id)
        interviewer = self.db.get_interviewer(slot.interviewer_id) if slot else None
        return {
            "booking": booking,
            "candidate": candidate,
            "slot": slot,
            "interviewer": interviewer
        }

    def auto_schedule(self, candidate_id, preferred_date=None):
        """Auto-assign the earliest available slot for a candidate."""
        candidate = self.db.get_candidate(candidate_id)
        if not candidate:
            return None, "Candidate not found"

        available = self.db.get_available_slots()
        if preferred_date:
            try:
                pd = datetime.strptime(preferred_date, "%Y-%m-%d").date()
                preferred = [s for s in available if s.date == pd]
                available = preferred if preferred else available
            except ValueError:
                pass

        # Sort by date then time
        available.sort(key=lambda s: (s.date, s.start_time))

        # Exclude dates where candidate already has a booking
        candidate_bookings = self.db.get_bookings_by_candidate(candidate_id)
        booked_dates = set()
        for b in candidate_bookings:
            bs = self.db.get_slot(b.slot_id)
            if bs:
                booked_dates.add(bs.date)

        for slot in available:
            if slot.date not in booked_dates:
                return self.book_slot(candidate_id, slot.slot_id)

        return None, "No available slots found"

    def get_schedule_summary(self):
        all_bookings = self.db.get_all_bookings()
        total_slots = len(self.db.get_all_slots())
        available_slots = len(self.db.get_available_slots())
        booked_slots = total_slots - available_slots
        return {
            "total_candidates": len(self.db.get_all_candidates()),
            "total_interviewers": len(self.db.get_all_interviewers()),
            "total_slots": total_slots,
            "booked_slots": booked_slots,
            "available_slots": available_slots,
            "total_bookings": len(all_bookings)
        }
