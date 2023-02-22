import datetime
import time

from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction

from catalog.forms import ContactFrom, RegisterForm, RenewBookForm
from catalog.models import Author, Book, BookInstance

from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.mail import BadHeaderError, send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic


from .tasks import send_mail as celery_send_mail

User = get_user_model()


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = BookInstance.objects.filter(status__exact=BookInstance.LoanStatus.AVAILABLE).count()
    num_authors = Author.objects.count()  # The "all()" is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        "index.html",
        context={
            "num_books": num_books,
            "num_instances": num_instances,
            "num_instances_available": num_instances_available,
            "num_authors": num_authors,
            "num_visits": num_visits,
        },
    )


def contact_form(request):
    if request.method == "POST":
        form = ContactFrom(request.POST)
        if form.is_valid():
            subject = form.cleaned_data["subject"]
            from_email = form.cleaned_data["from_email"]
            message = form.cleaned_data["message"]
            # celery_send_mail.delay(subject, message, from_email)
            messages.add_message(request, messages.SUCCESS, "Message sent")
            # try:
            #     send_mail(subject, message, from_email, ["admin@example.com"])
            #     messages.add_message(request, messages.SUCCESS, "Message sent")
            # except BadHeaderError:
            #     messages.add_message(request, messages.ERROR, "Message not sent")
            return redirect("contact")
    else:
        form = ContactFrom()
    return render(
        request,
        "catalog/contact.html",
        context={
            "form": form,
        },
    )


class RegisterFormView(generic.FormView):
    template_name = "registration/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        # form.cleaned_data.get("password1")

        # username = self.request.POST["username"]
        # password = self.request.POST["password1"]

        user = authenticate(self.request, username=user.username, password=form.cleaned_data.get("password1"))
        login(self.request, user)
        return super(RegisterFormView, self).form_valid(form)


class UpdateProfile(LoginRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "registration/update_profile.html"
    success_url = reverse_lazy("index")
    success_message = "Profile updated"

    def get_object(self, queryset=None):
        user = self.request.user
        return user


class UserProfile(LoginRequiredMixin, generic.DetailView):
    model = User
    template_name = "registration/profile.html"

    def get_object(self, queryset=None):
        user = self.request.user
        return user

    # def get_context_data(self, **kwargs):
    #     context = super(UserProfile, self).get_context_data(**kwargs)
    #     context["posts_count"] = self.get_object().posts_set.count()
    #     return context


class BookListView(generic.ListView):
    """Generic class-based view for a list of books."""

    model = Book
    queryset = Book.objects.select_related("author")
    paginate_by = 3


class BookDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""

    model = Book


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""

    model = Author
    paginate_by = 2

    def get_queryset(self):
        return super(AuthorListView, self).get_queryset().select_related("authorprofile")


class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""

    model = Author


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    # fmt: off
    def get_queryset(self):
        return BookInstance.objects.filter(
            borrower=self.request.user
        ).filter(
            status__exact=BookInstance.LoanStatus.ON_LOAN
        ).order_by("due_back")
    # fmt: on


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""

    model = BookInstance
    permission_required = "catalog.can_mark_returned"
    template_name = "catalog/bookinstance_list_borrowed_all.html"
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact=BookInstance.LoanStatus.ON_LOAN).order_by("due_back")


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["renewal_date"]
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("all-borrowed"))

    # If this is a GET (or any other method) create the default form
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={"renewal_date": proposed_renewal_date})

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


class AuthorCreate(PermissionRequiredMixin, generic.CreateView):
    model = Author
    fields = "__all__"  # Not recommended (potential security issue if more fields added)
    initial = {"date_of_death": "11/06/2020"}
    permission_required = "catalog.can_mark_returned"


class AuthorUpdate(PermissionRequiredMixin, generic.UpdateView):
    model = Author
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    permission_required = "catalog.can_mark_returned"


class AuthorDelete(PermissionRequiredMixin, generic.DeleteView):
    model = Author
    success_url = reverse_lazy("authors")
    permission_required = "catalog.can_mark_returned"


# Classes created for the forms challenge
class BookCreate(PermissionRequiredMixin, generic.CreateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.can_mark_returned"


class BookUpdate(PermissionRequiredMixin, generic.UpdateView):
    model = Book
    fields = ["title", "author", "summary", "isbn", "genre", "language"]
    permission_required = "catalog.can_mark_returned"


class BookDelete(PermissionRequiredMixin, generic.DeleteView):
    model = Book
    success_url = reverse_lazy("books")
    permission_required = "catalog.can_mark_returned"
