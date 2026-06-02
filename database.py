import json
import os
from datetime import date, time, datetime
from models import Candidate, Interviewer, InterviewSlot, Booking

DB_FILE = "data.json"


def _serialize(obj):
    """Convert dataclass objects to JSON-serializable dicts."""
    d = obj.__dict__.copy()
    for k, v in d.items():
        if isinstance(v, (date, time, datetime)):
            d[k] = v.isoformat()
    return d


def _to_date(s):
    return date.fromisoformat(s) if s else None

def _to_time(s):
    return time.fromisoformat(s) if s else None

def _to_datetime(s):
    return datetime.fromisoformat(s) if s else None


class Database:
    def __init__(self):
        self._candidates = {}
        self._interviewers = {}
        self._slots = {}
        self._bookings = {}
        self._load()

    # ---------- Persistence ----------
    def _load(self):
        if not os.path.exists(DB_FILE):
            return
        with open(DB_FILE, "r") as f:
            data = json.load(f)

        for d in data.get("candidates", []):
            c = Candidate(**{k: v for k, v in d.items() if k != "created_at"})
            c.created_at = _to_datetime(d.get("created_at"))
            self._candidates[c.candidate_id] = c

        for d in data.get("interviewers", []):
            i = Interviewer(**{k: v for k, v in d.items() if k != "created_at"})
            i.created_at = _to_datetime(d.get("created_at"))
            self._interviewers[i.interviewer_id] = i

        for d in data.get("slots", []):
            s = InterviewSlot(
                interviewer_id=d["interviewer_id"],
                date=_to_date(d["date"]),
                start_time=_to_time(d["start_time"]),
                end_time=_to_time(d["end_time"]),
                duration_minutes=d["duration_minutes"],
                is_available=d["is_available"],
                slot_id=d["slot_id"],
            )
            s.created_at = _to_datetime(d.get("created_at"))
            self._slots[s.slot_id] = s

        for d in data.get("bookings", []):
            b = Booking(
                candidate_id=d["candidate_id"],
                slot_id=d["slot_id"],
                booked_at=_to_datetime(d["booked_at"]),
                booking_id=d["booking_id"],
                status=d["status"]
            )
            self._bookings[b.booking_id] = b

    def _save(self):
        data = {
            "candidates": [_serialize(c) for c in self._candidates.values()],
            "interviewers": [_serialize(i) for i in self._interviewers.values()],
            "slots": [_serialize(s) for s in self._slots.values()],
            "bookings": [_serialize(b) for b in self._bookings.values()],
        }
        with open(DB_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # ---------- Candidates ----------
    def save_candidate(self, candidate):
        self._candidates[candidate.candidate_id] = candidate
        self._save()
        return candidate

    def get_candidate(self, candidate_id):
        return self._candidates.get(candidate_id)

    def get_all_candidates(self):
        return list(self._candidates.values())

    def delete_candidate(self, candidate_id):
        if candidate_id in self._candidates:
            del self._candidates[candidate_id]
            self._save()
            return True
        return False

    # ---------- Interviewers ----------
    def save_interviewer(self, interviewer):
        self._interviewers[interviewer.interviewer_id] = interviewer
        self._save()
        return interviewer

    def get_interviewer(self, interviewer_id):
        return self._interviewers.get(interviewer_id)

    def get_all_interviewers(self):
        return list(self._interviewers.values())

    # ---------- Slots ----------
    def save_slot(self, slot):
        self._slots[slot.slot_id] = slot
        self._save()
        return slot

    def get_slot(self, slot_id):
        return self._slots.get(slot_id)

    def get_all_slots(self):
        return list(self._slots.values())

    def get_available_slots(self):
        return [s for s in self._slots.values() if s.is_available]

    def get_slots_by_interviewer(self, interviewer_id):
        return [s for s in self._slots.values() if s.interviewer_id == interviewer_id]

    def mark_slot_unavailable(self, slot_id):
        if slot_id in self._slots:
            self._slots[slot_id].is_available = False
            self._save()

    def mark_slot_available(self, slot_id):
        if slot_id in self._slots:
            self._slots[slot_id].is_available = True
            self._save()

    def delete_slot(self, slot_id):
        if slot_id in self._slots:
            del self._slots[slot_id]
            self._save()
            return True
        return False

    # ---------- Bookings ----------
    def save_booking(self, booking):
        self._bookings[booking.booking_id] = booking
        self._save()
        return booking

    def get_booking(self, booking_id):
        return self._bookings.get(booking_id)

    def get_all_bookings(self):
        return list(self._bookings.values())

    def get_bookings_by_candidate(self, candidate_id):
        return [b for b in self._bookings.values() if b.candidate_id == candidate_id]

    def delete_booking(self, booking_id):
        if booking_id in self._bookings:
            del self._bookings[booking_id]
            self._save()
            return True
        return False
