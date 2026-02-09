"""
Student Academic Helper — Sprint 1 Main Program (Terminal UI)

Quality attributes:
  - Usability: clear confirmations after actions (immediate)
  - Performance: deadlines list renders quickly (small dataset)
  - Accuracy: grade calculation correct
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


DATA_FILE = "academic_helper_data.json"


# Data model helpers

def _today() -> date:
    return date.today()


def _parse_date_yyyy_mm_dd(s: str) -> date:
    return datetime.strptime(s.strip(), "%Y-%m-%d").date()


def _format_date_long(d: date) -> str:
    return d.strftime("%B %d, %Y")


def _next_id(items: List[Dict[str, Any]]) -> int:
    return (max((int(x["id"]) for x in items), default=0) + 1)


def _clear_screen() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _pause(msg: str = "Press Enter to continue...") -> None:
    try:
        input(msg)
    except EOFError:
        pass


def _safe_input(prompt: str) -> str:
    try:
        return input(prompt)
    except EOFError:
        return ""


def _load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        return {
            "courses": [],
            "assignments": []
        }

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("courses", [])
        data.setdefault("assignments", [])
        return data
    except (json.JSONDecodeError, OSError):
        return {
            "courses": [],
            "assignments": []
        }


def _save_data(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _get_course_by_id(data: Dict[str, Any], course_id: int) -> Optional[Dict[str, Any]]:
    for c in data["courses"]:
        if int(c["id"]) == int(course_id):
            return c
    return None


def _find_course_by_name(data: Dict[str, Any], name: str) -> Optional[Dict[str, Any]]:
    name_norm = name.strip().lower()
    for c in data["courses"]:
        if str(c["name"]).strip().lower() == name_norm:
            return c
    return None


# Seed data

def ensure_seed_data(data: Dict[str, Any]) -> None:
    if data["courses"]:
        return

    data["courses"].append({"id": 1, "name": "CS 361 – Software Engineering I"})
    data["courses"].append({"id": 2, "name": "MTH 265 – Intro to Series"})
    data["courses"].append({"id": 3, "name": "CS 340 – Intro to Databases"})


# UI: Home/Main Menu

def show_home() -> None:
    _clear_screen()
    print("=" * 46)
    print("Student Academic Helper")
    print("=" * 46)
    print()
    # IH#1
    print("What this app does (Benefits):")
    print("- Helps you add assignments and track deadlines")
    print("- Lets you view upcoming work in due-date order")
    print("- Calculates your current grade from recorded scores")
    print()
    # IH#6
    print("How it works (Step-by-step):")
    print("1) Add assignments (and optionally scores)")
    print("2) View upcoming deadlines (and details if you want)")
    print("3) Calculate your current course grade")
    print()
    print("Main Menu:")
    print("1) Add Assignment")
    print("2) View Upcoming Deadlines")
    print("3) Current Grade")
    print("4) Exit")
    print()


# Add Assignment

def add_assignment_flow(data: Dict[str, Any]) -> None:
    while True:
        _clear_screen()
        print("=" * 46)
        print("Add Assignment")
        print("=" * 46)
        print()
        # IH#2
        print("Before you start (Costs/Requirements):")
        print("- Required fields: Course, Title, Due Date")
        print("- Keeping deadlines accurate takes a little time, but it helps you avoid surprises.")
        print()

        course = choose_or_create_course(data)
        if course is None:
            # IH#5
            return

        title = _safe_input("Assignment Title (required): ").strip()
        if not title:
            _pause("Title is required. Press Enter to try again...")
            continue

        due_date = choose_due_date()
        if due_date is None:
            return

        status = choose_status(default="Not Started")
        if status is None:
            return

        score = choose_optional_score()

        # IH#8
        _clear_screen()
        print("=" * 46)
        print("Confirm Save")
        print("=" * 46)
        print("You are about to save this assignment:")
        print(f"- Course: {course['name']}")
        print(f"- Title: {title}")
        print(f"- Due: {_format_date_long(due_date)} ({due_date.isoformat()})")
        print(f"- Status: {status}")
        if score is None:
            print("- Score: (none)")
        else:
            print(f"- Score: {score:.2f}%")
        print()
        print("1) Save")
        print("2) Cancel (do not save)")
        choice = _safe_input("Choose: ").strip()

        if choice != "1":
            _pause("Canceled. Nothing was saved. Press Enter to return...")
            return

        assignment_id = _next_id(data["assignments"])
        data["assignments"].append({
            "id": assignment_id,
            "course_id": int(course["id"]),
            "title": title,
            "due_date": due_date.isoformat(),
            "status": status,
            "score": None if score is None else float(score),
            "created_at": datetime.now().isoformat(timespec="seconds"),
        })
        _save_data(data)

        # Usability quality attribute: clear confirmation quickly
        _clear_screen()
        print("-" * 46)
        print("Assignment Added Successfully")
        print("-" * 46)
        print(f"Course: {course['name']}")
        print(f"Title:  {title}")
        print(f"Due:    {_format_date_long(due_date)}")
        print()
        print("1) Add another assignment")
        print("2) Return to Main Menu")
        next_choice = _safe_input("Choose: ").strip()
        if next_choice != "1":
            return


def choose_or_create_course(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Lets user pick an existing course OR create a new one.
    Also provides cancel to support backtracking (IH#5).
    """
    while True:
        print("Select a course:")
        for idx, c in enumerate(data["courses"], start=1):
            print(f"{idx}) {c['name']}")
        print(f"{len(data['courses']) + 1}) Create a new course")
        print("0) Cancel / Return to Main Menu")
        choice = _safe_input("Choose: ").strip()

        if choice == "0":
            return None

        try:
            n = int(choice)
        except ValueError:
            _pause("Please enter a number. Press Enter to continue...")
            continue

        if 1 <= n <= len(data["courses"]):
            return data["courses"][n - 1]

        if n == len(data["courses"]) + 1:
            name = _safe_input("New course name (required): ").strip()
            if not name:
                _pause("Course name is required. Press Enter to try again...")
                continue
            existing = _find_course_by_name(data, name)
            if existing:
                _pause("That course already exists. Press Enter to continue...")
                return existing
            course_id = _next_id(data["courses"])
            new_course = {"id": course_id, "name": name}
            data["courses"].append(new_course)
            _save_data(data)
            return new_course

        _pause("Invalid selection. Press Enter to try again...")


