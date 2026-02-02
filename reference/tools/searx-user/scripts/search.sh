#!/bin/bash
python3 -c "
import requests
import json
import sys

query = '$1'
max_results = int('${2:-10}')
lang = '${3:-en}'

params = {
    'q': query,
    'language': lang,
    'format': 'json',
    'safesearch': 1
}

try:
    r = requests.get('http://127.0.0.1:8888/search', params=params, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
    r.raise_for_status()
    data = r.json()

    output = []
    for result in data.get('results', [])[:max_results]:
        output.append({
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'content': result.get('content', ''),
            'engine': result.get('engine', ''),
            'category': result.get('category', '')
        })

    print(json.dumps(output, ensure_ascii=False, indent=2))
except Exception as e:
    print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)
"
