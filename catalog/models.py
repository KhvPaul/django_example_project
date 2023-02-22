import uuid
from datetime import date

from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class Genre(models.Model):
    """Model representing a book genre (e.g. Science Fiction, Non Fiction)."""

    # fmt: off
    name = models.CharField(
        _("name"),
        max_length=200,
        help_text=_("Enter a book genre (e.g. Scince fiction, French Poentry etc.)")
    )
    # fmt: on

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""

    # fmt: off
    name = models.CharField(
        _("name"),
        max_length=50,
        help_text=_("Enter the book's natural language (e.g. English, French etc.)")
    )
    # fmt: on

    def __str__(self):
        """String for representing the Model object (in Admin site etc.)"""
        return self.name


class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""

    title = models.CharField(_("title"), max_length=200)
    author = models.ForeignKey("Author", on_delete=models.SET_NULL, null=True)
    # Foreign Key used because book can only have one author, but authors can have multiple books
    # Author as a string rather than object because it hasn't been declared yet in file.
    summary = models.TextField(_("summary"), max_length=1000, help_text=_("Enter a brief description of the book"))
    isbn = models.CharField(_("ISBN"), max_length=13, help_text=_("13 character ISBN number"))
    genre = models.ManyToManyField(Genre, verbose_name=_("genre"), help_text=_("Select a genre for this book"))
    # ManyToManyField used because a genre can contain many books and a Book can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    language = models.ForeignKey("Language", verbose_name=_("language"), on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ["title", "author"]

    def __str__(self):
        """String for representing the Model object."""
        return self.title

    def display_genre(self):
        """Creates a string for the Genre. This is required to display genre in Admin."""
        return ", ".join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = "Genre"

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse("book-detail", args=[str(self.id)])


class BookInstance(models.Model):
    """Model representing a specific copy of a book (i.e. that can be borrowed from the library)."""

    # fmt: off
    class LoanStatus(models.IntegerChoices):
        MAINTENANCE = 1, _("Maintenance")  # d
        ON_LOAN = 2, _("On loan")          # o
        AVAILABLE = 3, _("Available")      # a
        RESERVED = 4, _("Reserved")        # r
    # fmt: on
    id = models.UUIDField(  # noqa: A003
        primary_key=True, default=uuid.uuid4, help_text=_("Unique ID for this particular book across whole library")
    )
    book = models.ForeignKey("Book", on_delete=models.SET_NULL, null=True)
    imprint = models.CharField(_("imprint"), max_length=200, help_text=_("Enter publisher trade name"))
    due_back = models.DateField(_("due back"), null=True, blank=True)
    status = models.PositiveSmallIntegerField(
        choices=LoanStatus.choices, default=LoanStatus.MAINTENANCE, blank=True, help_text=_("Book availability")
    )
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["due_back"]
        permissions = (("can_mark_returned", "Set book as returned"),)

    @property
    def is_overdue(self):
        if self.due_back and date.today() > self.due_back:
            return True
        return False

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.id} ({self.book.title})"


class Author(models.Model):
    """Model representing an author."""

    first_name = models.CharField(_("first name"), max_length=100)
    last_name = models.CharField(_("last name"), max_length=100)
    date_of_birth = models.DateField(_("date of birth"), null=True, blank=True)
    date_of_death = models.DateField(_("date of death"), null=True, blank=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        """String for representing the Model object."""
        return f"{self.last_name}, {self.first_name}"

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse("author-detail", args=[str(self.id)])


class AuthorProfile(models.Model):
    author = models.OneToOneField("Author", on_delete=models.CASCADE)
    about = models.TextField(_("about"), max_length=1000, help_text=_("Author bio"))

    def __str__(self):
        return f"{self.author.last_name} {self.author.first_name} Profile"
