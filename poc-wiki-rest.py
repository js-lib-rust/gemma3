import requests
from urllib.parse import quote


class WikipediaAPI:
    def __init__(self, language='en'):
        self.base_url = f"https://{language}.wikipedia.org/api/rest_v1"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'WikipediaBot/1.0 (https://example.com)'
        })

    def get_page_summary(self, title):
        url = f"{self.base_url}/page/summary/{quote(title)}"
        return self._make_request(url)

    def get_page_content(self, title, page_format='html'):
        url = f"{self.base_url}/page/{page_format}/{quote(title)}"
        return self._make_request(url, parse_json=False)

    def search_pages(self, query, limit=10):
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
    wiki = WikipediaAPI()
    content = wiki.get_page_content("nightingale", page_format='html')
    print(content)


if __name__ == "__main__":
    main()
