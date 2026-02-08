# Eneet

**Nitter API Client** - Fetch tweets without Twitter API

Eneet is a Python library that allows you to fetch tweets from Twitter/X without using the official Twitter API. It works by scraping Nitter instances (privacy-respecting Twitter frontends).

## Features

- **No Twitter API required** - No API keys, no rate limits
- **CLI tool** - Easy command-line interface for fetching tweets
- **Fetch user tweets** - Get tweets from any public user
- **Search tweets** - Search for tweets by keywords
- **Filter & Exclude** - Filter tweets by keywords
- **Historical fetch** - Fetch tweets going back in time with automatic resume
- **JSONL output** - Save tweets in JSONL format for easy processing

## Installation

```bash
pip install eneet
```

Or install from source:

```bash
git clone https://github.com/ryokobachan/eneet.git
cd eneet
pip install -e .
```

## CLI Usage

After installation, the `eneet` command is available.

### Basic Usage

```bash
# Fetch all tweets from a user
eneet elonmusk --since 2024-01-01

# Fetch with custom output file
eneet elonmusk -o elon_tweets.jsonl --since 2024-01-01
```

### Search by Keywords

```bash
# Search for tweets containing keywords
eneet -q "bitcoin OR ethereum" --since 2024-01-01

# Search tweets from a specific user with keywords
eneet -q "from:elonmusk AI" --since 2024-01-01
```

### Filter and Exclude

```bash
# Only save tweets containing "AI" (filter)
eneet elonmusk --filter "AI" --since 2024-01-01

# Only save tweets containing both "AI" AND "GPU"
eneet elonmusk --filter "AI,GPU" --since 2024-01-01

# Skip tweets containing "spam" or "ad" (exclude)
eneet elonmusk --exclude "spam,ad" --since 2024-01-01

# Combine filter and exclude
eneet elonmusk --filter "AI" --exclude "spam" --since 2024-01-01
```

### Using Config File

```bash
eneet -c config.json
```

**config.json:**
```json
{
  "username": "elonmusk",
  "query": null,
  "until_date": null,
  "since_date": "2024-01-01",
  "period_days": 10,
  "instance": "https://nitter.net",
  "filters": ["AI"],
  "excludes": ["spam", "ad"]
}
```

### All CLI Options

```
eneet [-h] [-q QUERY] [-c CONFIG] [-o OUTPUT] [--until UNTIL]
      [--since SINCE] [--period PERIOD] [--instance INSTANCE]
      [-f FILTER] [-e EXCLUDE] [username]

positional arguments:
  username              Twitter username to fetch (without @)

options:
  -h, --help            show this help message and exit
  -q, --query           Search query (instead of username)
  -c, --config          Path to config.json file
  -o, --output          Output JSONL file (default: posts_{username}.jsonl)
  --until               Until date (YYYY-MM-DD) - fetch from this date backwards
  --since               Since date (YYYY-MM-DD) - stop fetching at this date
  --period              Days per search period (default: 1)
  --instance            Nitter instance URL (default: https://nitter.net)
  -f, --filter          Filter: only save tweets containing these words (comma-separated)
  -e, --exclude         Exclude: skip tweets containing these words (comma-separated)
```

## Python API

### Fetch User Tweets

```python
from eneet import NitterClient

# Initialize client
client = NitterClient()

# Get latest tweets from a user
tweets = client.get_user_tweets("elonmusk", limit=10)

for tweet in tweets:
    print(f"@{tweet.username}: {tweet.text}")
    print(f"Likes: {tweet.likes} | Retweets: {tweet.retweets}")
    print(f"Date: {tweet.date}")
    print("-" * 50)
```

### Get User Information

```python
from eneet import NitterClient

client = NitterClient()

# Get user profile
user = client.get_user("elonmusk")

print(f"Name: {user.display_name}")
print(f"Username: @{user.username}")
print(f"Bio: {user.bio}")
print(f"Followers: {user.followers:,}")
print(f"Following: {user.following:,}")
```

### Search Tweets

```python
from eneet import NitterClient

client = NitterClient()

# Search for tweets (generator)
for tweet in client.search("Python programming", limit=20):
    print(f"{tweet.text[:100]}...")
```

### Historical Fetcher (Programmatic)

```python
from eneet import HistoricalFetcher
from datetime import datetime

fetcher = HistoricalFetcher(
    username="elonmusk",
    output_file="elon_tweets.jsonl",
    since_date=datetime(2024, 1, 1),
    filters=["AI"],
    excludes=["spam"],
)
fetcher.run()
```

### Use Different Nitter Instance

```python
from eneet import NitterClient

# Use a specific Nitter instance
client = NitterClient(instance="https://nitter.poast.org")

tweets = client.get_user_tweets("github", limit=5)
```

## Output Format

Tweets are saved in JSONL format (one JSON object per line):

```json
{"id": "123456789", "date": "2024-01-15T10:30:00", "username": "elonmusk", "display_name": "Elon Musk", "text": "Tweet content here", "likes": 1000, "retweets": 100, "replies": 50, "is_retweet": false, "is_reply": false, "images": [], "videos": [], "url": "https://twitter.com/elonmusk/status/123456789"}
```

## API Reference

### `NitterClient`

Main client class for interacting with Nitter.

#### `__init__(instance=None, timeout=20)`

- `instance` (str, optional): Nitter instance URL. Default: https://nitter.net
- `timeout` (int): Request timeout in seconds. Default: 20

#### `get_user(username: str) -> User`

Fetch user information.

#### `get_user_tweets(username, limit=20, replies=True, retweets=True) -> List[Tweet]`

Fetch tweets from a user's timeline.

#### `search(query: str, limit=None, max_pages=None) -> Iterator[Tweet]`

Search for tweets (generator).

### `HistoricalFetcher`

Class for fetching historical tweets with automatic resume.

#### `__init__(...)`

- `username`: Twitter username
- `query`: Search query (alternative to username)
- `output_file`: Output JSONL file path
- `until_date`: Until date (fetch from here backwards)
- `since_date`: Since date (stop at this date)
- `period_days`: Days per search period (default: 1)
- `instance`: Nitter instance URL
- `filters`: List of words to filter (must contain ALL)
- `excludes`: List of words to exclude (skip if contains ANY)

## Important Notes

- **Rate limiting**: The library includes automatic delays to avoid rate limits.
- **Resume capability**: If interrupted, re-run the same command to continue from where it left off (uses ID-based deduplication).
- **Nitter instances** may be down or rate-limited.
- **Ethical use**: Respect Twitter's terms of service and user privacy.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit pull requests.

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/ryokobachan/eneet/issues).

---

Made with love by [@ryokobachan](https://github.com/ryokobachan)