def choose_due_date() -> Optional[date]:
    """
    IH#7: multiple ways to do the same action (manual OR quick presets)
    """
    while True:
        _clear_screen()
        print("=" * 46)
        print("Choose Due Date")
        print("=" * 46)
        print()
        print("Pick one method:")
        print("1) Enter date manually (YYYY-MM-DD)")
        print("2) Quick presets")
        print("0) Cancel / Return")
        choice = _safe_input("Choose: ").strip()

        if choice == "0":
            return None

        if choice == "1":
            s = _safe_input("Due Date (YYYY-MM-DD): ").strip()
            try:
                d = _parse_date_yyyy_mm_dd(s)
                return d
            except ValueError:
                _pause("Invalid date format. Use YYYY-MM-DD. Press Enter to try again...")
                continue

        if choice == "2":
            return choose_quick_due_date()

        _pause("Invalid selection. Press Enter to try again...")


def choose_quick_due_date() -> Optional[date]:
    today = _today()
    options: List[Tuple[str, date]] = [
        ("Tomorrow", today + timedelta(days=1)),
        ("In 3 days", today + timedelta(days=3)),
        ("Next week", today + timedelta(days=7)),
        ("In 2 weeks", today + timedelta(days=14)),
    ]

    while True:
        _clear_screen()
        print("=" * 46)
        print("Quick Due Date Presets")
        print("=" * 46)
        print()
        for i, (label, d) in enumerate(options, start=1):
            print(f"{i}) {label} ({d.isoformat()})")
        print("0) Cancel / Return")
        choice = _safe_input("Choose: ").strip()

        if choice == "0":
            return None

        try:
            n = int(choice)
        except ValueError:
            _pause("Please enter a number. Press Enter to continue...")
            continue

        if 1 <= n <= len(options):
            return options[n - 1][1]

        _pause("Invalid selection. Press Enter to try again...")


