import json
import requests
import sys

from config import RESULT_NUM, MINIMUM_SCRIPT_SIZE, FILENAME, ACCESS_TOKEN_PARAM

# returns JSON content of content_url as dict. If status is not OK or content 
# is not JSON return None
def get_json(content_url):
    try:
        content_request = requests.get(content_url)
        return json.loads(content_request.text)
    except:
        return None

# returns list of repo content URLs from GitHub search items list
def get_repo_content_urls(repo_list):
    repo_url_list = []
    for item in repo_list:
        repo_url = item['contents_url'].replace('{+path}', '')
        repo_url_list.append(repo_url)
    return repo_url_list

# returns list of directory paths found in content_list
def filter_dir_paths(content_list):
    dir_list = []
    for item in content_list:
        if item['type'] == 'dir':
            dir_list.append(item['path'])
    return dir_list

# returns list of python script URLs found in content_list (the size of the 
# scripts must match or exceed MINIMUM_SCRIPT_SIZE)
def filter_script_paths(content_list):
    python_paths = []
    for item in content_list:
        item_name = item['name']
        if item_name.endswith('.py') and item['size'] >= MINIMUM_SCRIPT_SIZE:
            python_paths.append(item['path'])
    return python_paths

# returns list of Python script URLs. Takes a Github repo URL as a parameter
def get_script_urls(url):
    contents = get_json(url + '?' + ACCESS_TOKEN_PARAM)
    dir_path_list = filter_dir_paths(contents)
    script_paths = []
    script_paths.extend(filter_script_paths(contents))
    
    while len(dir_path_list) > 0:
        dir_url = url + dir_path_list.pop(0) + '?' + ACCESS_TOKEN_PARAM
        content = get_json(dir_url)
        if content == None:
            continue  
        # if a repo contains only one file the return value is a dict and not a 
        # list so it must be wrapped
        if type(content) == dict:
            content = [content]
        dir_path_list.extend(filter_dir_paths(content))
        script_paths.extend(filter_script_paths(content))

    script_urls = [url + '/' + path for path in script_paths]
    return script_urls


base_search_url = 'https://api.github.com/search/repositories?'
search_params = 'q=language:python&sort=stars&order=desc'
results_per_page = 'per_page=' + str(RESULT_NUM)
search_url = base_search_url + '&'.join((search_params, results_per_page, 
    ACCESS_TOKEN_PARAM))

if __name__ == '__main__':
    search_r = requests.get(search_url)
    try:
        search_r.raise_for_status()
    except:
        sys.exit('Couldn\'t access Github\'s search results.')
    search_data = json.loads(search_r.text)
    
    repo_urls = get_repo_content_urls(search_data['items'])
    print('Collecting script URLs.')    
    
    # write script URLs as list to the file specified in FILENAME (overrides 
    # existing file)
    with open(FILENAME, 'w') as file:
        file.write('script_urls = [\n')
        for repo_url in repo_urls:
            script_urls = get_script_urls(repo_url)
            for script_url in script_urls:
                file.write('    \'{}\',\n'.format(script_url))
                print('Wrote URL:', script_url)
        file.write(']')
    
    print('Finished collecting!')