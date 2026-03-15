"""CLI for fetching historical tweets."""

import argparse
import json
import os
import sys
import time
import random
from datetime import datetime
from typing import List, Optional

from .client import NitterClient


def _err(msg: str):
    """Print error message to stderr."""
    print(msg, file=sys.stderr)


class HistoricalFetcher:
    """Fetches tweets and saves to JSONL or streams to stdout."""

    def __init__(
        self,
        username: str = None,
        query: str = None,
        output_file: str = None,
        until_date: datetime = None,
        since_date: datetime = None,
        instance: str = "https://nitter.net",
        filters: List[str] = None,
        excludes: List[str] = None,
        tweet_limit: Optional[int] = None,
        no_retweets: bool = False,
        no_replies: bool = False,
        min_likes: Optional[int] = None,
    ):
        self.username = username
        self.query = query
        self.output_file = output_file  # None means stdout mode
        self.until_date = until_date
        self.since_date = since_date
        self.instance = instance
        self.filters = filters or []
        self.excludes = excludes or []
        self.seen_ids = set()
        # tweet_limit: None = 1 page (default), -1 = unlimited, N > 0 = up to N tweets
        self.tweet_limit = tweet_limit
        self.no_retweets = no_retweets
        self.no_replies = no_replies
        self.min_likes = min_likes

    @staticmethod
    def default_output_file(username: str = None, query: str = None) -> str:
        if username:
            return f"posts_{username}.jsonl"
        elif query:
            safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
            return f"search_{safe_query}.jsonl"
        return "posts.jsonl"

    def load_existing_ids(self):
        """Load existing IDs from output file to avoid duplicates."""
        if self.output_file is None or not os.path.exists(self.output_file):
            return
        with open(self.output_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    if data.get('id'):
                        self.seen_ids.add(data['id'])
                except:
                    pass

    def should_save(self, tweet) -> bool:
        """Check if tweet passes all filter rules."""
        if self.no_retweets and tweet.is_retweet:
            return False
        if self.no_replies and tweet.is_reply:
            return False
        if self.min_likes is not None and tweet.likes < self.min_likes:
            return False
        text_lower = tweet.text.lower()
        for f in self.filters:
            if f.lower() not in text_lower:
                return False
        for e in self.excludes:
            if e.lower() in text_lower:
                return False
        return True

    def emit_tweet(self, tweet) -> int:
        """Output or save a single tweet. Returns 1 if emitted, 0 if skipped."""
        if not tweet.id or tweet.id in self.seen_ids:
            return 0
        if not self.should_save(tweet):
            return 0

        self.seen_ids.add(tweet.id)

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

        if self.output_file is None:
            # Stdout mode: stream immediately
            print(json.dumps(data, ensure_ascii=False), flush=True)
        else:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(data, ensure_ascii=False) + '\n')
                f.flush()
        return 1

    def build_query(self) -> str:
        """Build the full search query with optional date filters."""
        if self.username:
            base = f"from:{self.username}"
        elif self.query:
            base = self.query
        else:
            raise ValueError("Either username or query is required")

        parts = [base]
        if self.since_date:
            parts.append(f"since:{self.since_date.strftime('%Y-%m-%d')}")
        if self.until_date:
            parts.append(f"until:{self.until_date.strftime('%Y-%m-%d')}")
        return " ".join(parts)

    def run(self):
        """Run the fetch."""
        self.load_existing_ids()
        client = NitterClient(instance=self.instance)

        query = self.build_query()
        search_url = f"{self.instance}/search?f=tweets&q={query.replace(' ', '%20')}"

        # Determine limits
        if self.tweet_limit is None:
            fetch_limit, fetch_max_pages = None, 1      # default: 1 page
        elif self.tweet_limit == -1:
            fetch_limit, fetch_max_pages = None, None   # unlimited via cursor
        else:
            fetch_limit, fetch_max_pages = self.tweet_limit, None  # up to N tweets

        attempt = 0
        max_attempts = 5

        while attempt < max_attempts:
            try:
                for tweet in client.search(query, limit=fetch_limit, max_pages=fetch_max_pages):
                    self.emit_tweet(tweet)
                break

            except Exception as e:
                attempt += 1
                error_msg = str(e)
                if "429" in error_msg:
                    wait_time = min(60 * (2 ** (attempt - 1)), 900)
                    _err(f"ERROR: 429 rate limited. Waiting {wait_time}s... ({attempt}/{max_attempts}) URL: {search_url}")
                    client.reset_session()
                    time.sleep(wait_time)
                else:
                    _err(f"ERROR: {error_msg} ({attempt}/{max_attempts}) URL: {search_url}")
                    time.sleep(60)
        else:
            _err(f"ERROR: Failed after {max_attempts} attempts. URL: {search_url}")


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime."""
    if not date_str:
        return None
    return datetime.strptime(date_str, '%Y-%m-%d')


def parse_list(value: str) -> List[str]:
    """Parse comma-separated string to list."""
    if not value:
        return []
    return [v.strip() for v in value.split(',') if v.strip()]


def main():
    parser = argparse.ArgumentParser(
        description="Fetch historical tweets via Nitter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch 1 page (default)
  eneet elonmusk --since 2024-01-01

  # Fetch up to 50 tweets via cursor pagination
  eneet elonmusk --since 2024-01-01 -n 50

  # Fetch all tweets (unlimited cursor pagination)
  eneet elonmusk --since 2024-01-01 -n -1

  # Search with keyword query
  eneet -q "from:yasutaketin NBIS" --since 2026-01-01 -n -1

  # Save to default filename (posts_elonmusk.jsonl)
  eneet elonmusk --since 2024-01-01 -o

  # Save to specific file
  eneet elonmusk --since 2024-01-01 -o myfile.jsonl

  # Pipe stdout to another tool
  eneet elonmusk --since 2024-01-01 | jq '.text'

  # Use config file
  eneet -c config.json
        """
    )
    parser.add_argument(
        "username",
        nargs="?",
        help="Twitter username to fetch (without @)",
    )
    parser.add_argument(
        "-q", "--query",
        help="Search query (instead of username)",
    )
    parser.add_argument(
        "-c", "--config",
        help="Path to config.json file",
    )
    parser.add_argument(
        "-o", "--output",
        nargs="?",
        const="",
        default=None,
        help="Output JSONL file. Use -o alone for default filename, -o FILE for specific file. Without -o, outputs JSONL to stdout.",
    )
    parser.add_argument(
        "--until",
        help="Until date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--since",
        help="Since date (YYYY-MM-DD)",
    )
    parser.add_argument(
        "--instance",
        default="https://nitter.net",
        help="Nitter instance URL (default: https://nitter.net)",
    )
    parser.add_argument(
        "-n", "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Max tweets to fetch. Default: 1 page (1 request). -1 = unlimited.",
    )
    parser.add_argument(
        "-f", "--filter",
        help="Filter: only save tweets containing these words (comma-separated)",
    )
    parser.add_argument(
        "-e", "--exclude",
        help="Exclude: skip tweets containing these words (comma-separated)",
    )
    parser.add_argument(
        "--no-retweets",
        action="store_true",
        help="Exclude retweets",
    )
    parser.add_argument(
        "--no-replies",
        action="store_true",
        help="Exclude replies",
    )
    parser.add_argument(
        "--min-likes",
        type=int,
        default=None,
        metavar="N",
        help="Only include tweets with at least N likes",
    )

    args = parser.parse_args()

    # Load from config if provided
    if args.config:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = json.load(f)
        username = config.get('username')
        query = config.get('query')
        until_date = parse_date(config.get('until_date'))
        since_date = parse_date(config.get('since_date'))
        instance = config.get('instance', 'https://nitter.net')
        filters = config.get('filters', [])
        excludes = config.get('excludes', [])
        config_output = config.get('output')
        raw_output = args.output if args.output is not None else (config_output or None)
        tweet_limit = args.limit if args.limit is not None else config.get('tweet_limit')
        no_retweets = args.no_retweets or config.get('no_retweets', False)
        no_replies = args.no_replies or config.get('no_replies', False)
        min_likes = args.min_likes if args.min_likes is not None else config.get('min_likes')
    else:
        username = args.username
        query = args.query
        until_date = parse_date(args.until)
        since_date = parse_date(args.since)
        instance = args.instance
        filters = parse_list(args.filter)
        excludes = parse_list(args.exclude)
        raw_output = args.output
        tweet_limit = args.limit
        no_retweets = args.no_retweets
        no_replies = args.no_replies
        min_likes = args.min_likes

    if not username and not query:
        parser.error("Either username, --query, or --config is required")

    # Resolve output_file:
    #   raw_output is None  -> no -o flag -> stdout mode (output_file = None)
    #   raw_output is ""    -> -o without filename -> use default filename
    #   raw_output is str   -> -o FILE -> use that filename
    if raw_output is None:
        output_file = None
    elif raw_output == "":
        output_file = HistoricalFetcher.default_output_file(username, query)
    else:
        output_file = raw_output

    fetcher = HistoricalFetcher(
        username=username,
        query=query,
        output_file=output_file,
        until_date=until_date,
        since_date=since_date,
        instance=instance,
        filters=filters,
        excludes=excludes,
        tweet_limit=tweet_limit,
        no_retweets=no_retweets,
        no_replies=no_replies,
        min_likes=min_likes,
    )
    fetcher.run()


if __name__ == "__main__":
    main()
