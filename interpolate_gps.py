from pathlib import Path
from exif import Image
import datetime
import pandas as pd
import scipy as sp
from math import modf
from random import random
import folium

def GPS_to_decimal(GPS,ref) -> float:
    assert len(GPS)==3,'GPS needs to contain 3 values'
    assert ref in ['N','W','S','E'], 'Reference needs to be any of N,S,W,E'
    decimal = GPS[0] + GPS[1]/60 + GPS[2]/3600
    if ref in ['W','S']:
        return -decimal
    else:
        return decimal

def decimal_to_GPS(decim,keep_sign=False,coordinates='latitude') -> tuple:
    assert isinstance(decim,float),'Input requires a float'
    assert abs(decim)<=180,'Input requires to be between -180 and 180 degrees'
    assert coordinates in ['longitude','latitude'],'coordinates needs to be either longitude or latitude'
    
    if decim < 0:
        if keep_sign == False:
            decim = -decim
        if coordinates == 'latitude':
            ref = 'S'
        else:
            ref = 'W'
    else:
        if coordinates == 'latitude':
            ref = 'N'
        else:
            ref = 'E'
        
    rem,deg = modf(decim)
    rem,min = modf(rem*60)
    sec = rem*60
    GPS = (deg,min,sec)
    return GPS, ref
    # if ref in ['W','S']:
    # else:
    #     return decimal
# f_list_photo_smartphone = Path(r'./smartphone').glob('20220802_072*.jpg')

# for _ in range(10):
#     x = random()*10-5
#     gps = decimal_to_GPS(x)
#     gps = decimal_to_GPS(x)
#     print(x,gps)
    
# exit()


f_list_photo_smartphone = Path(r'./smartphone').glob('*.jpg')
f_list_photo_dslr = Path(r'./DSLR').glob('*.JPG')

fnames = []
latitude_deg = []
longitude_deg = []
timedata = []

for f in f_list_photo_smartphone:
    with open(f,'rb') as src:
        img = Image(src)
        print(img.list_all())
        # print(img['datetime_original'].split())
        # dt_orig = img['datetime_original'].split()
        # t_date = datetime.date.fromisoformat(dt_orig[0].replace(':','-'))
        # t_time = datetime.time.fromisoformat(dt_orig[1])
        try:
            datetime_original = datetime.datetime.strptime(img['datetime_original'], '%Y:%m:%d %H:%M:%S')
        except AttributeError:
            print(f'{src.name} has no time data')
            continue
        try:
            gpsdata = [img['gps_latitude'], img['gps_latitude_ref'], img['gps_longitude'], img['gps_longitude_ref']]
        except AttributeError:
            print(f'{src.name} has no coordinate data')
            continue
        
        fnames.append(src.name)
        timedata.append(int(datetime_original.timestamp()))
        latitude_deg.append(GPS_to_decimal(gpsdata[0],gpsdata[1]))
        longitude_deg.append(GPS_to_decimal(gpsdata[2],gpsdata[3]))
        # decim = GPS_to_decimal(gpsdata[0],gpsdata[1])
        # print(f'{gpsdata[0]} --> {decim} --> {decimal_to_GPS(decim)}')
        # exit()

df_src = pd.DataFrame({"filename":fnames,
                "date time":timedata,
                "gps lat":latitude_deg,
                "gps lon":longitude_deg})

interp_longitude = sp.interpolate.interp1d(df_src['date time'],df_src['gps lon'])
interp_latitude = sp.interpolate.interp1d(df_src['date time'],df_src['gps lat'])
        
route_coordinates = []
for _,point in df_src.iterrows():
    route_coordinates.append((point["gps lat"],point["gps lon"]))
# print(route_coordinates)

target_fnames = []
target_gps_longitude_dec = []
target_datetime_orig = []
target_gps_latitude_dec = []
target_gps_longitude_deg = []
target_gps_latitude_deg = []

for f in f_list_photo_dslr:
    with open(f,'rb') as src:
        img = Image(src)
        print(f'Working on image: {src.name}')
        try:
            datetime_original = datetime.datetime.strptime(img['datetime_original'], '%Y:%m:%d %H:%M:%S')
        except AttributeError:
            print(f'{src.name} has no time data, not processed')
            continue
        
        target_fnames.append(src.name)
        print(f'Original time: {datetime_original}')
        target_datetime_orig.append(datetime_original)
        print(f'Original time: {datetime_original.timestamp()}')
        longitude_dec = interp_longitude(datetime_original.timestamp())
        latitude_dec = interp_latitude(datetime_original.timestamp())
        longitude_deg = decimal_to_GPS(float(longitude_dec),coordinates='longitude')
        latitude_deg = decimal_to_GPS(float(latitude_dec),coordinates='latitude')
        print(f'New coordinates for {src.name}: {latitude_dec},{longitude_dec}, i.e. {latitude_deg}, {longitude_deg}')
        target_gps_latitude_dec.append(latitude_dec)
        target_gps_longitude_dec.append(longitude_dec)
        target_gps_latitude_deg.append(latitude_deg)
        target_gps_longitude_deg.append(longitude_deg)

df_target = pd.DataFrame({"filename":target_fnames,
                "date time":target_datetime_orig,
                "gps lat dec":target_gps_latitude_dec,
                "gps lon dec":target_gps_longitude_dec,
                "gps lat deg":target_gps_latitude_deg,
                "gps lon deg":target_gps_longitude_deg})

for _,record in df_target.iterrows():
    img = Image(record['filename'])
    print(img.list_all())
    img.gps_latitude_ref = record['gps lat deg'][1]
    img.gps_latitude = record['gps lat deg'][0]
    img.gps_longitude_ref = record['gps lon deg'][1]
    img.gps_longitude = record['gps lon deg'][0]
    fname = record['filename'].split('/')[1]
    print(fname)
    with open(f'MODIFIED/{fname}', 'wb') as new_image_file:
        new_image_file.write(img.get_file())

m = folium.Map(location=(df_src['gps lat'][0],df_src['gps lon'][0]),zoom_start=8)
folium.PolyLine(route_coordinates, tooltip="Coast").add_to(m)    

for _,new_marker in df_target.iterrows():
    html = f"""<img src=\"file:///home/ivo/Desktop/Canada%202022/{new_marker['filename']}\" >"""
    iframe = folium.IFrame(html=html, width=500, height=300)
    folium.Marker(
    location=[new_marker['gps lat dec'], new_marker['gps lon dec']],
    tooltip=new_marker['filename'],
    # popup=folium.Popup(html=iframe, max_width=500),
    icon=folium.Icon(icon="camera"),
    ).add_to(m)
    
m.save('test.html')
exit()