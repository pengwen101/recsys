import requests
import re
import time
import os
import pandas as pd
from dotenv import load_dotenv
from ratelimit import limits, sleep_and_retry
from requests.exceptions import RequestException, ReadTimeout, ConnectionError

load_dotenv()

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {os.getenv('TMDB_TOKEN')}"
}

CHECKPOINT_PATH = "data/movies_details_checkpoint.parquet"
OUTPUT_PATH     = "data/movies_details.parquet"


# ── API calls ──────────────────────────────────────────────────────────────────

@sleep_and_retry
@limits(calls=35, period=10)
def _get(url, params=None, max_retries=3):
    """Throttled GET with robust retry logic for 429s and Network Timeouts."""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=10)

            # Handle Rate Limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 10))
                print(f"  [rate limit] sleeping {retry_after}s")
                time.sleep(retry_after)
                continue  # Loop back and try again
                
            # If it's a 200 OK, or a 404 Not Found, return it to let the main logic handle it
            return response

        except (ReadTimeout, ConnectionError) as e:
            wait_time = 5 * (attempt + 1)  # Exponential backoff: 5s, 10s, 15s
            print(f"  [network error] {type(e).__name__}. Retrying in {wait_time}s (Attempt {attempt+1}/{max_retries})")
            time.sleep(wait_time)
            
   
    class FailedResponse:
        status_code = 500
        
    return FailedResponse()


def get_tmdb_id(movie_title: str) -> int | None:
    match = re.search(r'\((\d{4})\)', movie_title)
    year  = match.group(1) if match else None
    title = re.sub(r'\s*\(\d{4}\)', '', movie_title).strip()

    url = "https://api.themoviedb.org/3/search/movie"

    # try with year first — more precise
    if year:
        r = _get(url, params={"query": title, "primary_release_year": year})
        if r.status_code == 200:
            results = r.json().get("results", [])
            if results:
                return results[0]["id"]

    # fall back without year
    r = _get(url, params={"query": title})
    if r.status_code == 200:
        results = r.json().get("results", [])
        return results[0]["id"] if results else None

    return None


def get_movie_details(tmdb_id: int) -> dict | None:
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    r   = _get(url, params={"append_to_response": "credits,keywords"})

    if r.status_code != 200:
        return None

    data = r.json()

    directors = [
        {"id": c["id"], "name": c["name"]}
        for c in data.get("credits", {}).get("crew", [])
        if c["job"] == "Director"
    ]
    casts = [
        {"id": c["id"], "name": c["name"]}
        for c in data.get("credits", {}).get("cast", [])[:3]
    ]
    keywords = [
        k["name"]
        for k in data.get("keywords", {}).get("keywords", [])[:10]
    ]
    poster_path = data.get("poster_path")

    return {
        "overview":   data.get("overview", ""),
        "directors":  directors,
        "casts":      casts,
        "keywords":   keywords,
        "poster_url": f"https://image.tmdb.org/t/p/w200{poster_path}" if poster_path else None
    }


# ── enrichment ─────────────────────────────────────────────────────────────────

EMPTY = {
    "tmdb_id":   None,
    "overview":  None,
    "directors": None,
    "casts":     None,
    "keywords":  None,
    "poster_url": None
}

def enrich(movie_dict: dict) -> dict:
    tmdb_id = get_tmdb_id(movie_dict["title"])
    movie_dict["tmdb_id"] = tmdb_id

    if not tmdb_id:
        movie_dict.update({k: v for k, v in EMPTY.items() if k != "tmdb_id"})
        return movie_dict

    details = get_movie_details(tmdb_id)
    if not details:
        movie_dict.update({k: v for k, v in EMPTY.items() if k != "tmdb_id"})
        return movie_dict

    movie_dict.update(details)
    return movie_dict


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    movies_df   = pd.read_parquet("data/movies.parquet")
    movies_list = movies_df.to_dict(orient="records")
    total       = len(movies_list)

    # resume from checkpoint if exists
    if os.path.exists(CHECKPOINT_PATH):
        done_df  = pd.read_parquet(CHECKPOINT_PATH)
        done_ids = set(done_df["movieId"])
        results  = done_df.to_dict(orient="records")
        print(f"Resuming — {len(done_ids)}/{total} already done")
    else:
        done_ids = set()
        results  = []

    for i, movie in enumerate(movies_list):
        if movie["movieId"] in done_ids:
            continue

        enriched = enrich(movie)
        results.append(enriched)

        current = len(results)

        # progress
        if current % 50 == 0:
            print(f"[{current}/{total}] latest: {movie['title']}")

        # checkpoint every 500
        if current % 500 == 0:
            pd.DataFrame(results).to_parquet(CHECKPOINT_PATH)
            print(f"  checkpoint saved at {current}")

    # final save
    final_df = pd.DataFrame(results)
    final_df.to_parquet(OUTPUT_PATH)
    print(f"\nDone. {len(final_df)} movies saved to {OUTPUT_PATH}")

    # clean up checkpoint
    if os.path.exists(CHECKPOINT_PATH):
        os.remove(CHECKPOINT_PATH)
        print("Checkpoint removed.")


if __name__ == "__main__":
    main()