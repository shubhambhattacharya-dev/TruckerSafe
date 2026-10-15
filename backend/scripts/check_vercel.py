import requests, re
html = requests.get('https://frontend-mocha-eight-15.vercel.app/').text
matches = re.findall(r'/assets/[^"]+\.js', html)
print("Vercel JS:", matches)
if matches:
    content = requests.get('https://frontend-mocha-eight-15.vercel.app' + matches[0]).text
    print("Has 120s timeout:", ('120000' in content or '12e4' in content))
