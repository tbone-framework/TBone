#!/usr/bin/env python
# encoding: utf-8


import asyncio
import aiohttp
import argparse
from tbone.data.models import Model
from tbone.data.fields import *


API_KEY = '<get your own key for free at openweathermap.org>'
QUERY_URL = 'http://api.openweathermap.org/data/2.5/forecast?appid={key}&q={city},{state}'


def k2c(t):
    return t - 273.15


def k2f(t):
    return (t * 9 / 5.0) - 459.67


class CityInfo(Model):
    city = StringField(required=True)
    state = StringField()

    @export
    async def current_weather(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(QUERY_URL.format(key=API_KEY, city=self.city, state=self.state)) as resp:
                if resp.status == 200:  # http OK
                    data = await resp.json()
                    return data['list'][0]['main']['temp']
                return None


async def get_weather_info(opts):
    city_info = CityInfo(opts.__dict__)
    ser = await city_info.to_data()
    print('The current weather in {0} {1} is {2} celcius'.format(
        ser['city'],
        ser.get('state', None),
        k2c(ser.get('current_weather', None))
    ))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('city')
    parser.add_argument('state')
    opts = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(get_weather_info(opts))
    loop.close()


if __name__ == "__main__":
    main()
