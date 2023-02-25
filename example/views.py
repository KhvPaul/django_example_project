from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import generic

from .forms import ImageForm
from .models import Image, Product


# Create your views here.


class ProductListView(generic.ListView):
    model = Product
    paginate_by = 4
    template_name = "example/product_list.html"


def list_example(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 4)  # Show 4 contacts per page.

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(request, "example/product_list.html", {"page_obj": page_obj, "product_list": page_obj.object_list})


class ProductDeleteView(generic.DeleteView):
    model = Product
    success_url = reverse_lazy("products")
    template_name = "example/product_delete.html"


def static_example_view(request):
    file = Image.objects.last()
    return render(request, "example/example.html", {"file": file})


def create_image(request):
    if request.method == "POST":
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse("example"))
    else:
        form = ImageForm()
    return render(request, "example/load_file.html", {"form": form})
