#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
import math

# cat observasjoner.csv | python3 polarberegning.py -x 100 -y 100 -z 100 -i 0.239 -d ";" -r ST1 -rx 100.007 -ry 102.978 -rz 99.980

##
parser = argparse.ArgumentParser()

##  Kjent koordinat til totalstasjon:
parser.add_argument("-x", "--x",
                    help="Totalstasjonens X-posisjon (m)",
                    type=float, default=100)
parser.add_argument("-y", "--y",
                    help="Totalstasjonens Y-posisjon (m)",
                    type=float, default=100)
parser.add_argument("-z", "--z",
                    help="Totalstasjonens Z-posisjon (m)",
                    type=float, default=100)
parser.add_argument("-i", "--i",
                    help="Instrumenthoyde (m)",
                    type=float, default=0.239)

##  Ett annet kjentpunkt
parser.add_argument("-r", "--rst",
                    help="Navn på annet kjentpunkt",
                    type=str, default="ST1")
parser.add_argument("-rx", "--rx",
                    help="Referansepunktets X-posisjon (m)",
                    type=float, default=100.007)
parser.add_argument("-ry", "--ry",
                    help="Referansepunktets Y-posisjon (m)",
                    type=float, default=102.978)
parser.add_argument("-rz", "--rz",
                    help="Referansepunktets Z-posisjon (m)",
                    type=float, default=99.980)

## Andre parametere
parser.add_argument("-id", "--id",
                    help="Skilletegn for innput",
                    type=str, default=";")
parser.add_argument("-od", "--od",
                    help="Skilletegn for output",
                    type=str, default=";")
parser.add_argument("-g", "--g",
                    help="Gradesystem (gon er standard (200))",
                    type=int, default=200)
parser.add_argument("-des", "--des",
                    help="Antall desimaler (3 is default)",
                    type=int, default=3)


args = parser.parse_args()
##


## Funksjon for kvadranten!
def kvadrant_vinkel(dx, dy):
    import math
    # korrigerer vinkel etter kvadrantreglene
    
    phi = math.atan(dy/dx)
    
    if dx > 0 and dy > 0: # 1. kvadrant
        refkvadrant = 1
        # legger ikke til korreksjon
    elif dx < 0 and dy > 0: # 2. kvadrant
        phi += math.pi
        refkvadrant = 2
    elif dx < 0 and dy < 0: # 3. kvadrant
        phi += math.pi
        refkvadrant = 3
    elif dx > 0 and dy < 0: # 4. kvadrant
        phi += 2 * math.pi
        refkvadrant = 4

    return phi, refkvadrant

## Les inn data fra standard input
data = []

for nr, line in enumerate(sys.stdin):
    row = line.replace("\n","").split(args.id)
    if nr == 0:
        h = row # headers
    else:
        data.append(row)
        
        
    
# Definer X-aksen ved å regne ut orienteringsellementet
# Stedet mellom 1. og 4. kvadrant
for line in data:
    if line[0] == args.rst:
        delta_y = args.ry - args.y 
        delta_x = args.rx -  args.x 
        
        horisontalvinkel = float(line[h.index("HR")]) * (math.pi/args.g)
        
        # regn ut retningsvinkel
        retningsvinkel, refkvadrant = kvadrant_vinkel(delta_x, delta_y)
        
        
        # I hvilken kvadrant ligger den vilkårlige 0-vinkelen ?
        # Det er enkelt å finne ut i hvilken kvadrant den det andre kjentpunktet ligger i,
        # men vi vil vite hvilken kvadrant 0-retninga peker til.
        # Dette trenger vi å vite for å kunne tilføre korreksjoner etter kvadrantregelen.
        
        if (retningsvinkel - horisontalvinkel) < (- 2 * math.pi):
            # 2. kvadrant
            korreksjon = math.pi
            orienteringselement = retningsvinkel + horisontalvinkel + korreksjon
        elif (retningsvinkel - horisontalvinkel) < (- math.pi):
            # 3. kvadrant
            korreksjon = math.pi
            orienteringselement = retningsvinkel - horisontalvinkel + korreksjon
        elif (retningsvinkel - horisontalvinkel) < 0:
            #4. kvadrat
            korreksjon = 2 * math.pi
            orienteringselement = retningsvinkel - horisontalvinkel + korreksjon
        elif (retningsvinkel - horisontalvinkel) > 0:
            # 1. kvadrant
             orienteringselement = retningsvinkel + horisontalvinkel


## Opprett outputdata
ohead = "Navn;V;HR;d;sh;hdist;x;y;z".split(";") # out header
out_data = []

#print(data)

for line in data:
    obs_list = ["NA" for i in ohead]
    for nr, obs in enumerate(line):
        for header in h:
            if ohead[nr] == header:
                obs_list[ohead.index(header)] = obs
                
    out_data.append(obs_list)

#print(out_data)
# Regn ut horisontalavstander
for nr, line in enumerate(out_data):
    vertikalvinkel = float(line[ohead.index("V")])
    skraavstand = float(line[ohead.index("d")])
    
    # regn ut horisontalavstand
    horisontalavstand = skraavstand * math.sin( vertikalvinkel * (math.pi/args.g))
    
    # legg horisontalavstanden til datasettet
    out_data[nr][ohead.index("hdist")] = str(horisontalavstand)
    
# Regn ut koordinater
for nr, line in enumerate(out_data):
    horisontalavstand = float(line[ohead.index("hdist")])
    horisontalretning = float(line[ohead.index("HR")]) * (math.pi/args.g)
    vertikalvinkel = float(line[ohead.index("V")]) * (math.pi/args.g)
    instrumenthoyde = args.i
    siktehoyde = float(line[ohead.index("sh")])
    skraavasand = float(line[ohead.index("d")]) #¤ * (math.pi/args.g)
    

    # Regn ut kartesiske koordinater for x og y
    x = args.x + horisontalavstand * math.cos( horisontalretning + orienteringselement )
    y = args.y + horisontalavstand * math.sin( horisontalretning + orienteringselement ) 
    
    # Zenit har en vinkel på 0 gon kikkertstilling 1.
    # Nadir har en vinkel på 200 gon i kikkertstilling 1.
    # Dette er omvent i kikkertstilling 2.
    # Siden vi her jobber i kikkertstilling 1,
    # vil en vinkel på over 100 gon forteller oss at vi sikter nedover.
    # Dermed skal vi trekke fra høyden på den motstående kateten.
    
    # ved å bruke skraavasand og cosinus av vertikalvinkelen
    # regner vi ut z koordinatet
    z = args.z + skraavasand * math.cos(vertikalvinkel) + instrumenthoyde - siktehoyde

    
    # legg til verdier
    out_data[nr][ohead.index("x")] = str(x)
    out_data[nr][ohead.index("y")] = str(y)
    out_data[nr][ohead.index("z")] = str(z)


## Skriv ut resultat til standard output
## med korrekt antall desimaler
print(args.od.join(ohead))
for line in out_data:
    val_list = []
    for nr, val in enumerate(line):
        if nr == ohead.index("Navn"):
            val_list.append(val)
        else:
            
            val_list.append(str(round(float(val), args.des)))
            
    print(args.od.join(val_list))


