import datetime
import re
import ssl

import httpx
from bs4 import BeautifulSoup
import hassapi as hass

ONE_HOUR = 60 * 60
OVE_URL = "https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx"
VIEWSTATE = "__VIEWSTATE"
EVENTVALIDATION = "__EVENTVALIDATION"
OVE_LOGIN_USERNAME = ""
OVE_LOGIN_USERNAME_PASSWORD = ""


def create_ssl_context():
    # Enforce TLS 1.2
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    # Setting the specific cipher suite
    context.set_ciphers("TLS_RSA_WITH_AES_256_GCM_SHA384")
    return context


class OveConsumptionStats:
    def __init__(
        self,
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
        self.run_every(self.update, datetime.datetime.now(), ONE_HOUR * 6)

    def update(self, kwargs):
        self.log("Updating OVE Energy Stats")
        stats = self.getStats()

        entityWaterThisMonth = "sensor.water_consumption_this_month"
        self.set_state(
            entityWaterThisMonth,
            state=stats.waterThisMonth,
            attributes={
                "device_class": "water",
                "unit_of_measurement": "m³",
                "state_class": "total_increasing",
                "friendly_name": "Water used - This Month",
            },
        )

        entityHeatThisMonth = "sensor.heat_consumption_this_month"
        self.set_state(
            entityHeatThisMonth,
            state=stats.heatThisMonth,
            attributes={
                "device_class": "energy",
                "unit_of_measurement": "kWh",
                "state_class": "total_increasing",
                "friendly_name": "Heating used - This Month",
            },
        )

        entityElectricityThisMonth = "sensor.electricity_consumption_this_month"
        self.set_state(
            entityElectricityThisMonth,
            state=stats.electricityThisMonth,
            attributes={
                "device_class": "energy",
                "unit_of_measurement": "kWh",
                "state_class": "total_increasing",
                "friendly_name": "Electricity used - This Month",
            },
        )

        self.log("Updated OVE Energy Stats")
        self.log(
            f"""
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
"""
        )

    def getStats(self) -> OveConsumptionStats:
        ssl_context = create_ssl_context()

        # Create an HTTPX client with the custom SSL context
        with httpx.Client(verify=ssl_context) as client:
            get_login_page_response = client.get(OVE_URL)
            soup = BeautifulSoup(get_login_page_response.text, "html.parser")
            viewstate_value = soup.find("input", type="hidden", id=VIEWSTATE).attrs[
                "value"
            ]
            eventvalidation_value = soup.find(
                "input", type="hidden", id=EVENTVALIDATION
            ).attrs["value"]

            data = {
                "__VIEWSTATE": viewstate_value,
                "__EVENTVALIDATION": eventvalidation_value,
                "Login1$UserName": OVE_LOGIN_USERNAME,
                "Login1$Password": OVE_LOGIN_USERNAME_PASSWORD,
                "Login1$LoginButton": "Anmelden",
            }

            response = client.post(
                url="https://sem01.dvs.net/SEM.Portal.OVE/Login.aspx",
                data=data,
                follow_redirects=True,
            )
            soup = BeautifulSoup(response.text, "html.parser")
            all_gauge_divs = soup.find_all("div", class_="gaugelabel")

            # electricity
            electricity_last_month = self.getConsumptionFromText(
                all_gauge_divs[0].contents[2]
            )
            electricity_this_month = self.getConsumptionFromText(
                all_gauge_divs[1].contents[2]
            )
            # heat
            heat_last_month = self.getConsumptionFromText(all_gauge_divs[2].contents[2])
            heat_this_month = self.getConsumptionFromText(all_gauge_divs[3].contents[2])
            # water
            water_last_month = self.getConsumptionFromText(
                all_gauge_divs[4].contents[2]
            )
            water_this_month = self.getConsumptionFromText(
                all_gauge_divs[5].contents[2]
            )
            return OveConsumptionStats(
                electricity_last_month,
                electricity_this_month,
                heat_last_month,
                heat_this_month,
                water_last_month,
                water_this_month,
            )

    def getConsumptionFromText(self, text: str) -> float:
        match = re.search(r"Wert: (\d+(,\d+)?)", text)
        if match:
            return float(match.group(1).replace(",", "."))
