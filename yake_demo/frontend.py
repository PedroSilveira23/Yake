# This contains our frontend; since it is a bit messy to use the @app.route
# decorator style when using application factories, all of our routes are
# inside blueprints. This is the front-facing blueprint.
#
# You can find out more about blueprints at
# http://flask.pocoo.org/docs/blueprints/
# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, flash, redirect, url_for
# from flask_debug import Debug
from flask_bootstrap import __version__ as FLASK_BOOTSTRAP_VERSION
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from markupsafe import escape
from flask import Blueprint, render_template, flash, redirect, url_for
from flask import Flask, render_template, redirect, url_for, session, request, flash, abort, Markup
from .forms import UserInputForm, UrlInputForm, DatasetInputForm, SampleInputForm, PDFInputForm
from .nav import nav
import os
from demo.keyword_extractors import *
import json
import codecs
from stop_words import safe_get_stop_words
import time
from demo.languages import isoLangs

from yake.highlight import TextHighlighter

from demo.utils import *
from demo.remote_url import *

frontend = Blueprint('frontend', __name__)

# We're adding a navbar as well through flask-navbar. In our example, the
# navbar has an usual amount of Link-Elements, more commonly you will have a
# lot more View instances.
nav.register_element('frontend_top', Navbar(
    View('YAKE! Demo', '.index'),
    View('Home', '.index'),

    Subgroup(
        'Keyword extraction',
        Separator(),
        View('Free text input', '.handle_demo_user'),
        View('Page Url', '.demo_page_input'),
    ),

    Subgroup(
        'Sample documents',
        Separator(),
            View('English - Tech news', '.demo_sample_document',sample_name='sample1'),
            View('English - Tech news', '.demo_sample_document',sample_name='sample2'),
            View('English - Tech news', '.demo_sample_document',sample_name='sample3'),
            Separator(),
            View('Portuguese - Sport', '.demo_sample_document',sample_name='sample15'),
            View('Portuguese - Tourism', '.demo_sample_document',sample_name='sample12'),
            Separator(),
            View('Italian - Sports', '.demo_sample_document',sample_name='sample4'),
            View('German - Politics', '.demo_sample_document',sample_name='sample5'),
            View('Dutch - Culture', '.demo_sample_document',sample_name='sample6'),
            View('Spanish - History', '.demo_sample_document',sample_name='sample7'),
            View('Finnish - Tech news', '.demo_sample_document',sample_name='sample8'),
            View('French - Religion', '.demo_sample_document',sample_name='sample9'),
            View('Polish - Economy', '.demo_sample_document',sample_name='sample10'),
            View('Turkish - Education', '.demo_sample_document',sample_name='sample11'),
            View('Arabic - Biography', '.demo_sample_document',sample_name='sample13')
    ),

    Subgroup(
        'Official datasets samples',
        Separator(),
        View('110-PT-BN-KP', '.demo_dataset_document',sample_name='110-PT-BN-KP'),
        View('500N-KPCrowd-v1.1', '.demo_dataset_document',sample_name='500N-KPCrowd-v1.1'),
        #View('citeulike180', '.demo_dataset_document',sample_name='citeulike180'),
        #View('fao780', '.demo_dataset_document',sample_name='fao780'),
        View('Inspec (1)', '.demo_dataset_document',sample_name='Inspec'),
        View('Inspec (2)', '.demo_dataset_document',sample_name='Inspec2'),
        View('Nguyen2007', '.demo_dataset_document',sample_name='Nguyen2007'),
        View('PubMed', '.demo_dataset_document',sample_name='PubMed'),
        View('SemEval2010', '.demo_dataset_document',sample_name='SemEval2010'),
        #View('theses100', '.demo_dataset_document',sample_name='theses100')
    ),

    View('Open Source', '.pip'),
    View('API', '.api'),
    View('Mobile App', '.mobile'),
    Subgroup(
        'Related Projects',
        Separator(),
        View('SparkNLP', '.related_projects',name='SparkNLP'),
        View('textacy', '.related_projects',name='textacy'),        
        View('pke Toolkit', '.related_projects',name='pke'),
        View('Dockerized Yake', '.related_projects',name='dockerfile'),
        Separator(),
        View('Dendro', '.related_projects', name="dendro"),
        View('Conta-me Histórias', '.related_projects', name="contamehistorias"),
#        View('PDF', '.demo_pdf_input')
    ),
    View('About', '.about')

    ),)

