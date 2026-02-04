"""Example usage of Eneet library."""

from eneet import NitterClient


def main():
    # Initialize client
    client = NitterClient()
    
    print("=" * 60)
    print("Eneet - Nitter API Client Example")
    print("=" * 60)
    
    # Example 1: Get user information
    print("\n📊 Example 1: Fetch User Information")
    print("-" * 60)
    try:
        user = client.get_user("elonmusk")
        print(f"Username: @{user.username}")
        print(f"Display Name: {user.display_name}")
        print(f"Bio: {user.bio[:100]}..." if user.bio else "No bio")
        print(f"Followers: {user.followers:,}")
        print(f"Following: {user.following:,}")
        print(f"Tweets: {user.tweets_count:,}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Get user tweets
    print("\n🐦 Example 2: Fetch Recent Tweets")
    print("-" * 60)
    try:
        tweets = client.get_user_tweets("github", limit=5)
        for i, tweet in enumerate(tweets, 1):
            print(f"\n[{i}] @{tweet.username} ({tweet.date.strftime('%Y-%m-%d %H:%M')})")
            print(f"    {tweet.text[:100]}...")
            print(f"    ❤️ {tweet.likes:,}  🔁 {tweet.retweets:,}  💬 {tweet.replies:,}")
            if tweet.has_media:
                print(f"    📷 Media: {len(tweet.images)} images, {len(tweet.videos)} videos")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Filter tweets
    print("\n🔍 Example 3: Filter Tweets (No Retweets/Replies)")
    print("-" * 60)
    try:
        tweets = client.get_user_tweets(
            "NASA",
            limit=5,
            replies=False,
            retweets=False
        )
        for i, tweet in enumerate(tweets, 1):
            print(f"\n[{i}] {tweet.text[:80]}...")
            print(f"    Posted: {tweet.date.strftime('%Y-%m-%d %H:%M')}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Search tweets
    print("\n🔎 Example 4: Search Tweets")
    print("-" * 60)
    try:
        tweets = client.search_tweets("Python programming", limit=3)
        for i, tweet in enumerate(tweets, 1):
            print(f"\n[{i}] @{tweet.username}")
            print(f"    {tweet.text[:100]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
