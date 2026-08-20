#!/usr/bin/env python3
import requests, uuid, time, urllib.parse, random, urllib3, os, sys
urllib3.disable_warnings()
API = 'https://api.tianmiao.icu/api'
INVITE = 'ghqhsqRD'
GIST_ID_FILE = '.gist_id'
FILENAME = '天喵.txt'
UA = ['okhttp/4.12.0', 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36']
def hdr(tok=None, auth=None):
    h = {'deviceid': str(uuid.uuid4()), 'devicetype': '1', 'Content-Type': 'application/json; charset=UTF-8', 'User-Agent': random.choice(UA)}
    if tok and auth: h.update({'token': tok, 'authtoken': auth})
    return h
def extract():
    s = requests.Session(); s.verify = False
    r = s.post(f'{API}/register', headers=hdr(), json={'email': f't{int(time.time())}@qq.com', 'password': 'asd789369', 'password_word': 'asd789369'})
    d = r.json(); tok, auth = d['data']['auth_data'], d['data']['token']
    time.sleep(2)
    try: s.post(f'{API}/bandInviteCode', headers=hdr(tok, auth), json={'invite_code': INVITE})
    except: pass
    time.sleep(2)
    r = s.post(f'{API}/nodeListV2', headers=hdr(tok, auth), json={'protocol': 'all', 'include_ss': '1', 'include_shadowsocks': '1', 'include_trojan': '1'})
    urls = []
    for g in r.json().get('data', []):
        if g.get('type') == 'vip':
            for n in g.get('node', []):
                if isinstance(n, dict) and 'url' in n: urls.append(n['url'])
    return urls
def upload_gist(content, token):
    headers = {'Authorization': f'token {token}', 'Accept': 'application/vnd.github.v3+json'}
    gist_id = None
    if os.path.exists(GIST_ID_FILE):
        with open(GIST_ID_FILE) as f: gist_id = f.read().strip()
    payload = {'description': '天喵 VPN 节点（自动更新）', 'public': False, 'files': {FILENAME: {'content': content}}}
    if gist_id: r = requests.patch(f'https://api.github.com/gists/{gist_id}', headers=headers, json=payload)
    else: r = requests.post('https://api.github.com/gists', headers=headers, json=payload)
    if r.status_code in (200, 201):
        gist_id = r.json()['id']
        with open(GIST_ID_FILE, 'w') as f: f.write(gist_id)
        raw = f'https://gist.githubusercontent.com/raw/{gist_id}/{FILENAME}'
        print(f'Gist 直链: {raw}')
        return raw
    else:
        print(f'上传失败: {r.status_code}')
        return None
def main():
    token = os.environ.get('GITHUB_TOKEN') or (sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--token' else None)
    if not token: print('需要 GITHUB_TOKEN'); return
    print('提取节点中...')
    urls = extract()
    print(f'VIP节点: {len(urls)} 个')
    content = '\n'.join(urls) + '\n'
    with open(FILENAME, 'w', encoding='utf-8') as f: f.write(content)
    upload_gist(content, token)
if __name__ == '__main__': main()
