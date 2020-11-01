from flask import Flask, render_template 
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
import os 
from youtube_dl import YoutubeDL 
from celery import Celery



app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

celery = make_celery(app)


class SearchForm(FlaskForm):
    search = StringField('Paste URL here...', validators=[URL('Only URLs are accepted')])
    submit = SubmitField('Download')


@app.route('/', methods=['GET', 'POST'])
def index():
    #books = []
    key = None
    form = SearchForm()
    if form.validate_on_submit():
        url = form.search.data
        download_video.delay(url)
        form.search.data = ''
    return render_template('index.html', form=form)

@celery.task()
def download_video(url):
    with YoutubeDL({'format':'136'}) as ydl:
            return ydl.download([url])