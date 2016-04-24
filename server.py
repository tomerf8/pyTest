import requests
from lxml import html, etree
import re
import web
import shelve
from collections import Counter

urls = (
    '/profile/(.+)', 'get_profile',
    '/users', 'list_users',
    '/users/(.*)', 'get_user',
    '/skills', 'get_skills'
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
    return store_top_skills(user_data['skills'])


def get_top_skills():
    db = shelve.open('data.db')
    data = []
    if db.has_key('skills'):
        data = db['skills']
    db.close()
    return data


def store_top_skills(skills):
    db = shelve.open('data.db')
    skill_count = Counter(list(skills))

    if db.has_key('skills'):
        temp_counter = Counter(list(db['skills']))
        temp_counter = temp_counter + skill_count
        print temp_counter
        db['skills'] = dict(temp_counter)
    else:
        db['skills'] = dict(skill_count)
    db.close()


def fetch_profile(url):
    headers = {'User-agent': 'Mozilla/5.0 ()'}
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
    print page.content
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


def inject_mock_data():
    store_user_data({'name': 'tomer1', 'skills': ['Java', 'Python']})
    store_user_data({'name': 'tomer2', 'skills': ['Java', 'Perl']})


class list_users:
    def GET(self):
        return get_users_data()


class get_user:
    def GET(self, user):
        user = filter(lambda x: 'name' in x and x['name'] == user, get_users_data())
        if user is not None:
            return user
        return 'User not found!'


class get_profile:
    def GET(self, url):
        return fetch_profile(url)


class get_skills:
    def GET(self):
        return get_top_skills()


if __name__ == "__main__":
    inject_mock_data()
    # fetch_profile('https://il.linkedin.com/in/fridtom')
    app.run()
