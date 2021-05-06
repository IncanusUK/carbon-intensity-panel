# Carbon Intensity Panel

UK Carbon Intensity Panel on an electronic display with low intensity highlighting.

![Carbon Intensity Panel](https://github.com/IncanusUK/carbon-intensity-panel/blob/main/display.jpg)

The display gives the current carbon intensity for electricity in gCO2e/kWh and an intensity index for a given region in the UK (based on postcode). It also displays the next 24 hours forecast from the National Grid ESO using the https://api.carbonintensity.org.uk/ API. 

The display will highlight the background (in yellow) if the current intensity is 'low' or 'very low' and also highlight the time in the forecast with the lowest intensity and any time that is 'low' or 'very low'.

The project uses the yellow/back/white variant of the 4.2 inch Inky wHAT e-paper display (https://shop.pimoroni.com/products/inky-what) and a Raspberry Pi (in my case a Raspberry Pi W but others should also work).

The only dependency is the Inky library and its dependencies, a simple install script for this can be found here https://get.pimoroni.com/inky.

The only modification required is to update the ```POSTCODE``` in the ```carbon_panel.py``` script to the first part of your own postcode. 

On my system I have the ```carbon_panel.py``` script run every 30 minutes using a cron job:
```
*/30 * * * * /usr/bin/python3 /home/pi/carbon-intensity-panel/carbon_panel.py
```
