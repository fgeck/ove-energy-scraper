import re
import requests
from bs4 import BeautifulSoup

url = "https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx"
VIEWSTATE = '__VIEWSTATE'
EVENTVALIDATION = '__EVENTVALIDATION'


session = requests.Session()
getLoginPageResponse = session.get(url)
soup = BeautifulSoup(getLoginPageResponse.text, 'html.parser')
viewstateValue = soup.findAll('input', type='hidden', id=VIEWSTATE)[0].attrs['value']
eventvalidationValue = soup.findAll('input', type='hidden', id=EVENTVALIDATION)[0].attrs['value']


query_params = {
    'TestingCookie': 'true',
    'ReturnUrl': '/SEM.Portal.OVE/Default.aspx',
    '__VIEWSTATE': viewstateValue,
    '__EVENTVALIDATION': eventvalidationValue
}

form_data = {
    'Login1$UserName': '',
    'Login1$Password': '',
    'Login1$LoginButton': 'Anmelden'
}

cookies = {
    'ASP.NET_SessionId': '4fluvfnz3pl5di4h0xamejgr',
}

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-GB,en;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'https://sem01.dvs.net',
    'Referer': 'https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx?TestingCookie=true&ReturnUrl=%2fSEM.Portal.OVE%2fHelp.aspx',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
}

data = {
   # 'RadStyleSheetManager1_TSSM': ';Telerik.Web.UI, Version=2012.3.1308.40, Culture=neutral, PublicKeyToken=121fae78165ba3d4:de-DE:0c62baaa-fecc-4eb5-91ff-e3de59bf8f40:ef4a543:67d175d:92753c09:91f742eb',
   # 'RadScriptManager1_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:de-DE:c7c66246-7597-47ee-87ae-ac254004a457:ea597d4b:b25378d2;Telerik.Web.UI:de-DE:0c62baaa-fecc-4eb5-91ff-e3de59bf8f40:16e4e7cd:f7645509:22a6274a:ed16cbdc:86526ba7:874f8ea2:24ee1bba:f46195d3:19620875:490a9d4e:bd8f85e4',
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': '',
    '__VIEWSTATE': viewstateValue,
    '__EVENTVALIDATION': eventvalidationValue,
    'RadFormDecorator1_ClientState': '',
    'RadWindowManager1_ClientState': '',
    'Login1$UserName': '',
    'Login1$Password': '',
    'Login1$LoginButton': 'Anmelden',
}

response = session.post(
    'https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx',
    params=query_params,
    cookies=getLoginPageResponse.cookies,
    headers=headers,
    data=data,
    allow_redirects=True
)

# Prints the HTTP response code
print(response.status_code)

with open('result.html', 'w') as f:
    f.write(response.text)

soup = BeautifulSoup(response.text, 'html.parser')

allGaugeDivs = soup.findAll('div', class_='gaugelabel')

def getConsumptionFromText(text: str) -> float:
    match = re.search(r'Wert: (\d+(,\d+)?)', text)
    if match:
        return float(match.group(1).replace(',', '.'))


# electricity
electricityLastMonth = getConsumptionFromText(allGaugeDivs[0].text)
electricityThisMonth = getConsumptionFromText(allGaugeDivs[1].text)
# heat
heatLastMonth = getConsumptionFromText(allGaugeDivs[2].text)
heatThisMonth = getConsumptionFromText(allGaugeDivs[3].text)
# water
waterLastMonth = getConsumptionFromText(allGaugeDivs[4].text)
waterThisMonth = getConsumptionFromText(allGaugeDivs[5].text)

print(
    f"""
    Consumption Report from OVE
    ----------------------------
    Electricity:
    ------------
    Last month: {electricityLastMonth} kWh
    This month: {electricityThisMonth} kWh
            
    ----------------------------
    HEATING:
    ------------
    Last month: {heatLastMonth} kWh
    This month: {heatThisMonth} kWh
    
    ----------------------------
    WATER:
    ------------
    Last month: {waterLastMonth} m³
    This month: {waterThisMonth} m³

    """
)