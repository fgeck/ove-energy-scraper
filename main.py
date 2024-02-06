import datetime
import re
import requests

from bs4 import BeautifulSoup
import hassapi as hass

ONE_HOUR = 60*60
OVE_URL = "https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx"
VIEWSTATE = '__VIEWSTATE'
EVENTVALIDATION = '__EVENTVALIDATION'

class OveConsumptionStats():
    def __init__(self, 
        electricityLastMonth: float,
        electricityThisMonth: float,
        heatLastMonth: float,
        heatThisMonth: float,
        waterLastMonth: float,
        waterThisMonth: float,
                 ) -> None:
        self.electricityLastMonth = electricityLastMonth
        self.electricityThisMonth = electricityThisMonth
        self.heatLastMonth = heatLastMonth
        self.heatThisMonth = heatThisMonth
        self.waterLastMonth = waterLastMonth
        self.waterThisMonth = waterThisMonth


class OveEnergyScraperAppDaemon(hass.Hass):
    def initialize(self):
        self.log("OVE Energy Scraper Started")
        self.run_in(self.update, 0)
        # Update every hour
        self.run_every(self.update, datetime.datetime.now(), ONE_HOUR*6)

    def update(self, kwargs):
        self.log("Updating OVE Energy Stats")
        stats = self.getStats()

        entityWaterThisMonth = "sensor.water_consumption_this_month"
        self.set_state(entityWaterThisMonth, state = stats.waterThisMonth, attributes={"device_class": "water", "unit_of_measurement": "m³", "state_class": "total_increasing", "friendly_name": "Water used - This Month"})
        #entityWaterLastMonth = "sensor.water_consumption_last_month"
        #self.set_state(entityWaterLastMonth, state = stats.waterLastMonth, attributes={"device_class": "water", "unit_of_measurement": "m³", "state_class": "total_increasing", "friendly_name": "Water used - Last Month"})
        entityHeatThisMonth = "sensor.heat_consumption_this_month"
        self.set_state(entityHeatThisMonth, state = stats.heatThisMonth, attributes={"device_class": "energy", "unit_of_measurement": "kWh", "state_class": "total_increasing", "friendly_name": "Heating used - This Month"})
        #entityHeatLastMonth = "sensor.heat_consumption_last_month"
        #self.set_state(entityHeatLastMonth, state = stats.heatLastMonth)
        entityElectricityThisMonth = "sensor.electricity_consumption_this_month"
        self.set_state(entityElectricityThisMonth, state = stats.electricityThisMonth, attributes={"device_class": "energy", "unit_of_measurement": "kWh", "state_class": "total_increasing", "friendly_name": "Electricity used - This Month"})
        self.log("Updated OVE Energy Stats")
        self.log(f"""
Electricity:
------------
Last month: {stats.electricityLastMonth} kWh
This month: {stats.electricityThisMonth} kWh
        
----------------------------
HEATING:
------------
Last month: {stats.heatLastMonth} kWh
This month: {stats.heatThisMonth} kWh

----------------------------
WATER:
------------
Last month: {stats.waterLastMonth} m3
This month: {stats.waterThisMonth} m3
----------------------------
""")


    def getStats(self) -> OveConsumptionStats:
        session = requests.Session()
        getLoginPageResponse = session.get(OVE_URL)
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


        # electricity
        electricityLastMonth = self.getConsumptionFromText(allGaugeDivs[0].contents[2])
        electricityThisMonth = self.getConsumptionFromText(allGaugeDivs[1].contents[2])
        # heat
        heatLastMonth = self.getConsumptionFromText(allGaugeDivs[2].contents[2])
        heatThisMonth = self.getConsumptionFromText(allGaugeDivs[3].contents[2])
        # water
        waterLastMonth = self.getConsumptionFromText(allGaugeDivs[4].contents[2])
        waterThisMonth = self.getConsumptionFromText(allGaugeDivs[5].contents[2])
        return OveConsumptionStats(
            electricityLastMonth,
            electricityThisMonth,
            heatLastMonth,
            heatThisMonth,
            waterLastMonth,
            waterThisMonth
        )


    def getConsumptionFromText(self, text: str) -> float:
        match = re.search(r'Wert: (\d+(,\d+)?)', text)
        if match:
            return float(match.group(1).replace(',', '.'))
        