from crawleragent import search_duckduckgo, search_bing
print("DDG:", search_duckduckgo("your keyword", max_results=10))
print("Bing:", search_bing("your keyword", max_results=10))