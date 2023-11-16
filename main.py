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

data = {
    '__VIEWSTATE': viewstateValue,
    '__EVENTVALIDATION': eventvalidationValue,
    'Login1$UserName': 'D208735',
    'Login1$Password': '4Y^gZ.=',
    'Login1$LoginButton': 'Anmelden',
}

response = session.post(
    'https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx',
    data=data,
    allow_redirects=True
)
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