def choose_status(default: str = "Not Started") -> Optional[str]:
    statuses = ["Not Started", "In Progress", "Completed"]
    while True:
        print()
        print("Status:")
        for i, s in enumerate(statuses, start=1):
            d = " (default)" if s == default else ""
            print(f"{i}) {s}{d}")
        print("0) Cancel / Return")
        choice = _safe_input("Choose: ").strip()
        if choice == "":
            return default
        if choice == "0":
            return None
        try:
            n = int(choice)
        except ValueError:
            _pause("Please enter a number. Press Enter to continue...")
            continue
        if 1 <= n <= len(statuses):
            return statuses[n - 1]
        _pause("Invalid selection. Press Enter to try again...")


def choose_optional_score() -> Optional[float]:
    print()
    print("Score (optional):")
    print("- Enter a number 0–100 (e.g., 92.5), or press Enter to skip.")
    while True:
        s = _safe_input("Score %: ").strip()
        if s == "":
            return None
        try:
            val = float(s)
            if 0.0 <= val <= 100.0:
                return val
            _pause("Score must be between 0 and 100. Press Enter to try again...")
        except ValueError:
            _pause("Invalid number. Press Enter to try again...")


# View Upcoming Deadlines

def upcoming_deadlines_flow(data: Dict[str, Any]) -> None:
    """
    Story: View upcoming deadlines sorted by due date.
    IH#3: show minimal list, allow viewing more info via details screen.
    """
    while True:
        _clear_screen()
        print("=" * 46)
        print("Upcoming Deadlines")
        print("=" * 46)
        print()

        # Performance quality attribute: show it responds quickly.
        start = time.perf_counter()

        items = list_assignments_sorted(data, only_incomplete=True)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        if not items:
            print("No upcoming incomplete assignments found.")
            print()
            print("0) Return to Main Menu")
            _safe_input("Choose: ")
            return

        print("Assignments (sorted by due date):")
        print("-" * 46)

        # Minimal info (IH#3: avoid info)
        for idx, a in enumerate(items, start=1):
            course = _get_course_by_id(data, a["course_id"])
            course_name = course["name"] if course else f"Course #{a['course_id']}"
            due = _parse_date_yyyy_mm_dd(a["due_date"])
            print(f"{idx}) {course_name}")
            print(f"   {a['title']}")
            print(f"   Due: {due.isoformat()}   Status: {a['status']}")
            print("-" * 46)

        print(f"(Loaded in ~{elapsed_ms:.0f} ms)")
        print()
        print("Options:")
        print("D) View details for an assignment (enter its number)")
        print("M) Return to Main Menu")
        choice = _safe_input("Choose (D/M): ").strip().lower()

        if choice == "m":
            return

        if choice == "d":
            num = _safe_input("Enter assignment number: ").strip()
            try:
                n = int(num)
                if 1 <= n <= len(items):
                    assignment_details_view(data, items[n - 1])
                else:
                    _pause("That number is out of range. Press Enter to continue...")
            except ValueError:
                _pause("Please enter a valid number. Press Enter to continue...")
            continue

        _pause("Invalid option. Press Enter to continue...")


def list_assignments_sorted(data: Dict[str, Any], only_incomplete: bool) -> List[Dict[str, Any]]:
    items = data["assignments"]
    if only_incomplete:
        items = [a for a in items if a.get("status") != "Completed"]

    def key_fn(a: Dict[str, Any]) -> Tuple[date, int]:
        try:
            d = _parse_date_yyyy_mm_dd(a["due_date"])
        except ValueError:
            d = date.max
        return (d, int(a["id"]))

    return sorted(items, key=key_fn)


