from flask import Flask
from flask import render_template

import base64
import json
import random
import re
import requests

from python_links import script_urls
from config import ACCESS_TOKEN_PARAM


app = Flask(__name__)

def get_script_data(script_url):
    content_r = requests.get(script_url)
    try:
        content_r.raise_for_status()
    except:
        return None
    content_obj = json.loads(content_r.text)

    source_code = decode_content(content_obj['content'])
    file_url = content_obj['html_url']
    project_name, project_url = get_project_details(file_url)

    data = {
        'content': source_code,
        'filename': content_obj['name'],
        'file_url': file_url,
        'project_name': project_name,
        'project_url': project_url
    }
    return data

def decode_content(encoded_content):
    content_bytes = base64.b64decode(encoded_content)
    content = content_bytes.decode()
    return content

def get_project_details(file_url):
    project_url_re = re.compile(r'''
        (https://github.com/
        [A-Za-z0-9-]+/              # user name
        ([A-Za-z0-9_.-]+)/          # project name
        .*)''', re.VERBOSE)
    mo = project_url_re.match(file_url) 
    project_url = mo.group(1)
    project_name = mo.group(2)
    return (project_name, project_url)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/random_code')
def random_code():
    random_url = random.choice(script_urls) + '?' + ACCESS_TOKEN_PARAM
    data = get_script_data(random_url)
    if data == None:
        abort(500)
    return render_template('code_content.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)