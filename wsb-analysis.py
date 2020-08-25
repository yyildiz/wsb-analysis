import praw
from psaw import PushshiftAPI
import datetime
import calendar
import csv
from collections import defaultdict
from collections import OrderedDict
from decimal import Decimal

ticker_occurrences = {}

def get_all_comments():

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    timestamp = calendar.timegm(yesterday.timetuple())

    api = PushshiftAPI()
    with open('comments.csv', mode='w', encoding='utf-8', newline='') as comments_file:
        gen = api.search_comments(after=timestamp, subreddit='wallstreetbets', filter=['body'])
        comment_writer = csv.writer(comments_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for c in gen:
            comment_writer.writerow([c[0]])

get_all_comments()

def get_all_stock_occurrences():
    stocks_file = open('all-stocks.csv', mode='r')
    stock_reader = list(csv.reader(stocks_file, delimiter=','))
    comments_file = open('comments.csv', mode='r', encoding='utf-8')
    comment_reader = list(csv.reader(comments_file, delimiter=','))

    for stock in stock_reader:
        for comment in comment_reader:
            count = comment[0].count(stock[0])
            if stock[0] in ticker_occurrences:
                ticker_occurrences[stock[0]] += count
            else:
                ticker_occurrences[stock[0]] = count
    return sorted(ticker_occurrences.items(), key=lambda x: x[1], reverse=True)

def output_sorted_occurrences():
    output_file = open('output.csv', mode='w', newline='')
    output_writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    stock_occurrences = get_all_stock_occurrences()
    for stock, occurrence in stock_occurrences:
        output_writer.writerow([stock, occurrence])

def merge_occurrences_with_stock_list():
    with open('all-stocks.csv', mode='r') as f:
        r = csv.reader(f)
        dict2 = {row[0]: row[1:] for row in r}

    with open('output.csv', mode='r') as f:
        r = csv.reader(f)
        dict1 = OrderedDict((row[0], row[1:]) for row in r)

    result = OrderedDict()
    for d in (dict1, dict2):
        for key, value in d.items():
            result.setdefault(key, []).extend(value)

    with open('stocks-with-market-cap.csv', mode='w', newline='') as f:
        w = csv.writer(f)
        for key, value in result.items():
            w.writerow([key] + value)

# merge_occurrences_with_stock_list()


def convert(val):
    lookup = {'M': 6, 'B': 9, 'T': 12}
    noDollas = val.split('$')
    if (len(noDollas) <  2):
        return 0
    n = noDollas[1]
    if n[-1] in lookup:
        num, magnitude = n[:-1], n[-1]
        return Decimal(num) * 10 ** lookup[magnitude]
    else:
        return Decimal(n)

def remove_stock_below_market_cap(minimum):
    stocks_file = open('stocks-with-market-cap.csv', mode='r')
    stocks_reader = list(csv.reader(stocks_file, delimiter=','))

    final_file = open('final.csv', mode='w', encoding='utf-8', newline='')
    final_writer = csv.writer(final_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    for stock in stocks_reader:
        if (len(stock) > 4 and stock[4] != 'n/a' and convert(stock[4]) > minimum):
            final_writer.writerow([stock])

# remove_stock_below_market_cap(500000000)