import json
import os
import time
import random
from dataclasses import asdict
from eneet import NitterClient
from eneet.exceptions import FetchError, UserNotFoundError

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

def save_tweets(tweets, cursor):
    with open(DATA_FILE, 'a', encoding='utf-8') as f:
        for tweet in tweets:
            # dataclass to dict
            data = asdict(tweet)
            # convert datetime to string for json serialization
            data['date'] = tweet.date.isoformat()
            # Add cursor info for debugging/verification
            data['fetch_cursor'] = cursor
            # write as newline-delimited json
            f.write(json.dumps(data, ensure_ascii=False) + '\n')

def main():
    # Use specific instance if needed, or let client auto-select
    # client = NitterClient(instance="https://nitter.cz")
    client = NitterClient()
    
    progress = load_progress()
    cursor = progress["cursor"]
    total = progress["total_tweets"]
    
    print(f"==================================================")
    print(f" Nitter Scraper for @{USERNAME}")
    print(f"==================================================")
    print(f"Resuming from cursor: {cursor if cursor else 'START'}")
    print(f"Tweets collected so far: {total}")
    print(f"Data file: {DATA_FILE}")
    print(f"Progress file: {PROGRESS_FILE}")
    print(f"--------------------------------------------------")
    
    consecutive_empty_pages = 0
    MAX_RETRIES = 3
    
    try:
        while True:
            # Manual loop to handle retries and cursor updates explicitly
            print(f"Fetching page with cursor: {cursor[:20] + '...' if cursor else 'START'}")
            
            try:
                # We use get_pages but only for one page at a time to handle retries
                page_generator = client.get_pages(
                    USERNAME, 
                    start_cursor=cursor,
                    replies=True, 
                    retweets=True,
                    max_pages=1
                )
                
                # Extract the single page result
                try:
                    tweets, next_cursor = next(page_generator)
                except StopIteration:
                    # Generator yielded nothing? Should not happen usually
                    tweets, next_cursor = [], None
                
            except Exception as e:
                print(f"⚠️ Network error: {e}")
                print("Waiting 30 seconds before retry...")
                time.sleep(30)
                continue

            if not tweets:
                consecutive_empty_pages += 1
                print(f"⚠️ No tweets found on this page. (Empty count: {consecutive_empty_pages}/{MAX_RETRIES})")
                
                if consecutive_empty_pages >= MAX_RETRIES:
                    print("❌ Too many empty pages. Assuming end of timeline or rate limit.")
                    print(f"Last cursor was: {cursor}")
                    break
                
                print("Waiting 10 seconds before retrying same cursor...")
                time.sleep(10)
                # Don't update cursor, retry loop with same cursor
                continue
            
            # Reset empty counter on success
            consecutive_empty_pages = 0
            
            # Save data with cursor info
            save_tweets(tweets, cursor)
            total += len(tweets)
            
            # Update progress
            save_progress(next_cursor, total)
            
            # Log progress
            cursor_short = next_cursor[:20] + '...' if next_cursor else 'None'
            print(f"✅ Fetched {len(tweets)} tweets. Total: {total}. Next: {cursor_short}")
            
            if not next_cursor:
                print("\n🎉 End of timeline reached (next_cursor is None)!")
                break
            
            # Update cursor for next iteration
            cursor = next_cursor
            
            # Sleep is already handled inside get_pages, but since we call it 1-by-1,
            # we should add our own sleep here to be safe
            time.sleep(random.uniform(2.0, 5.0))
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopped by user.")
        print("Progress has been saved. Run script again to resume exactly where you left off.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Progress has been saved. Run script again to resume.")

if __name__ == "__main__":
    main()
