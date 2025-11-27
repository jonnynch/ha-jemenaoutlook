# ha-jemenaoutlook
This is a [Home Assistant](https://home-assistant.io) sensor component to retrieve information from the [Jemena - My Portal](https://myportal.jemena.com.au/) website, they are an electricity distributor within Victoria, Australia.

This component will retrieve your electricity usage details from their website, and only cover a limited area around the northern and north western suburbs of Melbourne, Victoria.

To use this component you will need to register for an account via the My Portal website.

If Jemena are not your electricity distributor then this will be of no use to you.

The component will retrieve Last 3 days hourly usage. 

The component is forked from https://github.com/mvandersteen/ha-jemenaoutlook, which was originally for Jemena Outlook.
It has further developed to support UI configuration and Energy Dashboard.
Recently, it has redeveloped for the new jemena portal.

This component is not endorsed by Jemena, nor have a I asked for their endorsement.

## Installing the component

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=Jon&repository=https%3A%2F%2Fgithub.com%2Fjonnynch%2Fha-jemenaoutlook)

Use git to clone into a jemenaoutlook directory, when using this method make sure the user home-assistant is running as can read these files.
```
cd <homeassistant-user-configuration-directory>/custom_components
git clone https://github.com/jonnynch/ha-jemenaoutlook.git
ln -s  ha-jemenaoutlook/custom_components/jemenaoutlook jemenaoutlook
```

Or simply copy the whole repository into custom_components
Please make sure custom_components/jemenaoutlook/sensor.py exists.

## Configuring the sensor

It is now UI configured. After installing the component, you can add it via Home Assistant.

## Integrate with Energy Dashboard
Add "jemenaoutlook:consumption_usage" into the Grid consumption of Electricity grid
Add "jemenaoutlook:generation" into the Return to grid of Electricity grid (If any)
