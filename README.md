# Automated Interview Slot Scheduler

A command-line Python application to automate the scheduling of interview slots between candidates and interviewers.

## Features

- Add and manage **Candidates** and **Interviewers**
- Create **Interview Slots** with conflict detection
- **Manual booking** of slots
- **Auto-scheduling** – assigns the earliest available slot to a candidate
- **Cancel bookings** (slot becomes available again)
- Persistent storage via **JSON file** (no external DB required)
- **Dashboard summary** with booking statistics
- Full **unit test** coverage

## Project Structure

```
interview-scheduler/
├── main.py           # Interactive CLI menu
├── scheduler.py      # Core scheduling logic
├── models.py         # Data models (Candidate, Interviewer, Slot, Booking)
├── database.py       # JSON-based persistence layer
├── seed_data.py      # Sample data loader for demo
├── test_scheduler.py # Unit tests
└── data.json         # Auto-generated database file
```

## Requirements

- Python 3.8+
- No external libraries needed (uses only standard library)

## Setup & Run

```bash
# 1. Clone the repository
git clone https://github.com/your-username/interview-scheduler.git
cd interview-scheduler

# 2. (Optional) Load sample data
python seed_data.py

# 3. Run the application
python main.py

# 4. Run unit tests
python -m pytest test_scheduler.py -v
# or
python test_scheduler.py
```

## Usage

```
===================================================
      AUTOMATED INTERVIEW SLOT SCHEDULER
===================================================

  --- MAIN MENU ---
  1.  Add Candidate
  2.  View All Candidates
  3.  Delete Candidate
  4.  Add Interviewer
  5.  View All Interviewers
  6.  Create Interview Slot
  7.  View All Slots
  8.  View Available Slots
  9.  Delete Slot
  10. Book a Slot (Manual)
  11. Auto-Schedule Candidate
  12. Cancel Booking
  13. View All Bookings
  14. View Booking Details
  15. Dashboard Summary
  0.  Exit
```

## How It Works

1. **Add Interviewers** with their department and expertise
2. **Create Slots** for each interviewer (date, time, duration) — overlapping slots are rejected automatically
3. **Add Candidates** with their applied role
4. **Book** a specific slot manually, or use **Auto-Schedule** to assign the earliest available slot
5. **Cancel** any booking to free up the slot for others
6. View the **Dashboard** for a quick summary

## Data Storage

All data is saved in `data.json` automatically after every operation. The file is human-readable JSON and can be deleted to reset the application.

## Running Tests

```bash
python test_scheduler.py
```

24 unit tests covering: candidate/interviewer management, slot creation, conflict detection, booking, double-booking prevention, cancellation, and auto-scheduling.

## License

MIT
