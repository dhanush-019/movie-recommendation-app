import pandas as pd
import ast

df = pd.read_csv("movies_metadata.csv", low_memory=False)

def get_genre_names(genre_str):
    try:
        genres = ast.literal_eval(genre_str)
        return [g["name"] for g in genres]
    except (ValueError, SyntaxError):
        return []

df["genre_list"] = df["genres"].apply(get_genre_names)

mood_map = {
    "cozy": ["Family", "Animation", "Romance"],
    "heavy": ["Drama"],
    "hyped": ["Action"],
    "laugh": ["Comedy"],
    "spooked": ["Horror"],
    "curious": ["Science Fiction", "Mystery"]
}

while True:
    mood = input("\nHow are you feeling? (cozy/heavy/hyped/laugh/spooked/curious, or 'quit'): ")
    if mood == "quit":
        break
    if mood not in mood_map:
        print("Not a valid mood, try again.")
        continue

    picks = df[df["genre_list"].apply(lambda g: any(x in g for x in mood_map[mood]))]
    picks = picks.sort_values("vote_average", ascending=False).head(10)

    for _, row in picks.iterrows():
        year = str(row["release_date"])[:4] if pd.notna(row["release_date"]) else "?"
        poster_url = f"https://image.tmdb.org/t/p/w342{row['poster_path']}" if pd.notna(row["poster_path"]) else "no poster"
        imdb_url = f"https://www.imdb.com/title/{row['imdb_id']}/" if pd.notna(row["imdb_id"]) else "no link"
        print(f"\n{row['title']} ({year}) - rating {row['vote_average']}")
        print(f"Poster: {poster_url}")
        print(f"IMDb: {imdb_url}