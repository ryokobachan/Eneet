import requests
from bs4 import BeautifulSoup

url = "https://nitter.net/elonmusk"
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Priority': 'u=0, i',
    'Sec-Ch-Ua': '"Chromium";v="144", "Not(A:Brand";v="24", "Google Chrome";v="144"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"macOS"',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0',
}
response = requests.get(url, headers=headers)

print(f"Status: {response.status_code}")
print(f"Content length: {len(response.text)}")
print(f"\nFirst 2000 characters:")
print("=" * 80)
print(response.text[:2000])
print("=" * 80)

soup = BeautifulSoup(response.content, 'html.parser')

# Check main elements
print("\n\nChecking main elements:")
print(f"Profile card: {soup.find('div', class_='profile-card')}")
print(f"Timeline items: {len(soup.find_all('div', class_='timeline-item'))}")
print(f"All divs: {len(soup.find_all('div'))}")

# Print all class names
print("\n\nAll unique class names found:")
classes = set()
for elem in soup.find_all(class_=True):
    if isinstance(elem.get('class'), list):
        classes.update(elem.get('class'))
    else:
        classes.add(elem.get('class'))
        
for cls in sorted(classes)[:30]:
    print(f"  - {cls}")
