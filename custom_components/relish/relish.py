"""API module."""

import asyncio
from dataclasses import dataclass
from datetime import date, timedelta
import re
from urllib.parse import parse_qs, urlparse

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag


@dataclass
class RelishChild:
    """Child class."""

    name: str
    iac: str
    r: str
    account_balance: float
    meal_today: str
    pudding_today: str
    meal_tomorrow: str
    pudding_tomorrow: str


class RelishAPI:
    """API class to interact with relish."""

    def __init__(
        self, email: str, password: str, host: str, session: ClientSession
    ) -> None:
        """Create API object."""
        self._email = email
        self._password = password
        self._host = host
        self._session = session

    async def get_data(self) -> dict[str, RelishChild]:
        """Login to service."""
        children: dict[str, RelishChild] = {}
        children_details = await self.get_children_details()
        for name, details in children_details.items():
            iac = details["iac"]
            r = details["r"]
            main_meal, pudding, acc_balance = await self.get_current_details(iac, r)

            tomorrow = date.today() + timedelta(days=1)
            meal_tomorrow, pudding_tomorow = await self.get_meal_for_date(
                iac, r, tomorrow
            )

            children[iac] = RelishChild(
                name=name,
                iac=iac,
                r=r,
                account_balance=acc_balance,
                meal_today=main_meal,
                pudding_today=pudding,
                meal_tomorrow=meal_tomorrow,
                pudding_tomorrow=pudding_tomorow,
            )
        return children

    async def get_children_details(self):
        """Get children details."""
        pattern = re.compile(f"{self._host}/pupils.php\\?act=")

        payload = {"email": self._email, "password": self._password}
        resp = await self._session.post(
            url=f"{self._host}/prntsauthlogin.php", data=payload
        )
        soup = BeautifulSoup(await resp.read(), "html.parser")
        links = soup.find_all("a", href=pattern)
        children: dict[str, dict[str, str]] = {}
        for link in links:
            if not isinstance(link, Tag):
                raise TypeError("Error parsing link %s", str(link))
            href: str = str(link["href"])
            up = urlparse(href)
            q = parse_qs(up.query)
            iac = q.get("iac", {})[0]
            r = q.get("r", {})[0]
            name = link.text
            children[name] = {"iac": iac, "r": r}
        return children

    async def get_current_details(self, iac: str, r: str) -> tuple[str, str, float]:
        """Get details of current day and account balance."""
        resp = await self._session.get(
            url=f"{self._host}/pupils.php?act=2t&iac={iac}&r={r}"
        )
        soup = BeautifulSoup(await resp.read(), "html.parser")
        today_meal_details = soup.select("div.col-sm-2:has(> h4.purple + p)")
        main_meal: str = "None Selected"
        filling: str | None = None
        pudding: str = "None Selected"
        if today_meal_details:
            for today_meal in today_meal_details:
                meal_type = today_meal.find("h4")
                meal_value = today_meal.find("p")
                if not (meal_type and meal_value):
                    continue
                if meal_type.text == "Main Meal:":
                    main_meal = meal_value.text
                elif meal_type.text == "Filling:":
                    filling = meal_value.text
                elif meal_type.text == "Pudding:":
                    pudding = meal_value.text
                else:
                    raise ValueError("Unexpected meal type %s", str(meal_type))
        acc_balance = soup.select_one("h3:-soup-contains('Account Balance') + p + h4")
        if not acc_balance:
            raise ValueError("No account balance")
        if filling:
            main_meal = f"{main_meal} ({filling})"
        return (
            re.sub(r"\s\(\)$", "", main_meal),
            re.sub(r"\s\(\)$", "", pudding),
            float(re.sub(r"[^\d.]", "", acc_balance.text)),
        )

    async def get_meal_for_date(self, iac: str, r: str, meal_date: date):
        """Get meal details for give date."""
        main_meal = "None Selected"
        pudding = "None Selected"
        payload = {
            "san": 1,
            "dt": meal_date.strftime("%Y-%m-%d"),
            "icc": iac,
            "ipc": r,
        }
        resp = await self._session.post(
            url=f"{self._host}/pupilmealselctor2_2022.php", data=payload
        )
        soup = BeautifulSoup(await resp.read(), "html.parser")
        meal_details = soup.select("li > small > a")
        if meal_details:
            main_meal = meal_details[0].text.strip()
            pudding = meal_details[len(meal_details) - 1].text.strip()
            if len(meal_details) == 3:
                main_meal = f"{main_meal} ({meal_details[1].text.strip()})"

        return main_meal, pudding


# async def main():
#     """Run the test."""
#     r = RelishAPI(
#         "<email>",
#         "<password>",
#         "https://atlp.relishops.com/parents",
#         ClientSession(),
#     )
#     cs = await r.get_data()
#     for c in cs:
#         print(cs[c])


# asyncio.run(main())
