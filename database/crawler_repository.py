from pymongo import MongoClient
import utils.utils as util
from datetime import datetime


class CrawledArticle:
    def __init__(self, url, title, description, publish_date, source, content, summary, keypoints, keywords):
        self.url = url
        self.title = title
        self.description = description
        self.publish_date = publish_date
        self.source = source
        self.content = content
        self.summary = summary
        self.keypoints = keypoints
        self.keywords = keywords
        self.last_crawled = datetime.now()

    def to_dict(self):
        return {
            "url": self.url,
            "title": self.title,
            "description": self.description,
            "publish_date": self.publish_date,
            "source": self.source,
            "content": self.content,
            "summary": self.summary,
            "keypoints": self.keypoints,
            "keywords": self.keywords,
            "last_crawled": self.last_crawled
        }


class CrawledUrl:
    def __init__(self, url):
        self.url = url
        self.last_crawled = datetime.now()

    def to_dict(self):
        return {
            "url": self.url,
            "last_crawled": self.last_crawled
        }


class WebCrawlerRepository:
    def __init__(self, connection_string):
        self.client = MongoClient(connection_string)
        self.db = self.client.web_crawler
        self.articles_collection = self.db.articles
        self.crawled_urls_collection = self.db.crawled_urls

    # Save new article or update article into database
    def save_article(self, article):
        self.articles_collection.update_one({"url": article.url}, {"$set": article.to_dict()}, upsert=True)
        crawled_url = CrawledUrl(article.url)
        self.crawled_urls_collection.update_one({"url": crawled_url.url}, {"$set": crawled_url.to_dict()}, upsert=True)

    # Get article if existed
    def get_article(self, url):
        article_dict = self.articles_collection.find_one({"url": url})
        if article_dict is not None:
            article = CrawledArticle(url=article_dict["url"], title=article_dict["title"], description=article_dict["description"],
                                 publish_date=article_dict["publish_date"], source=article_dict["source"], content=article_dict["content"],
                                 summary=article_dict["summary"], keypoints=article_dict["keypoints"], keywords=article_dict["keywords"])
            return article
        return None

    # Check url was crawled or not
    def check_url(self, url):
        criteria = {"url": url}
        n_check = self.crawled_urls_collection.count_documents(criteria)
        if n_check == 0:
            return True
        return False

    # Check article has summary part or not
    def has_summary(self, url):
        criteria = {"url": url,"summary":""}
        n_check = self.crawled_urls_collection.count_documents(criteria)
        if n_check == 1:
            return True
        return False

    # Check article has keypoints part or not
    def has_keypoints(self, url):
        criteria = {"url": url,"keypoints":""}
        n_check = self.crawled_urls_collection.count_documents(criteria)
        if n_check == 1:
            return True
        return False

# Testing Code
# test_url = "https://vuiapp.vn?xinchao=1"
#
# test_url = util.remove_query_string(test_url)
# article = Article(url=test_url, title="Tieu de", description="Mo ta", published_date=datetime.now(), source="Vnexpress", content="Noi dung bai viet", summary="Noi dung tom tat cua bai viet", keywords=["kw1","kw2"])
# repository = WebCrawlerRepository()
#
# repository.save_article(article)
# print(repository.check_url(test_url))
