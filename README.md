# Eneet

**Nitter API Client** - Fetch tweets without Twitter API

Eneet is a Python library that allows you to fetch tweets from Twitter/X without using the official Twitter API. It works by scraping Nitter instances (privacy-respecting Twitter frontends).

## 🚀 Features

- ✅ **No Twitter API required** - No API keys, no rate limits
- ✅ **Fetch user tweets** - Get tweets from any public user
- ✅ **User information** - Retrieve user profiles and stats
- ✅ **Search tweets** - Search for tweets by keywords
- ✅ **Filter options** - Include/exclude replies and retweets
- ✅ **Media support** - Access images and videos from tweets
- ✅ **Simple API** - Easy-to-use Pythonic interface

## 📦 Installation

```bash
pip install eneet
```

## 🔧 Quick Start

### Fetch User Tweets

```python
from eneet import NitterClient

# Initialize client
client = NitterClient()

# Get latest tweets from a user
tweets = client.get_user_tweets("elonmusk", limit=10)

for tweet in tweets:
    print(f"@{tweet.username}: {tweet.text}")
    print(f"❤️ {tweet.likes} 🔁 {tweet.retweets} 💬 {tweet.replies}")
    print(f"📅 {tweet.date}")
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
print(f"Tweets: {user.tweets_count:,}")
```

### Search Tweets

```python
from eneet import NitterClient

client = NitterClient()

# Search for tweets
tweets = client.search_tweets("Python programming", limit=20)

for tweet in tweets:
    print(f"{tweet.text[:100]}...")
```

### Filter Tweets

```python
from eneet import NitterClient

client = NitterClient()

# Get tweets without replies and retweets
tweets = client.get_user_tweets(
    "elonmusk",
    limit=20,
    replies=False,  # Exclude replies
    retweets=False  # Exclude retweets
)
```

### Access Tweet Media

```python
from eneet import NitterClient

client = NitterClient()

tweets = client.get_user_tweets("NASA", limit=10)

for tweet in tweets:
    if tweet.has_media:
        print(f"Tweet: {tweet.text}")
        if tweet.images:
            print(f"Images: {len(tweet.images)}")
            for img_url in tweet.images:
                print(f"  - {img_url}")
        if tweet.videos:
            print(f"Videos: {len(tweet.videos)}")
```

### Use Different Nitter Instance

```python
from eneet import NitterClient

# Use a specific Nitter instance
client = NitterClient(instance="https://nitter.poast.org")

tweets = client.get_user_tweets("github", limit=5)
```

## 📚 API Reference

### `NitterClient`

Main client class for interacting with Nitter.

#### `__init__(instance=None, timeout=10)`

- `instance` (str, optional): Nitter instance URL. Default: auto-select
- `timeout` (int): Request timeout in seconds. Default: 10

#### `get_user(username: str) -> User`

Fetch user information.

- `username`: Twitter username (without @)
- Returns: `User` object
- Raises: `UserNotFoundError` if user doesn't exist

#### `get_user_tweets(username: str, limit=20, replies=True, retweets=True) -> List[Tweet]`

Fetch tweets from a user's timeline.

- `username`: Twitter username (without @)
- `limit`: Maximum number of tweets to fetch (default: 20)
- `replies`: Include replies (default: True)
- `retweets`: Include retweets (default: True)
- Returns: List of `Tweet` objects

#### `search_tweets(query: str, limit=20) -> List[Tweet]`

Search for tweets by keyword.

- `query`: Search query
- `limit`: Maximum number of tweets (default: 20)
- Returns: List of `Tweet` objects

### Data Models

#### `User`

- `username` (str): Twitter username
- `display_name` (str): Display name
- `bio` (str, optional): User bio
- `followers` (int, optional): Follower count
- `following` (int, optional): Following count
- `tweets_count` (int, optional): Total tweets
- `verified` (bool): Verification status
- `avatar_url` (str, optional): Profile picture URL

#### `Tweet`

- `id` (str): Tweet ID
- `username` (str): Author username
- `display_name` (str): Author display name
- `text` (str): Tweet text
- `date` (datetime): Tweet timestamp
- `likes` (int): Like count
- `retweets` (int): Retweet count
- `replies` (int): Reply count
- `is_retweet` (bool): Is this a retweet?
- `is_reply` (bool): Is this a reply?
- `images` (List[str]): Image URLs
- `videos` (List[str]): Video URLs
- `url` (str, optional): Tweet URL
- `has_media` (property): Check if tweet has media

## ⚠️ Important Notes

- **Nitter instances** may be down or rate-limited. The library automatically tries default instances.
- **Scraping limitations**: Eneet relies on Nitter's HTML structure, which may change over time.
- **Ethical use**: Respect Twitter's terms of service and user privacy.
- **No authentication**: Only public tweets can be fetched.

## 🛠️ Development

```bash
# Clone repository
git clone https://github.com/ryokobachan/eneet.git
cd eneet

# Install in development mode
pip install -e .

# Run tests
pytest tests/
```

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests.

## 📞 Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/ryokobachan/eneet/issues).

## 🔗 Related Projects

- [Nitter](https://github.com/zedeus/nitter) - Privacy-focused Twitter frontend
- [Fintics](https://github.com/ryokobachan/fintics) - Trading bot framework

---

Made with ❤️ by [@ryokobachan](https://github.com/ryokobachan)
