from django.contrib import admin
from django.template.defaultfilters import truncatechars, truncatewords  # noqa: F401

from .models import Author, AuthorProfile, Book, BookInstance, Genre, Language


@admin.register(Genre)
class GenreModelAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(Language)
class LanguageModelAdmin(admin.ModelAdmin):
    list_display = ["name"]


class AuthorProfileInlineModelAdmin(admin.TabularInline):
    model = AuthorProfile


class BookInlineModelAdmin(admin.TabularInline):
    """Defines format of inline book insertion (used in AuthorAdmin)"""

    model = Book


@admin.register(Author)
class AuthorModelAdmin(admin.ModelAdmin):
    """Administration object for Author models.
    Defines:
     - fields to be displayed in list view (list_display)
     - orders fields in detail view (fields),
       grouping the date fields horizontally
     - adds inline addition of books in author view (inlines)
    """

    list_display = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    fields = ["first_name", "last_name", ("date_of_birth", "date_of_death")]
    date_hierarchy = "date_of_birth"
    # readonly_fields = ["date_of_death", ]
    inlines = [AuthorProfileInlineModelAdmin, BookInlineModelAdmin]


@admin.register(AuthorProfile)
class AuthorProfileModelAdmin(admin.ModelAdmin):
    pass


class BooksInstanceInlineModelAdmin(admin.TabularInline):
    """Defines format of inline book instance insertion (used in BookAdmin)"""

    model = BookInstance
    # extra = 10
    # can_delete = False


@admin.register(Book)
class BookModelAdmin(admin.ModelAdmin):
    """Administration object for Book models.
    Defines:
     - fields to be displayed in list view (list_display)
     - adds inline addition of book instances in book view (inlines)
    """

    list_display = ["title", "author", "display_genre"]
    raw_id_fields = ["author"]
    # list_filter = ["genre", ]
    filter_vertical = ["genre"]
    inlines = [BooksInstanceInlineModelAdmin]


@admin.register(BookInstance)
class BookInstanceModelAdmin(admin.ModelAdmin):
    """Administration object for BookInstance models.
    Defines:
     - fields to be displayed in list view (list_display)
     - filters that will be displayed in sidebar (list_filter)
     - grouping of fields into sections (fieldsets)
    """

    list_display = ["id", "get_imprint", "book", "status", "borrower", "due_back"]
    list_filter = ["status", "due_back"]
    search_fields = ["imprint"]
    # fmt: off
    fieldsets = (
        (None, {
            "fields": ("book", "imprint", "id")
        }),
        ("Availability", {
            "fields": ("status", "due_back", "borrower")
        }),
    )
    # fmt: on
    actions = ["change_status_to_maintenance"]

    def get_queryset(self, request):
        return super(BookInstanceModelAdmin, self).get_queryset(request).select_related("book", "borrower")

    # fmt: off
    def change_status_to_maintenance(self, request, queryset):
        queryset.update(status=BookInstance.LoanStatus.MAINTENANCE)
    change_status_to_maintenance.short_description = "Mark selected books as on maintenance"
    # fmt: on

    # fmt: off
    def get_imprint(self, obj):
        # return truncatewords(obj.imprint, 1)
        return obj.imprint
    get_imprint.short_description = "imprint"
    # fmt: on
