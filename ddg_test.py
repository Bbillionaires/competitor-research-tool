from duckduckgo_search import DDGS

with DDGS() as ddgs:
    results = ddgs.text("immigration lawyers Ventura CA", max_results=5)
    for result in results:
        print(result['title'], "-", result['href'])
