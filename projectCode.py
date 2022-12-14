from datetime import date
from typing import Optional


class ProjectCode:

    def __init__(self):
        self._natureCode: Optional[int] = None
        self._date: Optional[date] = None
        self._countryCode: Optional[int] = None
        self._name: Optional[str] = None
        self._runningNum: Optional[int] = None

    def set_nature_code(self, nature: int):
        self._natureCode = nature

    def set_date(self, d: date):
        self._date = d

    def set_country_code(self, country: int):
        self._countryCode = country

    def set_name(self, name: str):
        self._name = name

    def set_running_num(self, num: int):
        self._runningNum = num

    def get_details(self) -> str:
        reformatted_date = self._date.strftime("%d/%m/%y")

        return f"Nature of project: {self._natureCode}\n" \
               f"Date of project opening: {reformatted_date}\n" \
               f"Project country code: {self._countryCode}\n" \
               f"Project name/address: {self._name}\n" \
               f"Project running num: {self._runningNum}"

    def __str__(self):
        month = None
        year = None
        if self._date is not None:
            month = self._date.strftime("%m")
            year = self._date.strftime("%y")

        return f"{self._countryCode}-{self._natureCode}-{month}-{year}-{self._runningNum}"