@frontend.route('/')
def index():
    return render_template('index.html')

@frontend.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@frontend.route('/tellmestories/disclaimer')
def disclaimer_tellmestories():
    return render_template('disclaimer_tellmestories.html')    

@frontend.route('/about')
def about():
    return render_template('about.html')

@frontend.route('/api')
def api():
    return redirect('apidocs/index.html?url=/yake/v2/spec#!/available_methods/post_yake_v2_extract_keywords')

@frontend.route('/mobile')
def mobile():
    return redirect('https://play.google.com/store/apps/details?id=com.yake.yake')    

@frontend.route('/pip')
def pip():
    return redirect('https://github.com/LIAAD/yake', code=302)

@frontend.route('/related/<name>')
def related_projects(name):
    if(name == "SparkNLP"):
        return redirect("https://nlp.johnsnowlabs.com/docs/en/annotators#yakemodel-keywords-extraction", code=302)

    if(name == "textacy"):
        return redirect("https://github.com/chartbeat-labs/textacy", code=302)    

    if(name == "pke"):
        return redirect("https://github.com/boudinfl/pke", code=302)

    if(name == "dendro"):
        return redirect("http://dendro-stg.inesctec.pt/", code=302)

    if(name == "dockerfile"):
        return redirect("https://github.com/LIAAD/yake#option-1-yake-as-a-cli-utility-inside-a-docker-container", code=302)

    if(name == "contamehistorias"):
        return redirect("http://contamehistorias.pt", code=302)

    return  redirect("/")


def convertToUTF8(text):
    try:
        _text = text.replace("\t"," ").replace("\r"," ")
    except Exception:
        return text
    return _text

def handle_keyword_extractor_request(content,n_gram_max_size):
    # extract keywords

    start_time = time.time()

    content = convertToUTF8(content)

    _detected_language = detect(content)
    undefined = False
    
    if _detected_language in isoLangs.keys():
        # language_name = iso_languages[_detected_language]
        language_name = isoLangs[_detected_language]["name"].lower()
    else:
        undefined = True
        language_name = "english"

    # TODO: replace by another library
    #alchemy = AlchemyKeywordExtrator()
    rake = RakeKeywordExtrator()

    #TODO: A API do YAKE deve suportar o padrao ISO_639-1.
    # assim nao precisamos fazer isso
    detected_language = _detected_language
    # if(_detected_language in iso_code_languages.keys()):
    #     detected_language = iso_code_languages[_detected_language][0]

    print("3.detected_language",detected_language)
    yake = YakeKeywordExtrator_wcf()

    time_yake = time.time()
    kwport_keywords = yake.execute(text=content, language=detected_language, n_gram_max_size=n_gram_max_size, top=20)
    spent_time_yake = time.time() - time_yake

    highlight_pre = '<span class="highlight_keyword">'
    highlight_post = '</span>'
    
    th = TextHighlighter(max_ngram_size = int(n_gram_max_size), highlight_pre = highlight_pre, highlight_post= highlight_post)
    
    keywords_ngrams = [x["Key"] for x in  kwport_keywords]
    highlighted_text = th.highlight(content, keywords_ngrams)
    
    rake_keywords = rake.execute(content, language=_detected_language, n_gram_max_size=n_gram_max_size)

    alchemy_keywords = []

    keywords_for_wordcloud = []

    kwport_keywords_normalized = normalize_scores(kwport_keywords)
    kwport_keywords_normalized = sorted(kwport_keywords_normalized, key=lambda x: x["Value"], reverse=False)

    for item in kwport_keywords_normalized:
    #     #TODO: fixme. annotation e uma palavra reservada nossa para highlight
    #     if(item["Key"].lower() != "annotation"):
        keywords_for_wordcloud.append({"text":item["Key"],"size":item["Value"],"time":0})

    keywords_for_wordcloud = sorted(keywords_for_wordcloud, key=lambda x: x["size"], reverse=False)

    if undefined:
        language_name = detected_language + " is not supported"

    num_max_keywords = 20

    total_spent_time = time.time() - start_time

    print("time spent to get yake results", spent_time_yake)
    print("time spent to get all results", total_spent_time)

    model = {
        "stats" : {"time_yake":spent_time_yake,
                   "time:total":total_spent_time},

    "num_max_keywords": {
            "annotation":20,
            "comparative":num_max_keywords
        },
    "language":language_name,
    "detectLan":_detected_language,
    "highlighted_text":highlighted_text, 
    "alchemy" : {
            "keywords":alchemy_keywords[:num_max_keywords],
            "background-color":"#111"
            },
    "yake" : {
            "keywords":kwport_keywords[:num_max_keywords],
            "wordcloud":keywords_for_wordcloud[:100],
            "keywords_to_annotate":keywords_for_wordcloud[-20:],
            "background-color":"#222"
            },

    "rake" : {
            "keywords":rake_keywords[:num_max_keywords],
            "background-color":"#111"
            }
    }

    return model

