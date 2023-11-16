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
    'Login1$UserName': '',
    'Login1$Password': '',
    'Login1$LoginButton': 'Anmelden',
}

response = session.post(
    url='https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx',
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
electricityLastMonth = getConsumptionFromText(allGaugeDivs[0].contents[2])
electricityThisMonth = getConsumptionFromText(allGaugeDivs[1].contents[2])
# heat
heatLastMonth = getConsumptionFromText(allGaugeDivs[2].contents[2])
heatThisMonth = getConsumptionFromText(allGaugeDivs[3].contents[2])
# water
waterLastMonth = getConsumptionFromText(allGaugeDivs[4].contents[2])
waterThisMonth = getConsumptionFromText(allGaugeDivs[5].contents[2])

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