"""Wrappers around Python 3 Requests library.

This lib will log errors, warnings and request duration, not raising any
exception: in such error cases, an empty dict is returned. To identify, if
necessary, that there where errors, a with_error flag must be set in the
arguments so that the methods return a tuple in the form of
(response_data: any, error: bool).

If there's any response expected from the endpoint, it will be returned
JSON-converted as-is, which means it's either valid JSON (string, number,
list, dict) or an empty dict (default response value, which is still valid
JSON).

"""

import asyncio
import functools
import logging
from time import time
from typing import NamedTuple
from typing import Optional
from typing import Union

import requests

__version__ = '0.4.0'
__author__ = 'HacKan (https://hackan.net)'
__license__ = 'GPL-3+'

logger = logging.getLogger(__name__)

VERIFY_SSL: bool = True
TJSONData = Optional[Union[dict, list, int, str]]


class SimpleResponse(NamedTuple):
    """Simple response class."""

    response: requests.Response
    error: bool


class SimpleDataResponse(NamedTuple):
    """Simple data response class."""

    response_data: TJSONData
    error: bool


class SimpleRequest:
    """Wrapper over requests lib that catches and logs errors and connection times."""

    @staticmethod
    def request(method: str, url: str, *, timeout: Union[int, float],
                **kwargs) -> SimpleResponse:
        """Make a request to an endpoint, return the response if any.

        Request time, errors and exceptions are all logged using the standard
        logger.

        :param method: The request method as string, such as GET, POST, PUT, etc.
        :param url: Endpoint URL as string.
        :param timeout: Connection timeout in seconds (0 for inf).
        :return: An object with the response (if any) and a bool representing
                 the occurrence of an error.
        """
        error = False
        response = None
        if timeout > 0:
            kwargs['timeout'] = timeout
        if 'verify' not in kwargs:
            kwargs['verify'] = VERIFY_SSL
        request_time_start = time()
        try:
            response = requests.request(method, url, **kwargs)
            request_time_end = time()
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout):
            request_time_end = time()
            logger.exception(
                'Error [%s]ing data (kwargs: %s) to/from the endpoint (url: %s)',
                method,
                str(kwargs),
                url,
            )
            error = True
        else:
            if not response.ok:
                logger.warning(
                    'Response from endpoint %s (kwargs: %s) is NOT OK: %d %s',
                    url,
                    str(kwargs),
                    response.status_code,
                    response.text,
                )
        logger.debug(
            'Request to endpoint %s took %.2f seconds',
            url,
            request_time_end - request_time_start,
        )

        return SimpleResponse(response, error)


class JSONConnectorAsync:
    """Generic requests wrapper class to handle JSON endpoints asynchronously."""

    @staticmethod
    async def request(method: str, url: str, *, timeout: Union[int, float],
                      **kwargs) -> SimpleDataResponse:
        """Make a request to a JSON endpoint, return the JSON converted response if any.

        Request time, errors and exceptions are all logged using the standard
        logger.

        Note that the type of the returned response depends on the endpoint,
        but it will always be some valid JSON.

        To know whether an error occurred or not check the error property of the
        return value.

        :param method: The request method as string, such as GET, POST, PUT, etc.
        :param url: Endpoint URL as string.
        :param timeout: Connection timeout in seconds (0 for inf).
        :return: An object with the response data (if any) and a bool representing
                 the occurrence of an error.
        """
        response_data = None
        kwargs['headers'] = {
            'content-type': 'application/json',
        }
        loop = asyncio.get_running_loop()
        response, error = await loop.run_in_executor(None, functools.partial(
            SimpleRequest.request,
            method,
            url,
            timeout=timeout,
            **kwargs,
        ))
        if not error and response.ok:
            try:
                response_data = response.json()
            except ValueError:
                if response.text:  # Could be an empty response
                    logger.warning(
                        'Response from endpoint %s is not valid JSON: %d %s',
                        url,
                        response.status_code,
                        response.text,
                    )
        return SimpleDataResponse(response_data, error)

    @classmethod
    async def get(cls, url: str, *, timeout: Union[int, float],
                  **kwargs) -> SimpleDataResponse:
        """Retrieve data from a JSON endpoint, return the JSON converted response if any.

        Request time, errors and exceptions are all logged using the standard
        logger.

        Note that the type of the returned response depends on the endpoint,
        but it will always be some valid JSON.

        To know whether an error occurred or not check the error property of the
        return value.

        :param url: Endpoint URL as string.
        :param timeout: Connection timeout in seconds (0 for inf).
        :return: An object with the response data (if any) and a bool representing
                 the occurrence of an error.
        """
        return await cls.request('GET', url, timeout=timeout, **kwargs)

    @classmethod
    async def post(cls, url: str, data: Union[str, dict, bytes, list, tuple],
                   *, timeout: Union[int, float], **kwargs) -> SimpleDataResponse:
        """Post data to a JSON endpoint, return the JSON converted response if any.

        If given data is a string, it will be previously encoded as if it were UTF-8.
        It is recommended to not send strings but encoded ones as bytes.

        Request time, errors and exceptions are all logged using the standard
        logger.

        Note that the type of the returned response depends on the endpoint,
        but it will always be some valid JSON.

        To know whether an error occurred or not check the error property of the
        return value.

        :param url: Endpoint URL as string.
        :param data: Data to post, either as a dictionary (JSON valid) or a string.
        :param timeout: Connection timeout in seconds (0 for inf).
        :return: An object with the response data (if any) and a bool representing
                 the occurrence of an error.
        """
        if isinstance(data, (dict, list, tuple)):
            return await cls.request('POST', url, timeout=timeout, json=data, **kwargs)
        elif isinstance(data, str):
            data = data.encode()
        return await cls.request('POST', url, timeout=timeout, data=data, **kwargs)
