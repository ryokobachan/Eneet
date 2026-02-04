import json
import os
import time
import random
from dataclasses import asdict
from eneet import NitterClient
from eneet.exceptions import FetchError, UserNotFoundError
# Global set to track seen IDs in memory
SEEN_IDS = set()
# Configuration
USERNAME = "yasutaketin"
DATA_FILE = f"tweets_{USERNAME}.jsonl"
PROGRESS_FILE = f"progress_{USERNAME}.json"

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {"cursor": None, "total_tweets": 0}

def save_progress(cursor, total_tweets):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"cursor": cursor, "total_tweets": total_tweets}, f)

def load_existing_ids():
    """Load IDs from the existing JSONL file to prevent duplicates on resume."""
    if not os.path.exists(DATA_FILE):
        return
    
    print(f"Loading existing IDs from {DATA_FILE}...")
    count = 0
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line: continue
                try:
                    data = json.loads(line)
                    if 'id' in data and data['id']:
                        SEEN_IDS.add(data['id'])
                        count += 1
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"⚠️ Error loading existing IDs: {e}")
    
    print(f"Loaded {count} unique IDs.")

def save_tweets(tweets, cursor):
    """Save tweets excluding duplicates and empty IDs."""
    saved_count = 0
    with open(DATA_FILE, 'a', encoding='utf-8') as f:
        for tweet in tweets:
            # Filter empty IDs
            if not tweet.id:
                continue
            
            # Filter duplicates
            if tweet.id in SEEN_IDS:
                continue
            
            # Add to seen
            SEEN_IDS.add(tweet.id)
            
            # dataclass to dict
            data = asdict(tweet)
            data['date'] = tweet.date.isoformat()
            data['fetch_cursor'] = cursor
            
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
            saved_count += 1
    return saved_count

def main():
    # Load existing IDs to prevent duplicates
    load_existing_ids()

    # client = NitterClient(instance="https://nitter.cz")
    client = NitterClient()
    
    progress = load_progress()
    cursor = progress["cursor"]
    total = progress["total_tweets"]
    
    print(f"==================================================")
    print(f" Nitter Scraper for @{USERNAME}")
    print(f"==================================================")
    print(f"Resuming from cursor: {cursor if cursor else 'START'}")
    print(f"Tweets collected (stats): {total}")
    print(f"Unique IDs loaded: {len(SEEN_IDS)}")
    print(f"--------------------------------------------------")
    
    consecutive_issues = 0
    MAX_RETRIES = 5  # Increased retries
    
    try:
        while True:
            print(f"Fetching page with cursor: {cursor[:20] + '...' if cursor else 'START'}")
            
            tweets = []
            next_cursor = None
            fetch_success = False

            try:
                # We use get_pages but only for one page at a time
                page_generator = client.get_pages(
                    USERNAME, 
                    start_cursor=cursor,
                    replies=True, 
                    retweets=True,
                    max_pages=1
                )
                try:
                    tweets, next_cursor = next(page_generator)
                    fetch_success = True
                except StopIteration:
                    # Generator yielded nothing
                    tweets, next_cursor = [], None
                
            except Exception as e:
                print(f"⚠️ Network error: {e}")
                time.sleep(30)
                # Continue main loop, will hit issues check below
            
            # Check for issues: No tweets OR No next cursor
            # User reported next_cursor should not be None unexpectedly
            has_tweets = len(tweets) > 0
            has_next = next_cursor is not None
            
            if not has_tweets or (not has_next and fetch_success):
                consecutive_issues += 1
                issue_type = "No tweets" if not has_tweets else "Next cursor is None"
                print(f"⚠️ Issue: {issue_type}. (Retry count: {consecutive_issues}/{MAX_RETRIES})")
                
                if consecutive_issues >= MAX_RETRIES:
                    print(f"❌ limit reached ({MAX_RETRIES}). Assuming end of timeline or persistent error.")
                    print(f"Last successful cursor: {cursor}")
                    break
                
                print("Waiting 10 seconds before retrying same cursor...")
                time.sleep(10)
                continue
            
            # Reset counter on success (we got tweets AND a next cursor)
            consecutive_issues = 0
            
            # Save data
            saved = save_tweets(tweets, cursor)
            total += len(tweets) # Should we count all or only saved? keeping orig logic: duplicate fetching counts as work done
            
            # Update progress
            save_progress(next_cursor, total)
            
            cursor_short = next_cursor[:20] + '...' if next_cursor else 'None'
            print(f"✅ Page fetched. Saved {saved} new (dup/empty filtered). Next: {cursor_short}")
            
            cursor = next_cursor
            time.sleep(random.uniform(2.0, 5.0))
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user.")
        save_progress(cursor, total) # Save checking point
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        save_progress(cursor, total)

if __name__ == "__main__":
    main()
