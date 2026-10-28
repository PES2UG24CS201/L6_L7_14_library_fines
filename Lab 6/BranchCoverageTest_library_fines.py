import pytest
from library_fines import late_fine, can_borrow, renewal_status


# ================= late_fine =================
def test_returned_on_time():
    assert late_fine("student", 10, False) == 0


def test_unknown_member_raises():
    with pytest.raises(ValueError, match="unknown member"):
        late_fine("visitor", 5, False)


def test_negative_days_raises():
    with pytest.raises(ValueError, match="invalid days"):
        late_fine("student", -1, False)


def test_zero_days_is_valid():
    # boundary: days_kept == 0 must NOT raise
    assert late_fine("student", 0, False) == 0


@pytest.mark.parametrize("member,days,expected", [
    ("student", 14, 0),    # exactly on the 14-day limit
    ("student", 15, 2),    # 1 day overdue * 2
    ("guest", 14, 0),
    ("guest", 16, 10),     # 2 days overdue * 5
    ("faculty", 30, 0),    # exactly on the 30-day limit
    ("faculty", 31, 1),    # 1 day overdue * 1
    ("faculty", 20, 0),    # would be overdue for a student, not faculty
])
def test_loan_period_boundaries(member, days, expected):
    assert late_fine(member, days, False) == expected


def test_fine_exactly_200_is_not_capped():
    # 100 days overdue * 2 = 200 (cap condition is > 200)
    assert late_fine("student", 114, False) == 200


def test_fine_just_above_200_is_capped():
    # 101 days overdue * 2 = 202 -> 200
    assert late_fine("student", 115, False) == 200


def test_guest_fine_capped():
    # 46 * 5 = 230 -> 200
    assert late_fine("guest", 60, False) == 200


def test_damaged_only():
    assert late_fine("student", 10, True) == 150


def test_damaged_and_overdue():
    # 6 * 2 = 12, + 150
    assert late_fine("student", 20, True) == 162


def test_damaged_and_capped():
    # capped fine 200 + 150 damage
    assert late_fine("guest", 100, True) == 350


def test_not_damaged_and_overdue():
    assert late_fine("student", 20, False) == 12


# ================= can_borrow =================
def test_can_borrow():
    assert can_borrow(1, 0, "student") is True


def test_student_at_book_limit():
    assert can_borrow(3, 0, "student") is False


def test_student_just_below_limit():
    assert can_borrow(2, 0, "student") is True


def test_guest_uses_student_limit():
    assert can_borrow(3, 0, "guest") is False


def test_faculty_below_limit():
    assert can_borrow(9, 0, "faculty") is True


def test_faculty_at_limit():
    assert can_borrow(10, 0, "faculty") is False


def test_pending_fine_above_100_blocks_borrowing():
    assert can_borrow(0, 101, "student") is False


def test_pending_fine_exactly_100_allows_borrowing():
    assert can_borrow(0, 100, "student") is True


def test_pending_fine_blocks_faculty_too():
    assert can_borrow(0, 101, "faculty") is False


# ================= renewal_status =================
def test_denied_when_reserved():
    assert renewal_status(0, True, 5) == "denied"


def test_reservation_takes_priority_over_limit():
    assert renewal_status(2, True, -3) == "denied"


def test_limit_reached_at_two_renewals():
    assert renewal_status(2, False, 5) == "limit reached"


def test_limit_reached_above_two_renewals():
    assert renewal_status(3, False, 5) == "limit reached"


def test_limit_takes_priority_over_overdue():
    assert renewal_status(2, False, -1) == "limit reached"


def test_overdue_when_days_left_negative():
    assert renewal_status(1, False, -1) == "overdue"


def test_renewed_when_days_left_zero():
    # boundary: days_left == 0 is not overdue
    assert renewal_status(1, False, 0) == "renewed"


def test_renewed_normal_case():
    assert renewal_status(0, False, 5) == "renewed"
