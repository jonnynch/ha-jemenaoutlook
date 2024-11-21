# ha-jemenaoutlook

This is a [Home Assistant](https://home-assistant.io) sensor component to retrieve information from the [Jemena Electricity Outlook](https://electricityoutlook.jemena.com.au/) website, they are an electricity distributor within Victoria, Australia.

This component will retrieve your electricity usage details from their website, and only cover a limited area around the northern and north western suburbs of Melbourne, Victoria.

To use this component you will need to register for an account via the Electricity Outlook website.

If Jemena are not your electricity distributor then this will be of no use to you.

The component will only retrieve Yesterdays usage, which will also retrieve the previous days if you wish do do some other comparisions. It could easily be extended to retrieve weekly, monthly or seasonal figures as well. (I haven't got that far yet)

The component is based on an older version of the [Hydro-Québec](https://home-assistant.io/components/sensor.hydroquebec/) energy sensor which is part fo the standard Home Assistant components. Thank you to the writer of that component it helpd a lot.

This component is not endorsed by Jemena, nor have a I asked for their endorsement.

## Installing the component

Copy the files under custom_components/jemenaoutlook to it's own directory called jemenaoutlook within custom_components directory where the configuration for your installation of home assistant sits. 

The custom_components directory does not exist in default installation state and may need to be created.

```
<homeassistant-user-configuration-directory>/custom_components/jemenaoutlook/sensor.py
<homeassistant-user-configuration-directory>/custom_components/jemenaoutlook/__init__.py
<homeassistant-user-configuration-directory>/custom_components/jemenaoutlook/manifest.py
```
For me this is :-
```
/home/ha/.homeassistant/custom_components/jemenaoutlook/sensor.py
/home/ha/.homeassistant/custom_components/jemenaoutlook/__init__.py
/home/ha/.homeassistant/custom_components/jemenaoutlook/manifest.py
```

Or just use git to clone into a jemenaoutlook directory, when using this method make sure the user home-assistant is running as can read these files.
```
cd <homeassistant-user-configuration-directory>/custom_components
git clone https://github.com/mvandersteen/ha-jemenaoutlook.git
ln -s  ha-jemenaoutlook/custom_components/jemenaoutlook jemenaoutlook
```

## Configuring the sensor

It becomes UI config

\*** For the cost based variables to be reported correctly you must setup your account with your current tarrif from your electricity retailer. These values can be obtained from your latest electricity bill. 