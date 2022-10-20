# some python file
# import textract

# from zeep import Client
# from zeep import xsd
import json
import requests
from rake import Rake

def kwporto_v1_rake(text_doc, lan='english', n_gram_max_size=4):
    rake = Rake(lan, max_words_length=n_gram_max_size)
    keywords = rake.run(text_doc)
    toReturn = []
    for (key, value) in keywords:
        toReturn.append({"Key":key,"Value":value})
    return sorted(toReturn, key=lambda x: x["Value"], reverse=True)

def kwporto_v2_alchemy(text):
    preload = 0
    top_k = 15
    verbose = 1
    classifier_type = "rcampos"
    
    url = "http://tm-websuiteapps.ipt.pt/yake/api/KeywordExtraction/alchemy"

    payload_dict = {
        "Content":text
        # "NGramMaxSize":unicode(n_gram_max_size),
        # "NumOfWordsToSelect":max_keywords
    }
    
    headers = {'content-type': 'application/json'}
    
    payload_json = json.dumps(payload_dict)
    print(payload_json)
    
    response = requests.request("POST", url, data=payload_json, headers=headers)
    print(response.text)
    
    json_response = json.loads(response.text)
    
    if("$values" in json_response.keys()):
        toReturn = []
        for item in json_response["$values"]:
            toReturn.append({"Key":item["Key"],"Value":item["Value"]})
        return sorted(toReturn, key=lambda x: x["Value"], reverse=True)

    
    return json_response 

# def kwporto_v2(title,text,language="en"):
def kwporto_v2(title,text,n_gram_max_size=4,max_keywords=15,language="en"):
    preload = 0
    top_k = 15
    verbose = 1
    classifier_type = "rcampos"
    
    url = "http://tm-websuiteapps.ipt.pt/yake/api/KeywordExtraction/yake"

    payload_dict = {
        "Title":title,
        "Content":text,
        "NGramMaxSize":n_gram_max_size,
        "NumOfWordsToSelect":max_keywords        
    }
    
    headers = {'content-type': 'application/json'}
    
    payload_json = json.dumps(payload_dict)
    print(payload_json)
    
    response = requests.request("POST", url, data=payload_json, headers=headers)
    print(response.text)
    
    json_response = json.loads(response.text)
    # top_ngrams = sorted(json_response, key = lambda x: x[1], reverse=True)[:top_k]
    if("$values" in json_response.keys()):
        toReturn = []
        for item in json_response["$values"]:
            toReturn.append({"Key":item["Key"],"Value":item["Value"]})
        return sorted(toReturn, key=lambda x: x["Value"])
    return json_response 

# def kwporto_v1(title,text,language="en"):
#     # wsdl = 'http://tm-websuiteapps.ipt.pt/KeywordsExtractor_V2_API/ws.asmx?wsdl'
#     client = Client(wsdl)
#
#     preload = 0
#     top_k = 15
#     verbose = 1
#     classifier_type = "rcampos"
#
#     """"
#     SoapMethod
#         <GetJSON xmlns="http://tempuri.org/">
#           <language>string</language>
#           <title>string</title>
#           <txt>string</txt>
#         </GetJSON>
#     """
#
#     response = client.service.GetJSON(language='en',title=title,txt=unicode(text))
#     json_response = json.loads(response)
#
#     top_ngrams = sorted(json_response.items(), key = lambda x: x[1], reverse=True)[:top_k]
#
#     # suggested_keywords = []
# #
# #     for ngram in top_ngrams:
# #         suggested_keywords.append(ngram[0])
#
#     return top_ngrams
