import json
import requests
import datetime
import pytz
import os

from time import gmtime, strftime
import time

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

try:
	from inky.auto import auto
	import inky
	INKY=True
except:
	INKY=False

POSTCODE = "RG28"

my_path = os.path.dirname(os.path.realpath(__file__))

carbon_api = "https://api.carbonintensity.org.uk"
current_intensity = "/regional/postcode/{postcode}"
forecast = "/regional/intensity/{from_time}/fw24h/postcode/{postcode}"

utc_tz = pytz.timezone('UTC')
lnd_tz = pytz.timezone('Europe/London')

def get_forcast():
	r = requests.get(carbon_api+forecast.format(from_time=str(datetime.datetime.now().isoformat()), postcode=POSTCODE))
	if r.status_code == 200:
		data = r.json()
		forecast_data = []
		for info in data['data']['data']:
			forecast_data.append({'time':info['from'], 'index':info['intensity']['index'],'forecast':info['intensity']['forecast']})
		return forecast_data
	else:
		return None

def get_intensity():
	r = requests.get(carbon_api+current_intensity.format(postcode=POSTCODE))
	if r.status_code == 200:
		data = r.json()
		return data['data'][0]['data'][0]['intensity']
	else:
		return None

def draw_frame(draw):
	# Draw the top bar
	draw.rectangle((0, 0, 400, 300), fill="White")
	draw.rectangle((400, 35, 0, 0), fill ="Black")

	# Add the clock
	timeStr = strftime("%d/%m/%Y", time.localtime())
	draw.text((10, 10), timeStr, 0, fontSmall)

def draw_intensity(draw):
	intensity = get_intensity()
	delta = 67
	if intensity == None:
		return

	if "low" in intensity['index']:
		fill_colour = "Yellow"
	else:
		fill_colour = "White"

	draw.rectangle((400, delta*2+35, 0, 35), fill=fill_colour, outline=None)
	draw.text((10, 70), intensity['index'].title(), "Black", fontLarge, stroke_width=2)
	draw.text((280, 70), str(intensity['forecast']), "Black", fontLarge, stroke_width=2)

def draw_box(x, y, draw, info):

	delta = 67
	x += 1
	y += 1

	if "L" in info['index'] or info['lowest']==True:
		fill_colour = "Yellow"
	else:
		fill_colour = None

	draw.rectangle((delta*x, 35+delta*y, delta*(x-1), 35+delta*(y-1)), fill=fill_colour, outline='Black')
	draw.text((delta*(x-1)+15, 35+delta*(y-1)+5), info['time'], "Black", fontSmall, stroke_width=1)
	draw.text((delta*(x-1)+18, 35+delta*(y-1)+25), info['index'], "Black", fontSmall, stroke_width=1)
	draw.text((delta*(x-1)+20, 35+delta*(y-1)+45), str(info['forecast']), "Black", fontSmall, stroke_width=1)

def getIndex(intensity):
	if intensity > 380:
		return 'VH'
	elif intensity > 280:
		return 'H'
	elif intensity > 180:
		return 'M'
	elif intensity > 80:
		return 'L'
	else:
		return 'VL'

def merge_forcast(forcast_data):
	time_index = 0
	merged = []
	while time_index < len(forcast_data)-1:

		naive_time = datetime.datetime.strptime(forcast_data[time_index]['time'],"%Y-%m-%dT%H:%MZ")
		utc_time = utc_tz.localize(naive_time)
		lnd_time = utc_time.astimezone(lnd_tz)
		start_time = lnd_time.strftime("%H:%M")

		ave_first_half = int(( forcast_data[time_index]['forecast'] + forcast_data[time_index + 1]['forecast']) /2)  
		ave_second_half = int(( forcast_data[time_index+2]['forecast'] + forcast_data[time_index + 3]['forecast']) /2)  
		ave_forcast = int((ave_first_half+ave_second_half)/2)
		ave_index = getIndex(ave_first_half) + ' / ' + getIndex(ave_second_half)
		merged.append({'index':ave_index,'forecast':ave_forcast,'time': start_time,'lowest':False})
		time_index += 4
	lowest = 0
	i = 0
	for reading in merged:
		if reading['forecast'] < merged[lowest]['forecast']:
			lowest = i
		i += 1
	merged[lowest]['lowest'] = True
	return merged

def draw_forecast(draw):
	forcast_data = get_forcast()
	if forcast_data == None:
		return
	merged = merge_forcast(forcast_data)
	i = 0
	for y in range(2,4):
		for x in range(0,6):
			info = merged[i]
			draw_box(x,y,draw,info)
			i+=1
			
if __name__ == "__main__":
	image = Image.new("P", (400, 300))
	draw = ImageDraw.Draw(image)
	fontSmall = ImageFont.truetype (my_path+"/"+"Nunito-ExtraLight.ttf", 16)
	fontVerySmall = ImageFont.truetype(my_path+"/""Nunito-ExtraLight.ttf", 10)
	fontLarge = ImageFont.truetype (my_path+"/""Nunito-ExtraLight.ttf", 50)

	draw_frame(draw)
	draw_intensity(draw)
	draw_forecast(draw)

	if INKY:
		ink = auto()
		ink.set_border(inky.BLACK)
		ink.set_image(image)
		ink.show()
	else:
		 image.show()