@frontend.route('/demo/user', methods=['GET', 'POST'])
def handle_demo_user():
    form = UserInputForm(csrf_enabled=False)

    if request.method == 'GET':
        form.n_gram_max_size.data = 3

    if request.method == 'POST':
        if form.validate():

            input_data = {
                #"title":form.title.data,
                "content":form.content.data
            }

            model = handle_keyword_extractor_request(
                                    form.content.data,
                                    form.n_gram_max_size.data)

            model = processClassModel(model, set(safe_get_stop_words(model['detectLan'])))
            return render_template('result_view.html',
                                    input_data=input_data,
                                    model=model
                                    )

    return render_template('demo_free_input.html',
        page_title="Free text input",
        form=form)

@frontend.route('/demo/url', methods=['GET', 'POST'])
def demo_page_input():
    form = UrlInputForm(csrf_enabled=False)

    if request.method == 'GET':
        form.n_gram_max_size.data = 3
        form.page_url.data = "http://neurosciencenews.com/genetics-brain-aging-6250"

    if request.method == 'POST':
        if form.validate():

            # title, content = handle_remote_page_content(form.page_url.data)
            content = handle_remote_page_content(form.page_url.data)

            input_data = {
                # "title":title,
                "content":content
            }

            model = handle_keyword_extractor_request(
                                        # title,
                                        content,
                                        form.n_gram_max_size.data)
            model = processClassModel(model, set(safe_get_stop_words(model['detectLan'])))
            return render_template('result_view.html',
                                    input_data=input_data,
                                    model=model
                                    )

    return render_template('demo_url_input.html',
                page_title="Extract keywords from web page",
                form=form)

import PyPDF2
def handle_pdf2(data):
    pdf = PyPDF2.PdfFileReader(data)
    pdf_text = ""

    #limitar numero de paginas?
    max_pages = 5
    for page in pdf.pages[:max_pages]:
        pdf_text += page.extractText() + " "

    return "", pdf_text


def valid_xml_char_ordinal(c):
    codepoint = ord(c)
    # conditions ordered by presumed frequency
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
        )

def handle_sample_document_content(sample_name):

    dir_name = os.path.dirname(__file__)

    import codecs

    json_file = dir_name + "/data/"+sample_name+".txt"

    if(os.path.exists(json_file)):
        content = open(json_file,"r").read()
        content = convertToUTF8(content.replace("\n"," ").replace("\r"," ").replace("\t"," "))

        return json.loads(content)
    else:
        return None

def handle_dataset_document_content(sample_name):
    dir_name = os.path.dirname(__file__)

    import codecs

    json_file = dir_name + "/data/"+sample_name+".txt"
    ground_truth_file = dir_name + "/data/"+sample_name+".key"

    if( os.path.exists(json_file) and os.path.exists(ground_truth_file) ):
        content = open(json_file,"r").read()
        json_content = json.loads(content.replace("\n"," ").replace("\r"," ").replace("\t"," "))
        _ground_truth = codecs.open(ground_truth_file,"r",encoding="UTF-8").read()
        _ground_truth = _ground_truth.lower().replace("\t"," ").split("\n")
        ground_truth = set( [ gt for gt in _ground_truth if len(gt.strip()) > 0 ] )
        return (json_content, ground_truth)
    else:
        return (None, None)

