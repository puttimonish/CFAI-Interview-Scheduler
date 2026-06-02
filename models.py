from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional
import uuid


def generate_id():
    return str(uuid.uuid4())[:8]


@dataclass
class Candidate:
    name: str
    email: str
    phone: str
    role: str
    candidate_id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"[{self.candidate_id}] {self.name} | {self.role} | {self.email}"


@dataclass
class Interviewer:
    name: str
    email: str
    department: str
    expertise: str
    interviewer_id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self):
        return f"[{self.interviewer_id}] {self.name} | {self.department} | {self.expertise}"


@dataclass
class InterviewSlot:
    interviewer_id: str
    date: date
    start_time: time
    end_time: time
    duration_minutes: int = 60
    is_available: bool = True
    slot_id: str = field(default_factory=generate_id)
    created_at: datetime = field(default_factory=datetime.now)

    def __str__(self):
        status = "Available" if self.is_available else "Booked"
        return (
            f"[{self.slot_id}] {self.date} | "
            f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')} | "
            f"{self.duration_minutes} min | {status}"
        )


@dataclass
class Booking:
    candidate_id: str
    slot_id: str
    booked_at: datetime
    booking_id: str = field(default_factory=generate_id)
    status: str = "confirmed"

    def __str__(self):
        return (
            f"[{self.booking_id}] Candidate: {self.candidate_id} | "
            f"Slot: {self.slot_id} | Status: {self.status} | "
            f"Booked at: {self.booked_at.strftime('%Y-%m-%d %H:%M')}"
        )
