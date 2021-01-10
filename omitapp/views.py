from django.shortcuts import render
from django.http import HttpResponseRedirect

# Create your views here.
def main_view(request):
    return render(request, 'omitapp/main.html')


import requests
from bs4 import BeautifulSoup
import json

def check_omit(blog_id):
    post_base = 'https://blog.naver.com/PostViewBottomTitleListAsync.nhn?blogId={}&logNo={}&sortDateInMilli={}'
    p_base = 'https://blog.naver.com/{}/{}'
    blog_base = 'https://blog.naver.com/PostList.nhn?blogId={}&categoryNo=0&from=postList'
    
    r = requests.get(blog_base.format(blog_id))
    sp = BeautifulSoup(r.text, 'html.parser')
    logno = sp.select_one('p.url a').attrs['href'].split('/')[-1]
    daty = ''

    post_urls = []
    while True:
        post_r = requests.get(post_base.format(blog_id, logno, daty))
        results = json.loads(post_r.text)
        
        post_urls.extend([p['logNo'] for p in results['postList']])
        
        logno = results['nextIndexLogNo']
        daty = results['nextIndexSortDate']

        if not logno:
            break

    post_is_searching={}
    for post_url in set(post_urls):
        p_r = requests.get(p_base.format(blog_id, post_url))
        sp = BeautifulSoup(p_r.text, 'html.parser')
        src = sp.select_one('iframe').attrs['src']
        iframe_r = requests.get('http://blog.naver.com%s'%src)
        iframe_sp = BeautifulSoup(iframe_r.text, 'html.parser')
        try:
            post_title = iframe_sp.select_one('div#title_1 span').text
        except:
            post_title = iframe_sp.select_one('div.se-title-text span').text

        search_r = requests.get('https://search.naver.com/search.naver?query={}&where=web'.format('"%s"'%post_title))
        search_sp = BeautifulSoup(search_r.text, 'html.parser')
        search_titles = [t.text.strip() for t in search_sp.select('div.total_tit')]
        if post_title in search_titles:
            post_is_searching[post_title] = True
        else:
            post_is_searching[post_title] = False

    return post_is_searching

def temp_view(request):
    blog_id = request.GET.get('bid')
    result = check_omit(blog_id)
    return render(request, 'omitapp/create.html', {'bid': blog_id, 'result':result})