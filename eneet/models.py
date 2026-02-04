"""Data models for Eneet."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """Represents a Twitter/Nitter user."""
    
    username: str
    display_name: str
    bio: Optional[str] = None
    followers: Optional[int] = None
    following: Optional[int] = None
    tweets_count: Optional[int] = None
    verified: bool = False
    avatar_url: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"User(username='{self.username}', display_name='{self.display_name}')"


@dataclass
class Tweet:
    """Represents a single tweet from Nitter."""
    
    id: str
    username: str
    display_name: str
    text: str
    date: datetime
    likes: int = 0
    retweets: int = 0
    replies: int = 0
    is_retweet: bool = False
    is_reply: bool = False
    images: List[str] = None
    videos: List[str] = None
    url: Optional[str] = None
    
    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.videos is None:
            self.videos = []
    
    def __repr__(self) -> str:
        return f"Tweet(id='{self.id}', username='{self.username}', text='{self.text[:50]}...')"
    
    @property
    def has_media(self) -> bool:
        """Check if tweet has any media (images or videos)."""
        return bool(self.images or self.videos)
