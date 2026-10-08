#!/usr/bin/env python3

import subprocess
from datetime import datetime 


def sbas_list_from_date_pairs(date_pairs, geolist):
    """
        date_pairs: list of `d1_d2` strings (date is YYYYMMDD format)
        geolist: list of `.geo` filename strings, as from an original geolist (../S1A----.geo)

        Writes a new sbas_list from the date_pairs provided with temporal and spatial baselines, 
        reconciles the other `list` text files as used by $PROC_HOME (jdlist, intlist, unwlist, geolist)
    """

    # sort the date_pairs just in case
    date_pairs = sorted(date_pairs)

    # write intlist
    intlist = [pair + ".int" for pair in date_pairs]
    with open("intlist","w") as file:
        for item in intlist:
            file.write(f"{item}\n")

    # write unwlist
    unwlist = [pair + ".unw" for pair in date_pairs]
    with open("unwlist","w") as file:
        for item in unwlist:
            file.write(f"{item}\n")

    with open("geolist", "w") as file:
        for item in geolist:
            file.write(f"{item}\n")

    def extract_date(geo):
        idx = geo.find('20')
        return geo[idx:idx+8]
    
    # form the jdlist
    jdlist = []
    for geo in geolist:
        scenedate = extract_date(geo)
        jd = datetime.strptime(scenedate, '%Y%m%d').toordinal() + 1721424.5
        jdlist.append(float(jd))

    date_to_index = {extract_date(geo): idx for idx, geo in enumerate(geolist)}

    # loop through date pairs, find the geo indices, compute baselines, write sbas_list file
    with open("sbas_list", "w") as ftb:
        for pair in date_pairs:
            d1, d2 = pair.split("_")

            i = date_to_index.get(d1)
            j = date_to_index.get(d2)

            if i is None or j is None:
                print(f"Warning: could not find geo for pair {pair}, skipping")
                continue

            baseline2 = abs(jdlist[i] - jdlist[j])

            # spatial baseline estimator
            orbtimingi = geolist[i].strip().replace('geo', 'orbtiming')
            orbtimingj = geolist[j].strip().replace('geo', 'orbtiming')
            command = '$PROC_HOME/sentinel/geo2rdr/estimatebaseline ' + orbtimingi + ' ' + orbtimingj
            print(command)
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
            (baseline1, err) = proc.communicate()
            print(command, ' baseline1: ', str(baseline1, "UTF-8"))
            print(err)

            geostri = geolist[i]
            geostrj = geolist[j]
            ftb.write(geostrj + ' ' + geostri + ' ' + str(baseline2) + ' ' + str(baseline1, "UTF-8") )

    print("New sbas_list written")