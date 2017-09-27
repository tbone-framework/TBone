# Weather App


This is a small example to demonstrate model data serialization and asynchronous export methods.
It is a command-line tool which accepts `city` and `state` parameters and fetches real-time weather information.

```bash
    $ python main.app Seattle WA
    The current weather in Seattle WA is 19.06 celcius
```

The example defines a data model like so:

```python
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
```

This data model implements a nonblocking export method which fetches the city weather in real-time

To learn more about data serialization and export methods refer to the [documentation](http://tbone.readthedocs.io/data.html#export-methods)