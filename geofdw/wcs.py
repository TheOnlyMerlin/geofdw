"""
:class:`WCS` is a WebCoverageService foreign data wrapper.
"""

from utils import *
import requests

XML = """<?xml version="1.0" encoding="UTF-8"?>
<GetCoverage version="1.0.0" service="WCS" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.opengis.net/wcs" xmlns:ows="http://www.opengis.net/ows/1.1" xmlns:gml="http://www.opengis.net/gml" xmlns:ogc="http://www.opengis.net/ogc" xsi:schemaLocation="http://www.opengis.net/wcs http://schemas.opengis.net/wcs/1.0.0/getCoverage.xsd">
  <sourceCoverage>$LAYER</sourceCoverage>
  <domainSubset>
    <spatialSubset>
      <gml:Envelope srsName="$CRS">
        <gml:pos>$MINX $MINY</gml:pos>
        <gml:pos>$MAXX $MAXY</gml:pos>
      </gml:Envelope>
      <gml:Grid dimension="2">
        <gml:limits>
          <gml:GridEnvelope>
            <gml:low>0 0</gml:low>
            <gml:high>$WIDTH $HEIGHT</gml:high>
          </gml:GridEnvelope>
        </gml:limits>
        <gml:axisName>x</gml:axisName>
        <gml:axisName>y</gml:axisName>
      </gml:Grid>
    </spatialSubset>
  </domainSubset>
  <rangeSubset>
    <axisSubset name="Band">
    <singleValue>$BAND</singleValue>
    </axisSubset>
  </rangeSubset>
  <output>
    <crs>$CRS</crs>
    <format>ArcGrid</format>
  </output>
</GetCoverage>
"""

class WCS(GeoRasterForeignDataWrapper):
  def __init__(self, options, columns):
    super(WCS, self).__init__(options, columns)    
    version = options.get('version', '1.0.0')
    layer = options.get('layer')
    width = str(options.get('width', 512))
    height = str(options.get('height', 512))
    band = str(options.get('band', 1))
    self.crs = options.get('crs')
    self.srid = self.crs_to_srid(self.crs)
    self.xml = XML.replace('$LAYER', layer).replace('$CRS', self.crs).replace('$HEIGHT', height).replace('$WIDTH', width).replace('$BAND', band)
    self.url = options.get('url')
    self.headers = {'content-type': 'text/xml', 'Accept-Encoding': 'text' }

  def execute(self, quals, columns):
    minx = str(0)
    miny = str(0)
    maxx = str(60)
    maxy = str(60)
    bbox = (minx, miny, maxx, maxy)
    
    xml = self.xml.replace('$MINX', bbox[0]).replace('$MINY', bbox[1]).replace('$MAXX', bbox[2]).replace('$MAXY', bbox[3])
    req = requests.post(self.url, headers=self.headers, data=xml)
    if req.status_code == 200:
      grid = req.text
      return self.grid_to_wkb(grid)
    else:
      return None

  def create_wkb(self, minx, miny, maxx, maxy, grid):
    #return  [ { 'rast' : '0100000200E80000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000' } ]