def assignment_details_view(data: Dict[str, Any], a: Dict[str, Any]) -> None:
    """
    IH#3: user can gather more info if they want.
    """
    _clear_screen()
    print("=" * 46)
    print("Assignment Details")
    print("=" * 46)
    print()
    course = _get_course_by_id(data, a["course_id"])
    course_name = course["name"] if course else f"Course #{a['course_id']}"
    due = _parse_date_yyyy_mm_dd(a["due_date"])
    print(f"Course: {course_name}")
    print(f"Title:  {a['title']}")
    print(f"Due:    {_format_date_long(due)} ({due.isoformat()})")
    print(f"Status: {a['status']}")
    if a.get("score") is None:
        print("Score:  (none recorded)")
    else:
        print(f"Score:  {float(a['score']):.2f}%")
    print()
    print("0) Return to Deadlines List")
    _safe_input("Choose: ")


# Current Grade Calculation

def current_grade_flow(data: Dict[str, Any]) -> None:
    """
    Calculates simple average of recorded scores for a selected course.
    Accuracy quality attribute: correct math, 2 decimals.
    """
    while True:
        _clear_screen()
        print("=" * 46)
        print("Current Grade")
        print("=" * 46)
        print()
        course = pick_course(data)
        if course is None:
            return

        scored = [
            a for a in data["assignments"]
            if int(a["course_id"]) == int(course["id"]) and a.get("score") is not None
        ]

        _clear_screen()
        print("=" * 46)
        print(f"Current Grade for: {course['name']}")
        print("=" * 46)
        print()

        if not scored:
            print("No scores recorded for this course yet.")
            print("Tip: Add an assignment and enter a score to calculate a grade.")
            print()
            print("0) Return")
            _safe_input("Choose: ")
            return

        scores = [float(a["score"]) for a in scored]
        avg = sum(scores) / len(scores)

        print("Scores included:")
        for a in scored:
            print(f"- {a['title']}: {float(a['score']):.2f}%")
        print("-" * 46)
        print(f"Current Grade: {avg:.2f}%")
        print()
        print("0) Return to Main Menu")
        _safe_input("Choose: ")
        return


def pick_course(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    while True:
        print("Select a course:")
        for idx, c in enumerate(data["courses"], start=1):
            print(f"{idx}) {c['name']}")
        print("0) Return to Main Menu")
        choice = _safe_input("Choose: ").strip()
        if choice == "0":
            return None
        try:
            n = int(choice)
        except ValueError:
            _pause("Please enter a number. Press Enter to continue...")
            continue
        if 1 <= n <= len(data["courses"]):
            return data["courses"][n - 1]
        _pause("Invalid selection. Press Enter to try again...")


# Exit confirmation (IH#8)

def exit_confirmation() -> bool:
    _clear_screen()
    print("=" * 46)
    print("Exit Student Academic Helper")
    print("=" * 46)
    print()
    print("Are you sure you want to exit?")
    print("1) Yes, exit")
    print("2) No, return to Main Menu")
    choice = _safe_input("Choose: ").strip()
    return choice == "1"


# Main loop

def main() -> None:
    data = _load_data()
    ensure_seed_data(data)
    _save_data(data)

    while True:
        show_home()
        choice = _safe_input("Enter a number: ").strip()

        if choice == "1":
            add_assignment_flow(data)
            data = _load_data()
        elif choice == "2":
            upcoming_deadlines_flow(data)
            data = _load_data()
        elif choice == "3":
            current_grade_flow(data)
            data = _load_data()
        elif choice == "4":
            if exit_confirmation():
                _clear_screen()
                print("Good luck this term — you’ve got this. 👋")
                sys.exit(0)
        else:
            _pause("Please enter 1, 2, 3, or 4. Press Enter to continue...")


if __name__ == "__main__":
    main()
