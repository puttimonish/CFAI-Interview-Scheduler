from scheduler import InterviewScheduler

scheduler = InterviewScheduler()


def print_banner():
    print("\n" + "=" * 55)
    print("      AUTOMATED INTERVIEW SLOT SCHEDULER")
    print("=" * 55)


def print_menu():
    print("""
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
""")


def input_field(prompt, required=True):
    while True:
        val = input(f"  {prompt}: ").strip()
        if val or not required:
            return val
        print("  [!] This field is required.")


# ---- Handlers ----

def add_candidate():
    print("\n  -- Add Candidate --")
    name  = input_field("Full Name")
    email = input_field("Email")
    phone = input_field("Phone")
    role  = input_field("Applied Role")
    c = scheduler.add_candidate(name, email, phone, role)
    print(f"\n  ✔ Candidate added: {c}")


def view_candidates():
    candidates = scheduler.get_all_candidates()
    print(f"\n  -- All Candidates ({len(candidates)}) --")
    if not candidates:
        print("  No candidates found.")
        return
    for c in candidates:
        print(f"  {c}")


def delete_candidate():
    view_candidates()
    cid = input_field("Enter Candidate ID to delete")
    ok = scheduler.delete_candidate(cid)
    print("  ✔ Deleted." if ok else "  ✘ Candidate not found.")


def add_interviewer():
    print("\n  -- Add Interviewer --")
    name   = input_field("Full Name")
    email  = input_field("Email")
    dept   = input_field("Department")
    expert = input_field("Expertise")
    i = scheduler.add_interviewer(name, email, dept, expert)
    print(f"\n  ✔ Interviewer added: {i}")


def view_interviewers():
    interviewers = scheduler.get_all_interviewers()
    print(f"\n  -- All Interviewers ({len(interviewers)}) --")
    if not interviewers:
        print("  No interviewers found.")
        return
    for i in interviewers:
        print(f"  {i}")


def create_slot():
    print("\n  -- Create Interview Slot --")
    view_interviewers()
    iid      = input_field("Interviewer ID")
    date_str = input_field("Date (YYYY-MM-DD)")
    time_str = input_field("Start Time (HH:MM, 24h)")
    dur_str  = input_field("Duration in minutes (default 60)", required=False)
    duration = int(dur_str) if dur_str.isdigit() else 60

    slot, msg = scheduler.create_slot(iid, date_str, time_str, duration)
    if slot:
        print(f"\n  ✔ {msg}: {slot}")
    else:
        print(f"\n  ✘ {msg}")


def view_all_slots():
    slots = scheduler.get_all_slots()
    print(f"\n  -- All Slots ({len(slots)}) --")
    if not slots:
        print("  No slots found.")
        return
    for s in slots:
        iw = scheduler.get_interviewer(s.interviewer_id)
        iw_name = iw.name if iw else "Unknown"
        print(f"  {s}  | Interviewer: {iw_name}")


def view_available_slots():
    date_str = input_field("Filter by date (YYYY-MM-DD, or press Enter to skip)", required=False)
    slots = scheduler.get_available_slots(date_str or None)
    print(f"\n  -- Available Slots ({len(slots)}) --")
    if not slots:
        print("  No available slots.")
        return
    for s in slots:
        iw = scheduler.get_interviewer(s.interviewer_id)
        iw_name = iw.name if iw else "Unknown"
        print(f"  {s}  | Interviewer: {iw_name}")


def delete_slot():
    view_all_slots()
    sid = input_field("Enter Slot ID to delete")
    ok = scheduler.delete_slot(sid)
    print("  ✔ Slot deleted." if ok else "  ✘ Slot not found.")


def book_slot():
    print("\n  -- Book a Slot --")
    view_candidates()
    cid = input_field("Candidate ID")
    view_available_slots()
    sid = input_field("Slot ID to book")
    booking, msg = scheduler.book_slot(cid, sid)
    if booking:
        print(f"\n  ✔ {msg}: {booking}")
    else:
        print(f"\n  ✘ {msg}")


def auto_schedule():
    print("\n  -- Auto-Schedule Candidate --")
    view_candidates()
    cid  = input_field("Candidate ID")
    date = input_field("Preferred date (YYYY-MM-DD, or Enter to skip)", required=False)
    booking, msg = scheduler.auto_schedule(cid, date or None)
    if booking:
        print(f"\n  ✔ {msg}: {booking}")
    else:
        print(f"\n  ✘ {msg}")


def cancel_booking():
    view_all_bookings()
    bid = input_field("Booking ID to cancel")
    ok, msg = scheduler.cancel_booking(bid)
    print(f"\n  {'✔' if ok else '✘'} {msg}")


def view_all_bookings():
    bookings = scheduler.get_all_bookings()
    print(f"\n  -- All Bookings ({len(bookings)}) --")
    if not bookings:
        print("  No bookings found.")
        return
    for b in bookings:
        print(f"  {b}")


def view_booking_details():
    bid = input_field("Booking ID")
    details = scheduler.get_booking_details(bid)
    if not details:
        print("  ✘ Booking not found.")
        return
    b  = details["booking"]
    c  = details["candidate"]
    s  = details["slot"]
    iw = details["interviewer"]
    print(f"""
  -- Booking Details --
  Booking ID   : {b.booking_id}
  Status       : {b.status.upper()}
  Booked At    : {b.booked_at.strftime('%Y-%m-%d %H:%M')}

  Candidate    : {c.name if c else 'N/A'} ({c.email if c else ''})
  Role         : {c.role if c else 'N/A'}

  Date         : {s.date if s else 'N/A'}
  Time         : {s.start_time.strftime('%H:%M') if s else ''} - {s.end_time.strftime('%H:%M') if s else ''}
  Duration     : {s.duration_minutes if s else 'N/A'} min

  Interviewer  : {iw.name if iw else 'N/A'} ({iw.department if iw else ''})
    """)


def dashboard():
    summary = scheduler.get_schedule_summary()
    print(f"""
  ========= DASHBOARD SUMMARY =========
  Total Candidates  : {summary['total_candidates']}
  Total Interviewers: {summary['total_interviewers']}
  Total Slots       : {summary['total_slots']}
  ├─ Booked         : {summary['booked_slots']}
  └─ Available      : {summary['available_slots']}
  Total Bookings    : {summary['total_bookings']}
  ======================================
    """)


ACTIONS = {
    "1": add_candidate,
    "2": view_candidates,
    "3": delete_candidate,
    "4": add_interviewer,
    "5": view_interviewers,
    "6": create_slot,
    "7": view_all_slots,
    "8": view_available_slots,
    "9": delete_slot,
    "10": book_slot,
    "11": auto_schedule,
    "12": cancel_booking,
    "13": view_all_bookings,
    "14": view_booking_details,
    "15": dashboard,
}


def main():
    print_banner()
    while True:
        print_menu()
        choice = input("  Enter choice: ").strip()
        if choice == "0":
            print("\n  Goodbye!\n")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("  [!] Invalid choice. Please try again.")
        input("\n  Press Enter to continue...")


if __name__ == "__main__":
    main()
