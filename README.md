# Jemena Portal Integration for Home Assistant

This is a [Home Assistant](https://home-assistant.io) sensor component to retrieve information from the [Jemena - My Portal](https://myportal.jemena.com.au/) website, they are an electricity distributor within Victoria, Australia.

To use this component you will need to register for an account via the My Portal website.

**If Jemena are not your electricity distributor then this will be of no use to you.**

The component was forked from https://github.com/mvandersteen/ha-jemenaoutlook, which was originally for Jemena Outlook.
It has further developed to support UI configuration and Energy Dashboard.
Recently, it has redeveloped for the new jemena portal.

This component is not endorsed by Jemena, nor have a I asked for their endorsement.

## Features

- Electricity usage monitoring
- Easy configuration through the UI
- Integration with Home Assistant Energy Dashboard

## Installation

### HACS (Recommended)

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=jonnynch&repository=ha-jemenaoutlook)

### Manual Installation

1. Copy the `custom_components/jemenaoutlook` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuring the sensor

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "Jemena Outlook"
4. Enter your credentials:
   - **username**: Your Jemena account email
   - **password**: Your Jemena account password
   - **backday**: The number of days to look back when loading data (default: 2)
5. Enter your Email Code received or Enter your OTP sensor configured

### About backday

The integration updates data every hour. Due to potential delays in the Jemena portal, you can configure how many days back to reload data on each cycle. For example:

- **backday = 2**: Every hour, the integration will reload data from 2 days ago to present
- This ensures you capture any delayed or updated data from the portal
- Recommended range: 2-5 days

### About OTP or OTP sensor configured

The API integration requries OTP token.

If OTP is provided, it can only be used within limited time (8 hours), reconfiguration will be required to resume the integration.

If OTP sensor is configured, it can retrieve the OTP automatically. It is done by creating IMAP entity and template sensor.

1. IMAP Entity
   - **Folder**: Inbox
   - **IMAP Search**: FROM no-reply-test@jemena.com.au
   - **Template to create custom event data**: `{{ text | regex_findall_index("([0-9]{6})")}}`
   - Please check [IMAP integration documentation](https://www.home-assistant.io/integrations/imap) for the details
2. Template sensors
   - configuration.yaml

     ```
     template: !include template.yaml
     ```

   - template.yaml
     ```
     - trigger:
         - platform: event
           event_type: imap_content
       sensor:
         - name: jemena_otp
           state: "{{ trigger.event.data.custom }}"
     ```

## Energy Dashboard Integration

To integrate with Home Assistant's Energy Dashboard:

1. Go to **Settings** → **Dashboards** → **Energy**
2. Click on **Electricity grid**
3. Under **Grid consumption**, add: `jemenaoutlook:consumption_usage`
4. Under **Return to grid** (if you have solar), add: `jemenaoutlook:generation`
5. Click **Save**

## Support

For issues and feature requests, please use the [GitHub issue tracker](https://github.com/jonnynch/ha-jemenaoutlook/issues).
