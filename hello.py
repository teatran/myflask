import datetime
import feedparser   # for RSS feed
import json
import urllib2   # for currency 

from flask import Flask, render_template
from flask import request, make_response

app = Flask(__name__)

RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
'cnn': 'http://rss.cnn.com/rss/edition.rss',
'fox': 'http://feeds.foxnews.com/foxnews/latest',
'iol': 'http://www.iol.co.za/cmlink/1.640'}

CURRENCY_URL = ('https://openexchangerates.org/api/latest.json' +
                '?app_id=17c0dd92186047c5bb929e841c64fe14')

DEFAULTS = {'publication': 'bbc',
            'currency_from': 'USD',
            'currency_to': 'VND'}


def get_rate(from_select, to_select):
    all_currency = urllib2.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    from_rate = parsed.get(from_select.upper())
    to_rate = parsed.get(to_select.upper())
    return (to_rate/from_rate, parsed.keys())
    

@app.route("/")
def home():
    # publication
    publication = request.args.get('publication')
    if not publication or publication.lower() not in RSS_FEEDS:
        publication = request.cookies.get('publication')
        if not publication:
            publication = DEFAULTS['publication']
    feed = feedparser.parse(RSS_FEEDS[publication])
    articles = feed['entries']

    # currency
    currency_from = request.args.get('currency_from')
    if not currency_from:
        currency_from = request.cookies.get('currency_from')
        if not currency_from:
            currency_from = DEFAULTS['currency_from']
            
    currency_to = request.args.get('currency_to')
    if not currency_to:
        currency_to = request.cookies.get('currency_to')
        if not currency_to:
            currency_to = DEFAULTS['currency_to']
    rate, currencies = get_rate(currency_from, currency_to)

    # make a response object and set the cookies
    response = make_response(render_template('home.html',
                                             articles=articles,
                                             currency_from=currency_from,
                                             currency_to=currency_to,
                                             rate=rate,
                                             currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie('publication', publication, expires=expires)
    response.set_cookie('currency_from', currency_from, expires=expires)
    response.set_cookie('currency_to', currency_to, expires=expires)

    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
