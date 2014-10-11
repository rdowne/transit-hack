import os
import bs4
import json
import shapely
import shapely.geometry

with open('example.sfmta.geo.json') as jsonin:
    geomess = json.loads( jsonin.read() )

def dictify_xmlline(filename):
    with open(filename) as xmlin:
        soup = bs4.BeautifulSoup( xmlin, 'xml' )

    samples = [ { a: l[a] for a in l.attrs } for l in soup.find_all('vehicle') ]
    return samples

routes = { f['properties']['shortName'].strip(): f['geometry']['geometries'] for f in geomess['features'] }

for k in routes.keys():
    new_routes = []

    for r in routes[k]:
        seglist = [ shapely.geometry.LineString( p ) for p in r['coordinates'] ]
        new_routes.append( shapely.geometry.MultiLineString( seglist ) )
    
    routes[k] = new_routes

route_filehandles = { k: open('./routes/%s.json' % k, 'w') for k in routes.keys() }

for root, dirs, files in os.walk('./sf-muni'):
    for f in files:
        ts = os.path.basename(f).split('.')[0]
        ts_list = dictify_xmlline( os.path.join( root, f ) )

        for sample in ts_list:
            sample['time'] = ts
            try:
                routeNo = sample.pop('routeTag').replace('_','-')
                route_filehandles[ routeNo ].write( json.dumps( sample ) + '\n' )
            except Exception as e:
                print( "Route %s does not exist: %s" % (routeNo, str(e)) )
        
for fh in route_filehandles:
    fh.close()
    
for k in routes.keys():
    with open('./routes/%s.json' % k) as linesin:
        samples = [ json.loads(l) for l in linesin.readlines() ]
