"""
seed_data.py – Populate the scheduler with sample data for demo/testing.
Run: python seed_data.py
"""
from datetime import date, timedelta
from scheduler import InterviewScheduler

s = InterviewScheduler()

print("Seeding sample data...\n")

# Interviewers
i1 = s.add_interviewer("Ravi Shankar",  "ravi@company.com",  "Engineering",  "Python, Backend")
i2 = s.add_interviewer("Priya Menon",   "priya@company.com", "Data Science",  "ML, Statistics")
i3 = s.add_interviewer("Anil Verma",    "anil@company.com",  "HR",            "Behavioral, Culture Fit")
print(f"Added Interviewers:\n  {i1}\n  {i2}\n  {i3}\n")

# Candidates
c1 = s.add_candidate("Alice Kumar",   "alice@gmail.com",   "9876543210", "Software Engineer")
c2 = s.add_candidate("Bob Thomas",    "bob@gmail.com",     "8765432109", "Data Scientist")
c3 = s.add_candidate("Charlie Das",   "charlie@gmail.com", "7654321098", "HR Manager")
c4 = s.add_candidate("Diana Prince",  "diana@gmail.com",   "6543210987", "Software Engineer")
print(f"Added Candidates:\n  {c1}\n  {c2}\n  {c3}\n  {c4}\n")

# Slots (next 3 days)
day1 = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
day2 = (date.today() + timedelta(days=2)).strftime("%Y-%m-%d")
day3 = (date.today() + timedelta(days=3)).strftime("%Y-%m-%d")

slots = [
    (i1.interviewer_id, day1, "09:00", 60),
    (i1.interviewer_id, day1, "11:00", 60),
    (i2.interviewer_id, day1, "10:00", 60),
    (i2.interviewer_id, day2, "09:00", 90),
    (i3.interviewer_id, day2, "14:00", 45),
    (i3.interviewer_id, day3, "10:00", 60),
    (i1.interviewer_id, day3, "15:00", 60),
]

print("Created Slots:")
for iid, d, t, dur in slots:
    slot, msg = s.create_slot(iid, d, t, dur)
    if slot:
        print(f"  {slot}")

print()

# Book some slots
all_slots = s.get_available_slots()
if len(all_slots) >= 3:
    b1, msg1 = s.book_slot(c1.candidate_id, all_slots[0].slot_id)
    b2, msg2 = s.book_slot(c2.candidate_id, all_slots[1].slot_id)
    b3, _    = s.auto_schedule(c3.candidate_id)
    print(f"Bookings:\n  {b1}\n  {b2}\n  {b3}\n")

summary = s.get_schedule_summary()
print(f"=== Summary ===")
print(f"  Candidates  : {summary['total_candidates']}")
print(f"  Interviewers: {summary['total_interviewers']}")
print(f"  Total Slots : {summary['total_slots']}")
print(f"  Booked      : {summary['booked_slots']}")
print(f"  Available   : {summary['available_slots']}")
print(f"  Bookings    : {summary['total_bookings']}")
print("\nDone! Run 'python main.py' to start the interactive scheduler.")
