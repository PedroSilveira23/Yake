# from bs4 import BeautifulSoup
# from bs4 import UnicodeDammit

# try:
# 	from urllib2 import Request, urlopen
# except:
# 	from urllib2 import Request, urlopen
	
import urllib
import re
from newspaper import Article

regex_script = re.compile(r'(?is)<script.*?</script>', re.IGNORECASE)
regex_style = re.compile(r'(?is)<style.*?</style>', re.IGNORECASE)
regex_text = re.compile(r'(?is)<.+?>')

def handle_remote_page_content(page_url):
    page_url = page_url
    
    article = Article(page_url)
    article.download()
    article.parse()
    
    title = article.title
    content = article.text

    full_content = title + ". " + content
    
    return full_content