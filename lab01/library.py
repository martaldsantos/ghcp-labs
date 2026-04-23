"""
Lab 01 — Code Generation Fundamentals
=======================================
A simple library management system. Participants learn core Copilot
features: inline completions, Chat, slash commands, and prompt crafting.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
from enum import Enum


class Genre(Enum):
    FICTION = "fiction"
    NON_FICTION = "non_fiction"
    SCIENCE = "science"
    HISTORY = "history"
    BIOGRAPHY = "biography"
    TECHNOLOGY = "technology"
    FANTASY = "fantasy"
    MYSTERY = "mystery"


@dataclass
class Book:
    isbn: str
    title: str
    author: str
    genre: Genre
    year_published: int
    copies_total: int = 1
    copies_available: int = 1

    @property
    def is_available(self) -> bool:
        return self.copies_available > 0


@dataclass
class Member:
    member_id: str
    name: str
    email: str
    joined_date: date = field(default_factory=date.today)
    is_active: bool = True


@dataclass
class Loan:
    loan_id: str
    book_isbn: str
    member_id: str
    loan_date: date = field(default_factory=date.today)
    due_date: Optional[date] = None
    return_date: Optional[date] = None

    def __post_init__(self):
        if self.due_date is None:
            self.due_date = self.loan_date + timedelta(days=14)

    @property
    def is_overdue(self) -> bool:
        if self.return_date:
            return False
        return date.today() > self.due_date

    @property
    def is_returned(self) -> bool:
        return self.return_date is not None


class Library:
    """Core library management system."""

    def __init__(self):
        self._books: dict[str, Book] = {}
        self._members: dict[str, Member] = {}
        self._loans: list[Loan] = []
        self._next_loan_id = 1

    # ── Book Management ──────────────────────────────────────────

    def add_book(self, book: Book) -> None:
        self._books[book.isbn] = book

    def get_book(self, isbn: str) -> Optional[Book]:
        return self._books.get(isbn)

    def search_books(self, query: str) -> list[Book]:
        """Search books by title or author (case-insensitive)."""
        query_lower = query.lower()
        return [
            b for b in self._books.values()
            if query_lower in b.title.lower() or query_lower in b.author.lower()
        ]

    # TODO: Add a method to search books by genre

    # TODO: Add a method to get all available books

    # TODO: Add a method to get the most popular books (most loans)

    # ── Member Management ────────────────────────────────────────

    def register_member(self, member: Member) -> None:
        self._members[member.member_id] = member

    def get_member(self, member_id: str) -> Optional[Member]:
        return self._members.get(member_id)

    # TODO: Add a method to deactivate a member

    # TODO: Add a method to search members by name

    # ── Loan Management ──────────────────────────────────────────

    def checkout_book(self, isbn: str, member_id: str) -> dict:
        """Check out a book to a member. Returns status dict."""
        book = self.get_book(isbn)
        if book is None:
            return {"status": "error", "message": "Book not found"}

        member = self.get_member(member_id)
        if member is None:
            return {"status": "error", "message": "Member not found"}

        if not member.is_active:
            return {"status": "error", "message": "Member is inactive"}

        if not book.is_available:
            return {"status": "error", "message": "No copies available"}

        loan_id = f"LOAN-{self._next_loan_id:06d}"
        self._next_loan_id += 1
        loan = Loan(loan_id=loan_id, book_isbn=isbn, member_id=member_id)
        self._loans.append(loan)
        book.copies_available -= 1

        return {"status": "ok", "loan_id": loan_id, "due_date": loan.due_date.isoformat()}

    def return_book(self, loan_id: str) -> dict:
        """Return a book. Returns status dict."""
        for loan in self._loans:
            if loan.loan_id == loan_id and not loan.is_returned:
                was_overdue = loan.is_overdue
                loan.return_date = date.today()
                book = self.get_book(loan.book_isbn)
                if book:
                    book.copies_available += 1
                return {"status": "ok", "was_overdue": was_overdue}
        return {"status": "error", "message": "Loan not found or already returned"}

    # TODO: Add a method to get all overdue loans

    # TODO: Add a method to extend a loan by N days

    # TODO: Add a method to get a member's loan history

    # ── Reports ──────────────────────────────────────────────────

    # TODO: Add a method that returns a summary dict with:
    #       total_books, total_members, active_loans, overdue_loans
