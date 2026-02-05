import json
import os
import time
import random
from datetime import datetime, timedelta
from eneet import NitterClient

# Load config
with open('config.json', 'r', encoding='utf-8') as f:
    CONFIG = json.load(f)

USERNAME = CONFIG['username']
PERIOD_DAYS = CONFIG.get('period_days', 10)
INSTANCE = CONFIG.get('instance', 'https://nitter.net')

# Parse dates (None = unlimited)
_start = CONFIG.get('start_date')
_end = CONFIG.get('end_date')
START_DATE = datetime.strptime(_start, '%Y-%m-%d') if _start else None
END_DATE = datetime.strptime(_end, '%Y-%m-%d') if _end else None

DATA_FILE = f"posts_{USERNAME}.jsonl"
SEEN_IDS = set()


def load_ids():
    print(f"Loading existing IDs from {DATA_FILE}...")
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                if data.get('id'):
                    SEEN_IDS.add(data['id'])
            except:
                pass
    print(f"Loaded {len(SEEN_IDS)} valid IDs.")


def save_tweet(tweet, query):
    """Save a single tweet immediately to disk with ordered keys: id, date first."""
    if not tweet.id or tweet.id in SEEN_IDS:
        return 0
    SEEN_IDS.add(tweet.id)

    data = {
        'id': tweet.id,
        'date': tweet.date.isoformat(),
        'username': tweet.username,
        'display_name': tweet.display_name,
        'text': tweet.text,
        'likes': tweet.likes,
        'retweets': tweet.retweets,
        'replies': tweet.replies,
        'is_retweet': tweet.is_retweet,
        'is_reply': tweet.is_reply,
        'images': tweet.images,
        'videos': tweet.videos,
        'url': tweet.url,
    }

    with open(DATA_FILE, 'a', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False) + '\n')
        f.flush()
    return 1


def get_oldest_date():
    """Get oldest date from existing data to continue from there."""
    if not os.path.exists(DATA_FILE):
        return None
    oldest = None
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                date = datetime.fromisoformat(data['date'])
                if oldest is None or date < oldest:
                    oldest = date
            except:
                pass
    return oldest


def generate_periods():
    """Generate periods going backwards from oldest existing data."""
    oldest = get_oldest_date()

    # Determine start point (until date)
    if START_DATE:
        # Use config start_date as the starting point
        current = START_DATE
        print(f"Using config start_date: {START_DATE.strftime('%Y-%m-%d')}")
    elif oldest:
        # until is EXCLUSIVE, so we need the day AFTER oldest data
        next_day = (oldest + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        current = next_day
        print(f"Oldest existing data: {oldest.strftime('%Y-%m-%d %H:%M')}")
        print(f"Will fetch until:{current.strftime('%Y-%m-%d')} (exclusive)")
    else:
        current = datetime.now()
        print("No existing data found. Starting from today.")

    # Determine end point
    end_limit = END_DATE if END_DATE else datetime(1970, 1, 1)
    if END_DATE:
        print(f"End limit: {END_DATE.strftime('%Y-%m-%d')}")
    else:
        print("End limit: unlimited (will go back as far as possible)")

    periods = []
    while current > end_limit:
        until_date = current
        since_date = until_date - timedelta(days=PERIOD_DAYS)

        # Don't go before end_limit
        if since_date < end_limit:
            since_date = end_limit

        since_str = since_date.strftime('%Y-%m-%d')
        until_str = until_date.strftime('%Y-%m-%d')

        periods.append((since_str, until_str))
        current = since_date

    return periods


def main():
    print(f"=== Fetching posts for @{USERNAME} ===")
    print(f"Instance: {INSTANCE}")
    print()

    load_ids()
    print(f"Using ID-based deduplication. Already have {len(SEEN_IDS)} unique IDs.")

    client = NitterClient(instance=INSTANCE)

    periods = generate_periods()
    print(f"Generated {len(periods)} periods to search.")
    print("Starting historical fetch...\n")

    for i, (since, until) in enumerate(periods):
        query = f"from:{USERNAME} since:{since} until:{until}"
        print(f"[{i+1}/{len(periods)}] Searching: {query}")

        attempt = 0
        max_attempts = 5
        cumulative_fetched = 0
        cumulative_saved = 0

        while attempt < max_attempts:
            try:
                for tweet in client.search(query, limit=None, max_pages=None):
                    cumulative_fetched += 1
                    saved = save_tweet(tweet, query)
                    cumulative_saved += saved

                    if saved:
                        print(f"  + {tweet.date.strftime('%Y-%m-%d %H:%M')} - {tweet.text[:50]}...")

                    if cumulative_fetched % 20 == 0:
                        print(f"  .. fetched {cumulative_fetched}, saved {cumulative_saved} new")

                print(f"   => Done! Fetched {cumulative_fetched}, saved {cumulative_saved} new.")
                time.sleep(random.uniform(10, 20))
                break

            except Exception as e:
                attempt += 1
                error_msg = str(e)
                print(f"Error (Attempt {attempt}/{max_attempts}): {error_msg}")
                print(f"   (Progress: fetched {cumulative_fetched}, saved {cumulative_saved})")

                if "429" in error_msg:
                    wait_time = 60 * (2 ** (attempt - 1))
                    if wait_time > 900:
                        wait_time = 900
                    print(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    time.sleep(60)
        else:
            print(f"Failed period {since}~{until} after {max_attempts} attempts.")

        print()


if __name__ == "__main__":
    main()
