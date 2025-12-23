import requests
import json
from urllib.parse import quote
import html2text

class WikipediaAPI:
    def __init__(self, language='en'):
        self.base_url = f"https://{language}.wikipedia.org/api/rest_v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaBot/1.0 (https://example.com)'
        })

    def get_page_summary(self, title):
        """Get page summary"""
        url = f"{self.base_url}/page/summary/{quote(title)}"
        return self._make_request(url)

    def get_page_content(self, title, format='html'):
        """Get full page content in specified format"""
        url = f"{self.base_url}/page/{format}/{quote(title)}"
        return self._make_request(url, parse_json=False)

    def search_pages(self, query, limit=10):
        """Search for pages"""
        url = f"{self.base_url}/page/search/{quote(query)}"
        params = {'limit': limit}
        return self._make_request(url, params=params)

    def _make_request(self, url, params=None, parse_json=True):
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json() if parse_json else response.text
        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return None


def main():
    # Create Wikipedia API instance
    wiki = WikipediaAPI()

    # Get lion page summary
    # print("=== LION PAGE SUMMARY ===")
    # lion_summary = wiki.get_page_summary("Lion")

    # if lion_summary:
    #     print(f"Title: {lion_summary.get('title')}")
    #     print(f"Description: {lion_summary.get('description', 'N/A')}")
    #     print(f"Extract: {lion_summary.get('extract', 'N/A')[:300]}...")
    #     print(f"Page URL: {lion_summary.get('content_urls', {}).get('desktop', {}).get('page', 'N/A')}")

    content = wiki.get_page_content("nightingale", format="json")
    print(content)

    h = html2text.HTML2Text()
    h.ignore_links = True
    markdown = h.handle(content)
    # print(markdown)

    # Search for related pages
    # print("\n=== RELATED PAGES ===")
    # search_results = wiki.search_pages("big cats", limit=5)
    #
    # if search_results and 'pages' in search_results:
    #     for page in search_results['pages'][:3]:
    #         print(f"- {page.get('title')}: {page.get('description', 'No description')}")


if __name__ == "__main__":
    main()
