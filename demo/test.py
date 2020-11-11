import requests

headers = {
    'authority': 'api.msrc.microsoft.com',
    'access-control-allow-origin': '*',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'authorization': 'undefined',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36',
    'content-type': 'application/json',
    'accept': '*/*',
    'origin': 'https://msrc.microsoft.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://msrc.microsoft.com/',
    'accept-language': 'zh-CN,zh;q=0.9',
}

response = requests.get('https://api.msrc.microsoft.com/sug/v2.0/zh-CN/vulnerability', headers=headers)
print(response.text)
import json
data = json.loads(response.text)
data = data.get('value')
import pdb
pdb.set_trace()


'''

Windows 10 Version 20H2 for x64-based Systems中的Internet Explorer 11,
Windows 10 Version 20H2 for ARM64-based Systems中的Internet Explorer 11,
Windows 10 Version 20H2 for 32-bit Systems中的Internet Explorer 11,
Windows 10 for x64-based Systems中的Microsoft Edge (EdgeHTML-based),
Windows 10 for 32-bit Systems中的Microsoft Edge (EdgeHTML-based),
Windows Server 2012 R2中的Internet Explorer 11,
Windows Server 2012 R2中的Internet Explorer 11,
Windows Server 2012中的Internet Explorer 11,
Windows Server 2012中的Internet Explorer 11,
Windows Server 2008 R2 for x64-based Systems Service Pack 1中的Internet Explorer 11,
Windows Server 2008 R2 for x64-based Systems Service Pack 1中的Internet Explorer 11,
Windows RT 8.1中的Internet Explorer 11,
Windows 8.1 for x64-based systems中的Internet Explorer 11,
Windows 8.1 for x64-based systems中的Internet Explorer 11,
Windows 8.1 for 32-bit systems中的Internet Explorer 11
,Windows 8.1 for 32-bit systems中的Internet Explorer 11,
Windows 7 for x64-based Systems Service Pack 1中的Internet Explorer 11,
Windows 7 for x64-based Systems Service Pack 1中的Internet Explorer 11
,Windows 7 for 32-bit Systems Service Pack 1中的Internet Explorer 11,
Windows 7 for 32-bit Systems Service Pack 1中的Internet Explorer 11,
Windows Server 2016中的Internet Explorer 11,
Windows 10 Version 1607 for x64-based Systems中的Internet Explorer 11,
Windows 10 Version 1607 for 32-bit Systems中的Internet Explorer 11,
Windows 10 for x64-based Systems中的Internet Explorer 11,
Windows 10 for 32-bit Systems中的Internet Explorer 11,
Windows 10 Version 1809 for ARM64-based Systems中的Internet Explorer 11
,Windows 10 Version 2004 for x64-based Systems中的Internet Explorer 11,Windows 10 Version 2004 for ARM64-based Systems中的Internet Explorer 11,Windows 10 Version 2004 for 32-bit Systems中的Internet Explorer 11,Windows 10 Version 1903 for ARM64-based Systems中的Internet Explorer 11,Windows 10 Version 1903 for x64-based Systems中的Internet Explorer 11,Windows 10 Version 1903 for 32-bit Systems中的Internet Explorer 11,Windows 10 Version 1909 for ARM64-based Systems中的Internet Explorer 11,Windows 10 Version 1909 for x64-based Systems中的Internet Explorer 11,Windows 10 Version 1909 for 32-bit Systems中的Internet Explorer 11,Windows Server 2019中的Internet Explorer 11,Windows 10 Version 1809 for x64-based Systems中的Internet Explorer 11,Windows 10 Version 1809 for 32-bit Systems中的Internet Explorer 11,Windows 10 Version 1803 for ARM64-based Systems中的Internet Explorer 11,Windows 10 Version 1803 for x64-based Systems中的Internet Explorer 11,Windows 10 Version 1803 for 32-bit Systems中的Internet Explorer 11。

'''