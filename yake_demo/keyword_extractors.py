# some python file
# import textract
# # # # # # # # #
# from zeep import Client
# from zeep import xsd

import json
import requests
from demo.rake import Rake
from zeep import Client
from zeep import xsd
from langdetect import detect
from stop_words import get_stop_words
from stop_words import StopWordError

import yake
from yake.highlight import TextHighlighter

from watson_developer_cloud import AlchemyLanguageV1

class RakeKeywordExtrator():

    def __init__(self):
        self.nameApproach = "Rake"

    def execute(self,content, language="english", n_gram_max_size=4):
        self.rake_service = Rake(language, max_words_length=n_gram_max_size)
        suggested_keywords = self.rake_service.run(content)
        toReturn = []

        for (key, value) in suggested_keywords:
            toReturn.append({"Key":key,"Value":value})
        return sorted(toReturn, key=lambda x: x["Value"], reverse=True)

class AlchemyKeywordExtrator():
    def __init__(self):
        self.key='<>' # Chave UNICA
        self.nameApproach = "alchemy"
        self.alchemy_language = AlchemyLanguageV1(api_key=self.key)
    def execute(self,content):
        try:
            result = self.alchemy_language.keywords(text=content)
            toReturn = [ {"Key":r['text'].lower(),"Value":float(r['relevance'])} for r in result['keywords'] ]
            return sorted(toReturn, key=lambda x: x["Value"], reverse=True)
        except:
            print(content)
            return []

class YakeKeywordExtrator_wcf():
    def __init__(self):
        self.nameApproach = "yake"

    def execute(self, text, language="en-US", n_gram_max_size=4, top=30):

        if("-" in language):
            language = language.split("-")[0]
        
        print("language", language)
        
        custom_kwextractor = yake.KeywordExtractor(lan=language, n=n_gram_max_size, dedupLim=0.9, dedupFunc='seqm', windowsSize=1, top=top)

        keywords = custom_kwextractor.extract_keywords(text)

        toReturn = []

        for key in keywords:
            toReturn.append({"Key":key[0],"Value":float(key[1])})

        return sorted(toReturn, key=lambda x: x["Value"], reverse=False)
