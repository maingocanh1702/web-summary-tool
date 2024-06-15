from urllib.parse import urlparse, urlunparse

def remove_query_string(url):
    parsed_url = urlparse(url)
    # Create a new URL without the query string
    url_without_query = urlunparse(parsed_url._replace(query=""))
    return url_without_query

def get_domain_name(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

def remove_markdown_code(text):
    start_index = text.find("```html")
    if start_index != -1:
        end_index = text.rfind("```")
        text = text[start_index + 7:end_index]
    return text

# Example
# url = "http://example.com/article?param1=value1&param2=value2"
# clean_url = get_domain_name(url)
# print(clean_url)  # Output: http://example.com/article