# Easiest solution
import wikipediaapi

wiki = wikipediaapi.Wikipedia(
    user_agent='MyResearchBot/1.0',
    language='en'
)


def get_clean_article(title):
    page = wiki.page(title)
    return {
        'title': page.title,
        'summary': page.summary,
        'full_text': page.text,
        'sections': [s.title for s in page.sections],
        'url': page.fullurl
    }


article = get_clean_article("nile")
print(article['summary'])
print('----------------------------')
print(article['full_text'])
