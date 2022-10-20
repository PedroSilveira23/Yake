from flask_wtf import FlaskForm
from wtforms.fields import *
from wtforms.validators import Required
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileRequired

class BaseInputForm(FlaskForm):
    n_gram_max_size = IntegerField(u'Max size of ngram')
    # language = TextField(u'Language')
    
class UrlInputForm(BaseInputForm):
    page_url = TextField(u'Url', validators=[Required()])
    
class PDFInputForm(BaseInputForm):
    pdf_file = FileField(u'PDF', validators=[FileRequired()])

class UserInputForm(BaseInputForm):
    # title = TextField(u'Title')
    content = TextAreaField(u'Content',widget=TextArea(),validators=[Required()])
    
class SampleInputForm(BaseInputForm):
    sample_name = HiddenField(u'sample_name', validators=[Required()])
    
    # title = TextField(u'Title',render_kw={'disabled':''})
    # title = TextField(u'Title')
    content = TextAreaField(u'Content',widget=TextArea(),validators=[Required()],render_kw={'readonly':''})
    # content = TextAreaField(u'Content',widget=TextArea(),validators=[Required()])
    
class DatasetInputForm(SampleInputForm):
    ground_truth = TextAreaField(u'ground_truth',widget=TextArea(),validators=[Required()],render_kw={'readonly':''})

