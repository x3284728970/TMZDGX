#!/usr/bin/env python3
import requests, uuid, time, random, urllib3, os, sys
urllib3.disable_warnings()

API = 'https://api.tianmiao.icu/api'
INVITE = os.environ.get('TM_INVITE_CODE', '')
FILENAME = 'tianmiao.txt'
GIST_DESC = '天喵 VPN 节点（自动更新）'
UA = ['okhttp/4.12.0', 'Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36']


def hdr(tok=None, auth=None):
    h = {
        'deviceid': str(uuid.uuid4()),
        'devicetype': '1',
        'Content-Type': 'application/json; charset=UTF-8',
        'User-Agent': random.choice(UA),
    }
    if tok and auth:
        h.update({'token': tok, 'authtoken': auth})
    return h


def extract():
    s = requests.Session()
    s.verify = False
    r = s.post(f'{API}/register', headers=hdr(),
               json={'email': f't{int(time.time())}@qq.com',
                     'password': 'asd789369',
                     'password_word': 'asd789369'})
    d = r.json()
    tok, auth = d['data']['auth_data'], d['data']['token']
    time.sleep(2)
    try:
        s.post(f'{API}/bandInviteCode', headers=hdr(tok, auth),
               json={'invite_code': INVITE})
    except Exception:
        pass
    time.sleep(2)
    r = s.post(f'{API}/nodeListV2', headers=hdr(tok, auth),
               json={'protocol': 'all', 'include_ss': '1',
                     'include_shadowsocks': '1', 'include_trojan': '1'})
    urls = []
    for g in r.json().get('data', []):
        if g.get('type') == 'vip':
            for n in g.get('node', []):
                if isinstance(n, dict) and 'url' in n:
                    urls.append(n['url'])
    return urls


def find_gist_id(token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    page = 1
    while True:
        r = requests.get(
            'https://api.github.com/gists',
            headers=headers,
            params={'per_page': 100, 'page': page},
        )
        if r.status_code != 200:
            print(f'列出 Gist 失败: {r.status_code} {r.text[:200]}')
            return None
        gists = r.json()
        if not gists:
            return None
        for g in gists:
            if g.get('description') == GIST_DESC:
                files = g.get('files', {})
                if FILENAME in files:
                    print(f'找到已有 Gist: {g["id"]}')
                    return g['id']
        if len(gists) < 100:
            return None
        page += 1


def upload_gist(content, token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
    }
    gist_id = find_gist_id(token)
    payload = {
        'description': GIST_DESC,
        'public': False,
        'files': {FILENAME: {'content': content}},
    }

    if gist_id:
        r = requests.patch(
            f'https://api.github.com/gists/{gist_id}',
            headers=headers,
            json=payload,
        )
        action = '更新'
    else:
        r = requests.post(
            'https://api.github.com/gists',
            headers=headers,
            json=payload,
        )
        action = '创建'

    if r.status_code in (200, 201):
        gist_id = r.json()['id']
        raw = f'https://gist.githubusercontent.com/raw/{gist_id}/{FILENAME}'
        print(f'{action} Gist 成功，直链: {raw}')
        return raw
    print(f'{action} Gist 失败: {r.status_code} {r.text[:300]}')
    return None


def main():
    token = os.environ.get('GITHUB_TOKEN') or (
        sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == '--token' else None
    )
    if not token:
        print('缺少 GITHUB_TOKEN')
        sys.exit(1)
    print('提取节点中...')
    urls = extract()
    print(f'VIP 节点: {len(urls)} 个')
    if not urls:
        print('没有提取到节点，API 可能暂时异常')
        sys.exit(1)
    content = '\n'.join(urls) + '\n'
    upload_gist(content, token)


if __name__ == '__main__':
    main()

