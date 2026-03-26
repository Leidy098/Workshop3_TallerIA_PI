import numpy as np
from django.core.management.base import BaseCommand

from movie.models import Movie


class Command(BaseCommand):
    help = "Verify stored movie embeddings by reading the binary field as float32 arrays"

    def handle(self, *args, **kwargs):
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        for movie in movies:
            if not movie.emb:
                self.stdout.write(self.style.WARNING(f"{movie.title}: no embedding stored"))
                continue

            try:
                embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)
            except ValueError as exc:
                self.stderr.write(f"{movie.title}: could not decode embedding ({exc})")
                continue

            if embedding_vector.size == 0:
                self.stdout.write(self.style.WARNING(f"{movie.title}: empty embedding"))
                continue

            preview = np.array2string(embedding_vector[:5], precision=6, separator=", ")
            self.stdout.write(f"{movie.title}: {preview}")
