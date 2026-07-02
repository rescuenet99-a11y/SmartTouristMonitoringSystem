from geopy.distance import geodesic

RISK_ZONES = [

{
"name":"Restricted Forest",
"lat":13.0840,
"lng":80.2740,
"radius":300,
"risk":"HIGH"
},

{
"name":"River Side",
"lat":13.0860,
"lng":80.2760,
"radius":200,
"risk":"MEDIUM"
}

]


def check_risk_zone(latitude, longitude):

    current = (latitude, longitude)

    for zone in RISK_ZONES:

        d = geodesic(
            current,
            (zone["lat"],zone["lng"])
        ).meters

        if d <= zone["radius"]:

            return zone

    return {
        "risk":"LOW",
        "name":"Safe Area"
    }