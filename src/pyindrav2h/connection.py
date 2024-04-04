import logging
import httpx
from typing import Text
from bs4 import BeautifulSoup as bs

from .exceptions import V2HException
from .exceptions import WrongCredentialsException
from .exceptions import TimeoutException

_LOGGER = logging.getLogger(__name__)

loginUrl = "https://smartportal.indra.co.uk"
apiBaseUrl = "https://api.indra.co.uk/api"

class Connection:
    def __init__(
        self, userEmail: Text = None, userPass: Text = None, timeout: int = 20
    ) -> None:
        """Initialize connection object."""
        self.timeout = timeout
        self.email = userEmail
        self.password = userPass
        self._headers = {"User-Agent": "Wget/1.14 (linux-gnu)"}
        self._xsrfToken = None
        self._bearerToken = None
        self._cookies = None
        _LOGGER.debug("New connection created")

    async def checkAPICreds(self):
        self._xsrfToken = await self.getXsrf(loginUrl)
        _LOGGER.debug(f"XSRF token: {self._xsrfToken}")
        self._bearerToken = await self.getAuth("POST", "/login")
        self._headers["Authorization"] = self._bearerToken
        succ = {'success': 'True'}
        if succ['success'] == False:
            raise WrongCredentialsException()
    
    async def send(self, method, url, json=None):
        # params = {'api_key': self.email, 'api_secret': self.password}
        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as httpclient:
            # theUrl = apiBaseUrl + url
            theUrl = url
            try:
                _LOGGER.debug(f"{method} {url} {theUrl}")
                response = await httpclient.request(method, theUrl, json=json)
            except httpx.ReadTimeout:
                raise TimeoutException()
            else:
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 202:
                    return True
                elif response.status_code == 401:
                    raise WrongCredentialsException()
                raise V2HException(response.status_code)
    
    async def get(self, url, data=None):
        url = apiBaseUrl + url
        return await self.send("GET", url, data)
    
    async def post(self, url, data=None):
        url = apiBaseUrl + url
        return await self.send("POST", url, data)
    
    async def getXsrf(self, url, method = "GET"):
        # loginResponse = await self.send("GET", url)
        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as httpclient:
            theUrl = url
            try:
                _LOGGER.debug(f"{method} {url} {theUrl}")
                response = await httpclient.request(method, theUrl)
            except httpx.ReadTimeout:
                raise TimeoutException()
            else:
                if response.status_code == 200:
                    htmlBody = response.content
                    self._cookies = response.cookies
                    soup = bs(htmlBody, "lxml")
                    return soup.find('input', {"name": "__RequestVerificationToken"})['value']
                elif response.status_code == 401:
                    raise WrongCredentialsException()
                raise V2HException(response.status_code)
    

    async def getAuth(self, method, url, json=None):
        data = {'user_email': self.email, 'user_password': self.password, '__RequestVerificationToken': self._xsrfToken}
        async with httpx.AsyncClient(
            headers=self._headers, timeout=self.timeout
        ) as httpclient:
            theUrl = loginUrl + url
            try:
                _LOGGER.debug(f"{method} {url} {theUrl}")
                response = await httpclient.post(theUrl, data=data, cookies=self._cookies, follow_redirects=True)
            except httpx.ReadTimeout:
                raise TimeoutException()
            else:
                if response.status_code == 200:
                    htmlBody = response.content
                    self._cookies = response.cookies
                    soup = bs(htmlBody, "lxml")
                    jwtToken = soup.find('input', {"name": "JWTToken"})
                    if jwtToken:
                        return jwtToken['value']
                    else:
                        raise WrongCredentialsException()

                    # _LOGGER.debug(f"RESPONSE: {response.text}")
                    # return response.json()
                elif response.status_code == 401:
                    raise WrongCredentialsException()
                raise V2HException(response.status_code)
