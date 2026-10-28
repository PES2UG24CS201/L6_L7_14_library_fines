import pytest
from library_fines import late_fine, can_borrow, renewal_status


# ---------- late_fine ----------
def test_returned_on_time():
    assert late_fine("student", 10, False) == 0


def test_unknown_member_raises():
    with pytest.raises(ValueError, match="unknown member"):
        late_fine("visitor", 5, False)


def test_negative_days_raises():
    with pytest.raises(ValueError, match="invalid days"):
        late_fine("student", -1, False)


def test_faculty_within_loan_period():
    assert late_fine("faculty", 20, False) == 0


def test_student_overdue():
    # 20 - 14 = 6 days overdue * Rs 2
    assert late_fine("student", 20, False) == 12


def test_fine_is_capped_at_200():
    # 46 days overdue * 5 = 230 -> capped to 200
    assert late_fine("guest", 60, False) == 200


def test_damaged_book_adds_flat_charge():
    assert late_fine("student", 10, True) == 150


# ---------- can_borrow ----------
def test_can_borrow():
    assert can_borrow(1, 0, "student") is True


def test_cannot_borrow_with_high_pending_fine():
    assert can_borrow(0, 150, "student") is False


def test_faculty_can_borrow_up_to_limit():
    assert can_borrow(5, 0, "faculty") is True


# ---------- renewal_status ----------
def test_renewal_denied_when_reserved():
    assert renewal_status(0, True, 5) == "denied"


def test_renewal_limit_reached():
    assert renewal_status(2, False, 5) == "limit reached"


def test_renewal_overdue():
    assert renewal_status(1, False, -1) == "overdue"


def test_renewal_success():
    assert renewal_status(0, False, 5) == "renewed"
