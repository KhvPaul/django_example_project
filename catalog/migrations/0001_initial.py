# Generated by Django 3.1.1 on 2020-09-07 14:18

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name="Author",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("first_name", models.CharField(max_length=100, verbose_name="first name")),
                ("last_name", models.CharField(max_length=100, verbose_name="last name")),
                ("date_of_birth", models.DateField(blank=True, null=True, verbose_name="date of birth")),
                ("date_of_death", models.DateField(blank=True, null=True, verbose_name="date of death")),
            ],
        ),
        migrations.CreateModel(
            name="Book",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200, verbose_name="title")),
                ("summary", models.TextField(help_text="Enter a brief description of the book", max_length=1000, verbose_name="summary")),
                ("isbn", models.CharField(help_text="13 character ISBN number", max_length=13, verbose_name="ISBN")),
                ("author", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="catalog.author")),
            ],
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(help_text="Enter a book genre (e.g. Scince fiction, French Poentry etc.)", max_length=200, verbose_name="name")),
            ],
        ),
        migrations.CreateModel(
            name="BookInstance",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, help_text="Unique ID for this particular book across whole library", primary_key=True, serialize=False)),
                ("imprint", models.CharField(help_text="Enter publisher trade name", max_length=200, verbose_name="imprint")),
                ("due_back", models.DateField(blank=True, null=True, verbose_name="due back")),
                ("status", models.PositiveSmallIntegerField(blank=True, choices=[(1, "Maintenance"), (2, "On loan"), (3, "Available"), (4, "Reserved")], default=1)),
                ("book", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="catalog.book")),
            ],
            options={
                "ordering": ["due_back"],
            },
        ),
        migrations.AddField(
            model_name="book",
            name="genre",
            field=models.ManyToManyField(help_text="Select a genre for this book", to="catalog.Genre", verbose_name="genre"),
        ),
    ]
