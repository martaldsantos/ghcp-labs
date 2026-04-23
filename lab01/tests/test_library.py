"""Basic tests for the Library system — validates existing methods work."""

import pytest
from datetime import date, timedelta
from library import Library, Book, Member, Genre, Loan


@pytest.fixture
def library():
    lib = Library()
    lib.add_book(Book("978-1", "Python Basics", "Alice Smith", Genre.TECHNOLOGY, 2021, copies_total=2, copies_available=2))
    lib.add_book(Book("978-2", "Mystery Novel", "Bob Jones", Genre.MYSTERY, 2019))
    lib.register_member(Member("M001", "Charlie", "charlie@example.com"))
    lib.register_member(Member("M002", "Dana", "dana@example.com"))
    return lib


class TestBookManagement:
    def test_add_and_get_book(self, library):
        book = library.get_book("978-1")
        assert book is not None
        assert book.title == "Python Basics"

    def test_get_book_not_found(self, library):
        assert library.get_book("000") is None

    def test_search_books_by_title(self, library):
        results = library.search_books("python")
        assert len(results) == 1
        assert results[0].isbn == "978-1"

    def test_search_books_by_author(self, library):
        results = library.search_books("bob")
        assert len(results) == 1
        assert results[0].isbn == "978-2"

    def test_search_books_no_match(self, library):
        assert library.search_books("nonexistent") == []


class TestCheckout:
    def test_checkout_success(self, library):
        result = library.checkout_book("978-1", "M001")
        assert result["status"] == "ok"
        assert "loan_id" in result
        assert library.get_book("978-1").copies_available == 1

    def test_checkout_unknown_book(self, library):
        result = library.checkout_book("000", "M001")
        assert result["status"] == "error"

    def test_checkout_unknown_member(self, library):
        result = library.checkout_book("978-1", "UNKNOWN")
        assert result["status"] == "error"

    def test_checkout_no_copies(self, library):
        library.checkout_book("978-2", "M001")  # only 1 copy
        result = library.checkout_book("978-2", "M002")
        assert result["status"] == "error"
        assert "No copies" in result["message"]

    def test_checkout_inactive_member(self, library):
        library.get_member("M002").is_active = False
        result = library.checkout_book("978-1", "M002")
        assert result["status"] == "error"
        assert "inactive" in result["message"].lower()


class TestReturn:
    def test_return_success(self, library):
        checkout = library.checkout_book("978-1", "M001")
        result = library.return_book(checkout["loan_id"])
        assert result["status"] == "ok"
        assert result["was_overdue"] is False
        assert library.get_book("978-1").copies_available == 2

    def test_return_not_found(self, library):
        result = library.return_book("LOAN-999999")
        assert result["status"] == "error"

    def test_return_overdue(self, library):
        checkout = library.checkout_book("978-1", "M001")
        # Manually set due_date in the past to simulate overdue
        loan = library._loans[-1]
        loan.due_date = date.today() - timedelta(days=1)
        result = library.return_book(checkout["loan_id"])
        assert result["status"] == "ok"
        assert result["was_overdue"] is True
