import requests
from lxml import html, etree
import re
import web
import shelve

urls = (
    '/profile/(.+)', 'get_profile',
    '/users', 'list_users',
    '/users/(.*)', 'get_user'
)

app = web.application(urls, globals())


def get_users_data():
    db = shelve.open('data.db')
    data = []
    if db.has_key('users'):
        data = db['users']
    db.close()
    return data


def store_user_data(user_data):
    db = shelve.open('data.db')
    if db.has_key('users'):
        temp = db['users']
        temp.append(user_data)
        db['users'] = temp
    else:
        db['users'] = [user_data]
    db.close()


def fetch_profile(url):
    headers = {'User-agent': 'Mozilla/5.0'}
    r = requests.get(url, headers=headers)
    data = parse_page(r)
    # store data
    store_user_data(data)
    # return
    return data


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def parse_page(page):
    data = {}
    # print page.content
    root = html.fromstring(page.content)
    # name
    e = root.find(".//h1[@id='name']")
    data['name'] = e.text
    # # title
    e = root.find(".//p[@class='headline title']")
    data['title'] = e.text
    # current positions
    # e = root.find(".//tr[@data-section='currentPositionsDetails']")
    # data['current'] = cleanhtml(etree.tostring(e))
    # summary
    e = root.find(".//section[@id='summary']")
    data['summary'] = cleanhtml(etree.tostring(e))
    # skills
    list = root.findall(".//li[@class='skill']/a/span")
    data['skills'] = [e.text for e in list]
    return data


class list_users:
    def GET(self):
        return get_users_data()


class get_user:
    def GET(self, user):
        return 'get_user'


class get_profile:
    def GET(self, url):
        print 'URL: %s' % url


if __name__ == "__main__":
    # store_user_data({'name': 'tomer1'})
    # store_user_data({'name': 'tomer2'})
    # app.run()
    fetch_profile('https://il.linkedin.com/in/fridtom')
