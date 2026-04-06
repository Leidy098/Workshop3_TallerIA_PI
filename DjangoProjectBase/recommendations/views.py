import os
from pathlib import Path

import numpy as np
from django.conf import settings
from django.shortcuts import render
from dotenv import load_dotenv
from openai import OpenAI

from movie.models import Movie


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def get_openai_client():
    env_path = Path(settings.BASE_DIR).parent / 'openAI.env'
    load_dotenv(env_path)

    api_key = os.environ.get('openai_apikey') or os.environ.get('openai_api_key')
    if not api_key:
        raise ValueError('OpenAI API key not found in openAI.env')

    return OpenAI(api_key=api_key)


def recommendations(request):
    prompt = request.GET.get('recommendationPrompt', '').strip()
    best_movie = None
    error_message = None

    if prompt:
        try:
            client = get_openai_client()
            response = client.embeddings.create(
                input=[prompt],
                model='text-embedding-3-small',
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

            max_similarity = -1
            for movie in Movie.objects.all():
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                if movie_emb.size == 0:
                    continue

                similarity = cosine_similarity(prompt_emb, movie_emb)
                if similarity > max_similarity:
                    max_similarity = similarity
                    best_movie = movie

            if best_movie is None:
                error_message = 'No fue posible encontrar una pelicula con embeddings validos.'
        except Exception as exc:
            error_message = f'No fue posible generar la recomendacion: {exc}'

    context = {
        'recommendation_prompt': prompt,
        'recommended_movie': best_movie,
        'error_message': error_message,
    }
    return render(request, 'recommendations.html', context)
