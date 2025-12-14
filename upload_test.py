import http.client
import urllib.parse
import json
import mimetypes

TOKEN_USER = 'admin'
TOKEN_PASS = 'admin123'
FILEPATH = 'test_upload.docx'

# get token
conn = http.client.HTTPConnection('localhost', 8000)
body = urllib.parse.urlencode({'username': TOKEN_USER, 'password': TOKEN_PASS})
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
conn.request('POST', '/token', body, headers)
res = conn.getresponse()
data = res.read()
print('Token response status', res.status)
print(data)
if res.status != 200:
    print('Failed to get token')
    raise SystemExit(1)

token = json.loads(data)['access_token']
print('Got token:', token[:20] + '...')

# prepare multipart
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
CRLF = '\r\n'
lines = []

# department
lines.append('--' + boundary)
lines.append('Content-Disposition: form-data; name="department"')
lines.append('')
lines.append('CSE')

# category
lines.append('--' + boundary)
lines.append('Content-Disposition: form-data; name="category"')
lines.append('')
lines.append('research')

# file
filename = FILEPATH
ctype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
with open(FILEPATH, 'rb') as f:
    filedata = f.read()

lines.append('--' + boundary)
lines.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"')
lines.append(f'Content-Type: {ctype}')
lines.append('')
body_start = CRLF.join(lines).encode('utf-8') + CRLF.encode('utf-8')
body_end = CRLF.encode('utf-8') + b'--' + boundary.encode('utf-8') + b'--' + CRLF.encode('utf-8')

body = body_start + filedata + body_end

# send upload
conn = http.client.HTTPConnection('localhost', 8000)
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': f'multipart/form-data; boundary={boundary}',
    'Content-Length': str(len(body))
}
conn.request('POST', '/api/upload', body, headers)
res = conn.getresponse()
print('Upload response status', res.status)
print(res.read())
