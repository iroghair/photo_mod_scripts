# Photo mod scripts

## interpolate_gps.py
I was using both my smartphone and DSLR to make pictures on my journeys, but the DSLR does not provide the GPS data in the EXIF tags. This script uses the smartphone pictures provided as a location source, and interpolates the GPS location data based on the time stamp of the un-tagged images, and writes this GPS data as EXIF tags.
It also maps the pictures and the route taken.
Should be cleaned up thoroughly...

## To do
Add scripts for the following steps:
[ ] Rename pictures based on datetime_original
[ ] Shift time by a number of seconds / provide 2 pictures that are taken at the same time
[ ] Map pictures onto a map
[ ] Select based on xmp files/ratings