import numpy as np
from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = "Display the stored embedding preview for a random movie"

    def handle(self, *args, **kwargs):
        movie = Movie.objects.order_by("?").first()

        if movie is None:
            self.stdout.write(self.style.WARNING("No movies found in the database"))
            return

        if not movie.emb:
            self.stdout.write(self.style.WARNING(f"{movie.title}: no embedding stored"))
            return

        try:
            embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)
        except ValueError as exc:
            self.stderr.write(f"{movie.title}: could not decode embedding ({exc})")
            return

        if embedding_vector.size == 0:
            self.stdout.write(self.style.WARNING(f"{movie.title}: empty embedding"))
            return

        preview = np.array2string(embedding_vector[:5], precision=6, separator=", ")
        self.stdout.write(f"Random movie: {movie.title}")
        self.stdout.write(f"Embedding length: {embedding_vector.size}")
        self.stdout.write(f"First values: {preview}")
