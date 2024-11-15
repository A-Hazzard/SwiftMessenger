import requests

resp = requests.post('https://textbelt.com/text', {
  'phone': '+18684921566',
  'message': 'Hello world',
  'key': '0ecacd39b46508871ad1e26cb49b3773daa73491yJ30IJTV7TuhMMEaJLlMBkhQa',
})
print(resp.json())
# 0ecacd39b46508871ad1e26cb49b3773daa73491yJ30IJTV7TuhMMEaJLlMBkhQa