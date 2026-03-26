import os
from pathlib import Path

from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = "Assign local images from media/movie/images/ to movies in the database"

    def handle(self, *args, **kwargs):
        base_dir = Path(__file__).resolve().parents[3]
        images_folder = base_dir / "media" / "movie" / "images"

        if not images_folder.exists():
            self.stderr.write(
                self.style.ERROR(f"Images folder not found: {images_folder}")
            )
            return

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        assigned_count = 0
        missing_count = 0

        for movie in movies:
            image_relative_path = self.find_image_for_movie(movie.title, images_folder)

            if not image_relative_path:
                missing_count += 1
                self.stderr.write(f"Image not found for: {movie.title}")
                continue

            movie.image = image_relative_path
            movie.save(update_fields=["image"])
            assigned_count += 1
            self.stdout.write(
                self.style.SUCCESS(f"Image assigned for: {movie.title}")
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Process finished. Updated: {assigned_count}, Missing: {missing_count}"
            )
        )

    def find_image_for_movie(self, movie_title, images_folder):
        main_title = self.extract_main_title(movie_title)
        candidates = [
            f"m_{movie_title}",
            movie_title,
            f"m_{main_title}",
            main_title,
            self.normalize_name(f"m_{movie_title}"),
            self.normalize_name(movie_title),
            self.normalize_name(f"m_{main_title}"),
            self.normalize_name(main_title),
        ]

        files_by_stem = {}
        for image_file in images_folder.iterdir():
            if image_file.is_file():
                files_by_stem.setdefault(image_file.stem.lower(), image_file.name)

        for candidate in candidates:
            matched_name = files_by_stem.get(candidate.lower())
            if matched_name:
                return os.path.join("movie", "images", matched_name).replace("\\", "/")

        return None

    def normalize_name(self, value):
        normalized = value.lower().strip()
        for char in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            normalized = normalized.replace(char, "")
        return normalized

    def extract_main_title(self, movie_title):
        for separator in [":", " or ", " - "]:
            if separator in movie_title:
                return movie_title.split(separator, 1)[0].strip()
        return movie_title.strip()
