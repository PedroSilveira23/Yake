from flask import Flask, jsonify, request
from flask import Blueprint, render_template, flash, redirect, url_for
from flask.views import MethodView
from flasgger import Swagger
from flasgger.utils import swag_from

# from demo import frontend
from demo.keyword_extractors import *
from demo.frontend import handle_keyword_extractor_request
from langdetect import detect
from demo.languages import isoLangs

from demo.utils import *
from demo.remote_url import *

from yake.highlight import TextHighlighter

import distutils
from distutils import util

api_frontend = Blueprint('api_frontend', __name__)

# TODO:passar isso para uma classe utils
def handle_yake(content, n_gram_max_size, number_of_keywords, highlight= False):
    # extract keywords
    
    full_content = content
    _detected_language = detect(full_content)
    undefined = False    
    
    if _detected_language in isoLangs.keys():
        # language_name = iso_languages[_detected_language]
        language_name = isoLangs[_detected_language]["name"].lower()
    else:
        undefined = True
        language_name = "english"
    
    detected_language = _detected_language

    yake = YakeKeywordExtrator_wcf()
    kwport_keywords = yake.execute(text=content, language=detected_language, n_gram_max_size=n_gram_max_size, top=30)

    result = []
    for item in kwport_keywords[:number_of_keywords]:
        item["Key"]
        item["Value"]
        
        result.append({
            "ngram":item["Key"],
            "score":item["Value"]
        })
    
    if undefined:
        language_name = detected_language + " is not supported"

        
    model = {
      "language":language_name,
      "keywords":result
      }

    if(highlight):
      th = TextHighlighter(max_ngram_size = int(n_gram_max_size))

      keywords_ngrams = [x["Key"] for x in  kwport_keywords]
      highlighted_text = th.highlight(content, keywords_ngrams)
      model["highlighted_text"] = highlighted_text

    return model
    
@api_frontend.route("/yake/v2/extract_keywords",methods=['POST'])
def handle_keyword_extraction():
    """
    extract keywords from input text
    ---
    
    tags:
    - available methods
    parameters:      
      - name: content
        in: formData
        type: string
        description: content    
        required: true
      - name: max_ngram_size
        in: query
        type: integer
        description: max size of ngram
        required: true
        default: 3    
      - name: number_of_keywords
        in: query
        type: integer
        description: number of keywords to return
        required: true
        default: 20
      - in: query
        name: highlight
        type: boolean
        default: 20
        required: false
        description: If true, the endpoint returns input text highlighting detected keywords.
      
    
    responses:
      200:
        description: Extract keywords from input text
        schema:
          id: result
          properties:
            language:
              type: string
              description: detected language
            keywords:
              type: array
              items:
                schema:
                  id: SubItem
                  properties:
                    ngram:
                      type: string
                      description: ngram
                    score:
                      type: integer
                      description: relevance score

    """
    
    print(request.form)
    
    content = request.form["content"]
    
    max_ngram_size = int(request.args["max_ngram_size"])
    number_of_keywords = int(request.args["number_of_keywords"])
    highlight = False

    if("highlight" in request.args):
      highlight = distutils.util.strtobool(request.args["highlight"].title())
      
    result_model = handle_yake(content,max_ngram_size, number_of_keywords, highlight)

    return jsonify(result_model)
        
@api_frontend.route("/yake/v2/extract_keywords_by_url",methods=['GET'])
def extract_keywords_by_url():
    """
    extract keywords from web page url
    ---

    tags:
    - available methods
    parameters:      
      - name: url
        in: query
        type: string
        description: web page url from where we will extract the content and keywords
        required: true
      - name: max_ngram_size
        in: query
        type: integer
        description: max size of ngram
        required: true
        default: 3
      - name: number_of_keywords
        in: query
        type: integer
        description: number of keywords to return
        required: true
        default: 20
      - in: query
        name: highlight
        type: boolean
        default: 20
        required: false
        description: If true, the endpoint returns input text highlighting detected keywords.
      
    responses:
      200:
        description: Extract keywords from web page url
        schema:
          id: result
          properties:
            language:
              type: string
              description: detected language
            keywords:
              type: array
              items:
                schema:
                  id: SubItem
                  properties:
                    ngram:
                      type: string
                      description: ngram
                    score:
                      type: integer
                      description: relevance score

    """
    
    page_url = request.args["url"]
    
    content = handle_remote_page_content(page_url)
    
    max_ngram_size = int(request.args["max_ngram_size"])
    number_of_keywords = int(request.args["number_of_keywords"])
    
    
    highlight = False

    if("highlight" in request.args):
      highlight = distutils.util.strtobool(request.args["highlight"].title())
      
    result_model = handle_yake(content,max_ngram_size, number_of_keywords, highlight)
    
    return jsonify(result_model)      
    
    
@api_frontend.route("/yake/v2/extract_keywords",methods=['GET'])
def handle_keyword_extraction_get():
    """
    extract keywords from input text
    ---

    tags:
    - available methods
    parameters:
      - name: content
        in: query
        type: string
        description: content
        required: true
      - name: max_ngram_size
        in: query
        type: integer
        description: max size of ngram
        required: true
        default: 3
      - name: number_of_keywords
        in: query
        type: integer
        description: number of keywords to return
        required: true
        default: 20
      - in: query
        name: highlight
        type: boolean
        default: 20
        required: false
        description: If true, the endpoint returns input text highlighting detected keywords.
    

    responses:
      200:
        description: Extract keywords from input text
        schema:
          id: result
          properties:
            language:
              type: string
              description: detected language
            keywords:
              type: array
              items:
                schema:
                  id: SubItem
                  properties:
                    ngram:
                      type: string
                      description: ngram
                    score:
                      type: integer
                      description: relevance score

    """

    content = request.args["content"]

    max_ngram_size = int(request.args["max_ngram_size"])
    number_of_keywords = int(request.args["number_of_keywords"])
    highlight = False

    if("highlight" in request.args):
      highlight = distutils.util.strtobool(request.args["highlight"].title())
      
    result_model = handle_yake(content,max_ngram_size, number_of_keywords, highlight)

    return jsonify(result_model)    