def processClassModel(model, stopwords):
    identifiers = {}
    for approach in ["alchemy", "yake", "rake"]:
        if approach in model:
            for key in model[approach]["keywords"]:
                classKeyword = set()
                for tokenKeyword in key['Key'].split(" "):
                    if tokenKeyword not in stopwords:
                        if tokenKeyword not in identifiers:
                            identifiers[tokenKeyword] = "classToken%d" % len(identifiers)
                        classKeyword.add(identifiers[tokenKeyword])
                key['class'] = classKeyword
    return model

@frontend.route('/demo/sample/', methods=['POST'], defaults={'sample_name': None})
@frontend.route('/demo/sample/<sample_name>', methods=['GET'])
def demo_sample_document(sample_name):

    form = SampleInputForm()

    if request.method == 'GET':

        form.n_gram_max_size.data = 3

        input_data = handle_sample_document_content(sample_name)

        if(input_data):
            content = input_data["title"] + ". " + input_data["content"]
            form.sample_name.data = sample_name
            # form.title.data = input_data["title"]
            form.content.data = content
        else:
            return render_template('index.html')

    if request.method == 'POST':

        input_data = handle_sample_document_content(form.sample_name.data)
        
        content = input_data["title"] + ". " + input_data["content"]

        model = handle_keyword_extractor_request(
                                    # input_data["title"],
                                    content,
                                    form.n_gram_max_size.data)

        model = processClassModel(model, set(safe_get_stop_words(model['detectLan'])))
        return render_template('result_view.html',
                                input_data=input_data,
                                model=model
                                )

    return render_template('demo_sample.html',
                page_title="Extract keywords from sample document",
                form=form)

def toprintGroundTruth(ground_truth, sep):
    toreturn = ""
    for goldkey in ground_truth:
        toreturn += goldkey + sep
    return toreturn

def processClass(model, _ground_truth, stopwords):
    identifiers = {}
    ground_truth = {}
    for gold in _ground_truth:
        classGoldKey = set()
        for tokenGold in gold.split(" "):
            tokenGold = tokenGold.strip()
            if tokenGold not in stopwords:
                if tokenGold not in identifiers:
                    identifiers[tokenGold] = "classToken%d" % len(identifiers)
                classGoldKey.add( identifiers[tokenGold] )
        ground_truth[gold] = classGoldKey

    for approach in ["alchemy", "yake", "rake"]:
        if approach in model:
            for key in model[approach]["keywords"]:
                classKeyword = set()
                for tokenKeyword in key['Key'].split(" "):
                    tokenKeyword = tokenKeyword.strip()
                    if tokenKeyword not in stopwords:
                        if tokenKeyword not in identifiers:
                            identifiers[tokenKeyword] = "classToken%d" % len(identifiers)
                        classKeyword.add( identifiers[tokenKeyword] )
                key['class'] = classKeyword
    return model, ground_truth



@frontend.route('/demo/dataset/', methods=['POST'], defaults={'sample_name': None})
@frontend.route('/demo/dataset/<sample_name>', methods=['GET'])
def demo_dataset_document(sample_name):

    form = DatasetInputForm()

    if request.method == 'GET':

        form.n_gram_max_size.data = 3

        json_content, gt = handle_dataset_document_content(sample_name)

        input_data = {
            "content":json_content["content"],
            "ground_truth":gt,
            "dataset":json_content["dataset"],
            "id":json_content["id"]
        }

        if(input_data):
            form.sample_name.data = sample_name
            form.content.data = input_data["content"]
            form.ground_truth.data = toprintGroundTruth(gt, "\n")
        else:
            return render_template('index.html')

    if request.method == 'POST':

        json_content, gt = handle_dataset_document_content(form.sample_name.data)

        input_data = {
            "content":json_content["content"],
            "dataset":json_content["dataset"],
            "id":json_content["id"]
        }

        model = handle_keyword_extractor_request(
                                    input_data["content"],
                                    form.n_gram_max_size.data)

        model, gt = processClass(model, gt, set(safe_get_stop_words(model['detectLan'])))
        input_data["ground_truth"] = gt
        print("=================================================")
        print("input_data", input_data)
        print("=================================================")
        print("model", model)
        print("=================================================")
        print("gt", gt)
        print("=================================================")

        return render_template('result_view.html',
                                input_data=input_data,
                                model=model
                                )

    return render_template('demo_dataset.html',
                page_title="Extract keywords from " + sample_name + " dataset",
                input_data=input_data,
                form=form)
