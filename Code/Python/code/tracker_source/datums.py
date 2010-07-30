#
# datums.py - v0.1 - GPS Datum conversions and calcultations
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#
# The UTM<->WGS84 calculations here are ported from javascript code
# by Charles L. Taylor, who has the following banner upon his webpage
# ( http://home.hiwaay.net/~taylorc/toolbox/geography/geoutm.html )
# regarding his code:
#
#    Programmers: The JavaScript source code in this document may be
#    copied and reused without restriction.
#


# Author(s):
#
#    Charles L. Taylor
#       Original Javascript version for UTM<->WGS84 calculations
#
#    Nick Burch
#       Distance and Bearing calculations (from geo_helper.py)
#
#    Mark Hurenkamp    Mark.Hurenkamp <at> xs4all.nl
#       Port javascript code to python for UTM<->WGS84 calculations
#       Port matlab code to python for RD<->WGS84 calculations
#

import math
deg2rad =  math.pi / 180
rad2deg = 180 /  math.pi
pi = math.pi
UTMScaleFactor = 0.9996;


def DegToRad (deg):
    return deg * deg2rad

def RadToDeg (rad):
    return rad * rad2deg

def GetDMSFromWgs84(lat,lon):
    latd = int(lat)
    lond = int(lon)
    latm = int((lat - latd) * 60)
    lonm = int((lon - lond) * 60)
    lats = ((lat - latd)*60 - latm) * 60
    lons = ((lon - lond)*60 - lonm) * 60
    return (latd,latm,lats),(lond,lonm,lons)

def GetWgs84FromDMS((latd,latm,lats),(lond,lonm,lons)):
    lat = latd + latm/60.0 + lats/3600.0
    lon = lond + lonm/60.0 + lons/3600.0
    return lat,lon


def GetDMFromWgs84(lat,lon):
    latd = int(lat)
    lond = int(lon)
    latm = (lat - latd) * 60.0
    lonm = (lon - lond) * 60.0
    return (latd,latm),(lond,lonm)

def GetWgs84FromDM((latd,latm),(lond,lonm)):
    lat = latd + latm/60.0
    lon = lond + lonm/60.0
    return lat,lon


# WGS84 to RD Calculation
# taken from http://www.gpsgek.nl/informatief/wgs84-rd-script.html
def GetRdFromWgs84(lat,lon):
    dF = 0.36 * (lat - 52.15517440)
    dL = 0.36 * (lon - 5.38720621)

    dX = (190094.945 * dL) + (-11832.228 * dF * dL) + (-144.221 * dF**2 * dL) + (-32.391 * dL**3) + (-0.705 * dF) \
       + (-2.340 * dF**3 * dL) + (-0.608 * dF * dL**3) + (-0.008 * dL**2) + (0.148 * dF**2 * dL**3)
    dY = (309056.544 * dF) + (3638.893 * dL**2) + (73.077 * dF**2 ) + (-157.984 * dF * dL**2) + (59.788 * dF**3 ) \
       + (0.433 * dL) + (-6.439 * dF**2 * dL**2) + (-0.032 * dF * dL) + (0.092 * dL**4) + (-0.054 * dF * dL**4)

    X = 155000 + int(dX)
    Y = 463000 + int(dY)
    return X,Y


# RD to WGS84 Calculation
# taken from http://www.gpsgek.nl/informatief/wgs84-rd-script.html
def GetWgs84FromRd(x,y):
    dX = (x - 155000) * 1.0e-5
    dY = (y - 463000) * 1.0e-5

    dN = (3235.65389 * dY) + (-32.58297 * dX**2) + (-0.2475 * dY**2) + (-0.84978 * dX**2 * dY) \
       + (-0.0655 * dY**3) + (-0.01709 * dX**2 * dY**2) + (-0.00738 * dX) + (0.0053 * dX**4) \
       + (-0.00039 * dX**2 * dY**3) + (0.00033 * dX**4 * dY) + (-0.00012 * dX * dY)
    dE = (5260.52916 * dX) + (105.94684 * dX * dY) + (2.45656 * dX * dY**2) + (-0.81885 * dX**3) \
       + (0.05594 * dX * dY**3) + (-0.05607 * dX**3 * dY) + (0.01199 * dY) + (-0.00256 * dX**3 * dY**2) \
       + (0.00128 * dX * dY**4) + (0.00022 * dY**2) + (-0.00022 * dX**2) + (0.00026 * dX**5)

    Latitude = 52.15517 + (dN / 3600)
    Longitude = 5.387206 + (dE / 3600)
    return Latitude,Longitude


sm_a = 6378137.0
sm_b = 6356752.314
sm_EccSquared = 6.69437999013e-03

def FootpointLatitude(y):
    #
    # Computes the footpoint latitude for use in converting transverse
    # Mercator coordinates to ellipsoidal coordinates.
    #
    # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    #   GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    #
    # Inputs:
    #   y - The UTM northing coordinate, in meters.
    #
    # Returns:
    #   The footpoint latitude, in radians.
    #

    # Precalculate n (Eq. 10.18) */
    n = (sm_a - sm_b) / (sm_a + sm_b)

    # Precalculate alpha_ (Eq. 10.22) */
    # (Same as alpha in Eq. 10.17) */
    alpha_ = ((sm_a + sm_b) / 2.0) \
            * (1 + (math.pow (n, 2.0) / 4) + (math.pow (n, 4.0) / 64))

    # Precalculate y_ (Eq. 10.23) */
    y_ = y / alpha_

    # Precalculate beta_ (Eq. 10.22) */
    beta_ = (3.0 * n / 2.0) + (-27.0 * math.pow (n, 3.0) / 32.0) \
            + (269.0 * math.pow (n, 5.0) / 512.0)

    # Precalculate gamma_ (Eq. 10.22) */
    gamma_ = (21.0 * math.pow (n, 2.0) / 16.0) \
            + (-55.0 * math.pow (n, 4.0) / 32.0)

    # Precalculate delta_ (Eq. 10.22) */
    delta_ = (151.0 * math.pow (n, 3.0) / 96.0) \
            + (-417.0 * math.pow (n, 5.0) / 128.0)

    # Precalculate epsilon_ (Eq. 10.22) */
    epsilon_ = (1097.0 * math.pow (n, 4.0) / 512.0)

    # Now calculate the sum of the series (Eq. 10.21) */
    result = y_ + (beta_ * math.sin (2.0 * y_)) \
            + (gamma_ * math.sin (4.0 * y_)) \
            + (delta_ * math.sin (6.0 * y_)) \
            + (epsilon_ * math.sin (8.0 * y_))

    return result


# MapXY to WGS84 Calculation
def GetWgs84FromMapXY(x,y,lambda0):
    #
    # MapXYToLatLon
    #
    # Converts x and y coordinates in the Transverse Mercator projection to
    # a latitude/longitude pair.  Note that Transverse Mercator is not
    # the same as UTM; a scale factor is required to convert between them.
    #
    # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    #   GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    #
    # Inputs:
    #   x - The easting of the point, in meters.
    #   y - The northing of the point, in meters.
    #   lambda0 - Longitude of the central meridian to be used, in radians.
    #
    # Returns:
    #   philambda - A 2-element containing the latitude and longitude
    #               in radians.
    #
    # Remarks:
    #   The local variables Nf, nuf2, tf, and tf2 serve the same purpose as
    #   N, nu2, t, and t2 in MapLatLonToXY, but they are computed with respect
    #   to the footpoint latitude phif.
    #
    #   x1frac, x2frac, x2poly, x3poly, etc. are to enhance readability and
    #   to optimize computations.
    #


    # Get the value of phif, the footpoint latitude. */
    phif = FootpointLatitude (y)

    # Precalculate ep2 */
    ep2 = (math.pow (sm_a, 2.0) - math.pow (sm_b, 2.0)) / math.pow (sm_b, 2.0)

    # Precalculate cos (phif) */
    cf = math.cos (phif)

    # Precalculate nuf2 */
    nuf2 = ep2 * math.pow (cf, 2.0)

    # Precalculate Nf and initialize Nfpow */
    Nf = math.pow (sm_a, 2.0) / (sm_b * math.sqrt (1 + nuf2))
    Nfpow = Nf

    # Precalculate tf */
    tf = math.tan (phif);
    tf2 = tf * tf;
    tf4 = tf2 * tf2;

    # Precalculate fractional coefficients for x**n in the equations
    # below to simplify the expressions for latitude and longitude. */
    x1frac = 1.0 / (Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**2) */
    x2frac = tf / (2.0 * Nfpow)

    Nfpow *= Nf    # now equals Nf**3) */
    x3frac = 1.0 / (6.0 * Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**4) */
    x4frac = tf / (24.0 * Nfpow)

    Nfpow *= Nf    # now equals Nf**5) */
    x5frac = 1.0 / (120.0 * Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**6) */
    x6frac = tf / (720.0 * Nfpow)

    Nfpow *= Nf    # now equals Nf**7) */
    x7frac = 1.0 / (5040.0 * Nfpow * cf)

    Nfpow *= Nf    # now equals Nf**8) */
    x8frac = tf / (40320.0 * Nfpow)

    # Precalculate polynomial coefficients for x**n.
    # -- x**1 does not have a polynomial coefficient. */
    x2poly = -1.0 - nuf2

    x3poly = -1.0 - 2 * tf2 - nuf2

    x4poly = 5.0 + 3.0 * tf2 + 6.0 * nuf2 - 6.0 * tf2 * nuf2 \
        - 3.0 * (nuf2 *nuf2) - 9.0 * tf2 * (nuf2 * nuf2)

    x5poly = 5.0 + 28.0 * tf2 + 24.0 * tf4 + 6.0 * nuf2 + 8.0 * tf2 * nuf2

    x6poly = -61.0 - 90.0 * tf2 - 45.0 * tf4 - 107.0 * nuf2 + 162.0 * tf2 * nuf2

    x7poly = -61.0 - 662.0 * tf2 - 1320.0 * tf4 - 720.0 * (tf4 * tf2)

    x8poly = 1385.0 + 3633.0 * tf2 + 4095.0 * tf4 + 1575 * (tf4 * tf2)

    # Calculate latitude */
    philambda0 = phif + x2frac * x2poly * (x * x) \
            + x4frac * x4poly * math.pow (x, 4.0) \
            + x6frac * x6poly * math.pow (x, 6.0) \
            + x8frac * x8poly * math.pow (x, 8.0)

    # Calculate longitude */
    philambda1 = lambda0 + x1frac * x \
            + x3frac * x3poly * math.pow (x, 3.0) \
            + x5frac * x5poly * math.pow (x, 5.0) \
            + x7frac * x7poly * math.pow (x, 7.0)

    return (RadToDeg(philambda0),RadToDeg(philambda1))



def UTMCentralMeridian(zone):
    #
    # Determines the central meridian for the given UTM zone.
    #
    # Inputs:
    #     zone - An integer value designating the UTM zone, range [1,60].
    #
    # Returns:
    #   The central meridian for the given UTM zone, in radians, or zero
    #   if the UTM zone parameter is outside the range [1,60].
    #   Range of the central meridian is the radian equivalent of [-177,+177].
    #
    return DegToRad (-183.0 + (zone * 6.0))


# UTM to WGS84 Calculation
def GetWgs84FromUTM(x,y,zone,southhemi):
    #
    # Converts x and y coordinates in the Universal Transverse Mercator
    # projection to a latitude/longitude pair.
    #
    # Inputs:
    #    x - The easting of the point, in meters.
    #    y - The northing of the point, in meters.
    #    zone - The UTM zone in which the point lies.
    #    southhemi - True if the point is in the southern hemisphere;
    #               false otherwise.
    #
    # Returns:
    #    latlon - A 2-element array containing the latitude and
    #            longitude of the point, in radians.
    #
    x -= 500000.0;
    x /= UTMScaleFactor

    # If in southern hemisphere, adjust y accordingly. */
    if (southhemi):
        y -= 10000000.0

    y /= UTMScaleFactor

    cmeridian = UTMCentralMeridian (zone)
    return GetWgs84FromMapXY (x, y, cmeridian)


def ArcLengthOfMeridian(phi):
    #
    # ArcLengthOfMeridian
    #
    # Computes the ellipsoidal distance from the equator to a point at a
    # given latitude.
    #
    # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    # GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    #
    # Inputs:
    #     phi - Latitude of the point, in radians.
    #
    # Globals:
    #     sm_a - Ellipsoid model major axis.
    #     sm_b - Ellipsoid model minor axis.
    #
    # Returns:
    #     The ellipsoidal distance of the point from the equator, in meters.
    #

    # Precalculate n */
    n = (sm_a - sm_b) / (sm_a + sm_b);

    # Precalculate alpha */
    alpha = ((sm_a + sm_b) / 2.0) \
           * (1.0 + (math.pow (n, 2.0) / 4.0) + (math.pow (n, 4.0) / 64.0))

    # Precalculate beta */
    beta = (-3.0 * n / 2.0) + (9.0 * math.pow (n, 3.0) / 16.0) \
         + (-3.0 * math.pow (n, 5.0) / 32.0)

    # Precalculate gamma */
    gamma = (15.0 * math.pow (n, 2.0) / 16.0) \
          + (-15.0 * math.pow (n, 4.0) / 32.0)

    # Precalculate delta */
    delta = (-35.0 * math.pow (n, 3.0) / 48.0) \
          + (105.0 * math.pow (n, 5.0) / 256.0)

    # Precalculate epsilon */
    epsilon = (315.0 * math.pow (n, 4.0) / 512.0)

    # Now calculate the sum of the series and return */
    result = alpha \
        * (phi + (beta * math.sin (2.0 * phi)) \
            + (gamma * math.sin (4.0 * phi)) \
            + (delta * math.sin (6.0 * phi)) \
            + (epsilon * math.sin (8.0 * phi)))

    return result


def GetXYFromWgs84(rlat,rlon,lambda0):
    #
    # MapLatLonToXY
    #
    # Converts a latitude/longitude pair to x and y coordinates in the
    # Transverse Mercator projection.  Note that Transverse Mercator is not
    # the same as UTM; a scale factor is required to convert between them.
    #
    # Reference: Hoffmann-Wellenhof, B., Lichtenegger, H., and Collins, J.,
    # GPS: Theory and Practice, 3rd ed.  New York: Springer-Verlag Wien, 1994.
    #
    # Inputs:
    #    rlat - Latitude of the point, in radians.
    #    rlon - Longitude of the point, in radians.
    #    lambda0 - Longitude of the central meridian to be used, in radians.
    #
    # Outputs:
    #    xy - A 2-element array containing the x and y coordinates
    #         of the computed point.
    #
    # Returns:
    #    The function does not return a value.
    #
    #
    #function MapLatLonToXY (rlat, rlon, lambda0, xy)

        # Precalculate ep2 */
        ep2 = (math.pow (sm_a, 2.0) - math.pow (sm_b, 2.0)) / math.pow (sm_b, 2.0)

        # Precalculate nu2 */
        nu2 = ep2 * math.pow (math.cos (rlat), 2.0)

        # Precalculate N */
        N = math.pow (sm_a, 2.0) / (sm_b * math.sqrt (1 + nu2))

        # Precalculate t */
        t = math.tan (rlat)
        t2 = t * t
        tmp = (t2 * t2 * t2) - math.pow (t, 6.0)

        # Precalculate l */
        l = rlon - lambda0

        # Precalculate coefficients for l**n in the equations below
        #  so a normal human being can read the expressions for easting
        #  and northing
        #  -- l**1 and l**2 have coefficients of 1.0 */
        l3coef = 1.0 - t2 + nu2

        l4coef = 5.0 - t2 + 9 * nu2 + 4.0 * (nu2 * nu2)

        l5coef = 5.0 - 18.0 * t2 + (t2 * t2) + 14.0 * nu2 \
            - 58.0 * t2 * nu2

        l6coef = 61.0 - 58.0 * t2 + (t2 * t2) + 270.0 * nu2 \
            - 330.0 * t2 * nu2

        l7coef = 61.0 - 479.0 * t2 + 179.0 * (t2 * t2) - (t2 * t2 * t2)

        l8coef = 1385.0 - 3111.0 * t2 + 543.0 * (t2 * t2) - (t2 * t2 * t2)

        # Calculate easting (x) */
        x = N * math.cos (rlat) * l \
            + (N / 6.0 * math.pow (math.cos (rlat), 3.0) * l3coef * math.pow (l, 3.0)) \
            + (N / 120.0 * math.pow (math.cos (rlat), 5.0) * l5coef * math.pow (l, 5.0)) \
            + (N / 5040.0 * math.pow (math.cos (rlat), 7.0) * l7coef * math.pow (l, 7.0))

        # Calculate northing (y) */
        y = ArcLengthOfMeridian (rlat) \
            + (t / 2.0 * N * math.pow (math.cos (rlat), 2.0) * math.pow (l, 2.0)) \
            + (t / 24.0 * N * math.pow (math.cos (rlat), 4.0) * l4coef * math.pow (l, 4.0)) \
            + (t / 720.0 * N * math.pow (math.cos (rlat), 6.0) * l6coef * math.pow (l, 6.0)) \
            + (t / 40320.0 * N * math.pow (math.cos (rlat), 8.0) * l8coef * math.pow (l, 8.0))

        return x,y

# WGS84 to UTM Calculation
def GetUTMFromWgs84(lat,lon,zone=0):
    #
    # LatLonToUTMXY
    #
    # Converts a latitude/longitude pair to x and y coordinates in the
    # Universal Transverse Mercator projection.
    #
    # Inputs:
    #   lat - Latitude of the point, in radians.
    #   lon - Longitude of the point, in radians.
    #   zone - UTM zone to be used for calculating values for x and y.
    #          If zone is less than 1 or greater than 60, the routine
    #          will determine the appropriate zone from the value of lon.
    #
    # Outputs:
    #   xy - A 2-element array where the UTM x and y values will be stored.
    #
    # Returns:
    #   The UTM zone used for calculating the values of x and y.
    #
    #
    #function LatLonToUTMXY (lat, lon, zone, xy)

    if zone < 1 or zone > 60:
        zone = math.floor ((lon + 180.0) / 6) + 1

    rlat = lat /180 * math.pi
    rlon = lon /180 * math.pi
    x,y = GetXYFromWgs84 (rlat, rlon, UTMCentralMeridian(zone))

    # Adjust easting and northing for UTM system. */
    x = x * UTMScaleFactor + 500000.0
    y = y * UTMScaleFactor
    if (y < 0.0):
        y += 10000000.0

    return x,y,zone



def CalculateDistanceAndBearing(fromwgs,towgs):
    """Uses the spherical law of cosines to calculate the distance and bearing between two positions"""
    from_lat_dec  = fromwgs[0]
    from_long_dec = fromwgs[1]
    to_lat_dec    = towgs[0]
    to_long_dec   = towgs[1]

    # For each co-ordinate system we do, what are the A, B and E2 values?
    # List is A, B, E^2 (E^2 calculated after)
    abe_values = {
	    'wgs84': [ 6378137.0, 6356752.3141, -1 ],
	    'osgb' : [ 6377563.396, 6356256.91, -1 ],
	    'osie' : [ 6377340.189, 6356034.447, -1 ]
        }

    # The earth's radius, in meters, as taken from an average of the WGS84
    #  a and b parameters (should be close enough)
    earths_radius = (abe_values['wgs84'][0] + abe_values['wgs84'][1]) / 2.0

    # Turn them all into radians
    from_theta = float(from_lat_dec)  / 360.0 * 2.0 * math.pi
    from_landa = float(from_long_dec) / 360.0 * 2.0 * math.pi
    to_theta = float(to_lat_dec)  / 360.0 * 2.0 * math.pi
    to_landa = float(to_long_dec) / 360.0 * 2.0 * math.pi

    try:
        distance = math.acos(
                math.sin(from_theta) * math.sin(to_theta) +
                math.cos(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
		    ) * earths_radius
    except:
        distance = 0
        print "Exception while calculating distance in datums.py@358"

    bearing = math.atan2(
                math.sin(to_landa-from_landa) * math.cos(to_theta),
                math.cos(from_theta) * math.sin(to_theta) -
                math.sin(from_theta) * math.cos(to_theta) * math.cos(to_landa-from_landa)
            )
    bearing = bearing / 2.0 / math.pi * 360.0

    return distance, bearing % 360



Ellipsoid = {
        "Airy":(6377563, 0.00667054),
        "Australian National":(6378160, 0.006694542),
        "Bessel 1841":(6377397, 0.006674372),
        "Bessel 1841 Nambia":(6377484, 0.006674372),
        "Clarke 1866":(6378206, 0.006768658),
        "Clarke 1880":(6378249, 0.006803511),
        "Everest 1830 India":(6377276, 0.006637847),
        "Fischer 1960 Mercury":(6378166, 0.006693422),
        "Fischer 1968":(6378150, 0.006693422),
        "GRS 1967":(6378160, 0.006694605),
        "GRS 1980":(6378137, 0.00669438),
        "Helmert 1906":(6378200, 0.006693422),
        "Hough":(6378270, 0.00672267),
        "International":(6378388, 0.00672267),      # == Hayford ellipsoid
        "Krassovsky":(6378245, 0.006693422),
        "Modified Airy":(6377340, 0.00667054),
        "Modified Everest":(6377304, 0.006637847),
        "Modified Fischer 1960":(6378155, 0.006693422),
        "South American 1969":(6378160, 0.006694542),
        "WGS 60":(6378165, 0.006693422),
        "WGS 66":(6378145, 0.006694542),
        "WGS-72":(6378135, 0.006694318),
        "WGS-84":(6378137, 0.00669438 ),
        "Everest 1830 Malaysia":(6377299, 0.006637847),
        "Everest 1956 India":(6377301, 0.006637847),
        "Everest 1964 Malaysia and Singapore":(6377304, 0.006637847),
        "Everest 1969 Malaysia":(6377296, 0.006637847),
        "Everest Pakistan":(6377296, 0.006637534),
        "Indonesian 1974":(6378160, 0.006694609),
    }

def _valid_utm_zone(char):
    return (char in "CDEFGHJKLMNPQRSTUVWX")

# Expects Ellipsoid Name, Latitude, Longitude
# (Latitude and Longitude in decimal degrees)
# Returns UTM Zone, UTM Easting, UTM Northing
def latlon_to_utm(ellips,latitude,longitude):
    assert (longitude >= -180 and longitude <= 180), 'Invalid longitude %f' % longitude

    long2 = longitude - int((longitude + 180)/360) * 360
    zone  = _latlon_zone_number(latitude, long2)

    return _latlon_to_utm(ellips, zone, latitude, long2)



def latlon_to_utm_force_zone(ellips, zone, latitude, longitude):
    assert (longitude >= -180 and longitude <= 180), 'Invalid longitude %f' % longitude

    long2 = longitude - int((longitude + 180)/360) * 360

#    my ($zone_number) = $zone =~ /^(\d+)[CDEFGHJKLMNPQRSTUVWX]?$/i;
    assert (zone_number <= 60), 'Invalid zone %f' % zone_number

    return _latlon_to_utm(ellips, zone_number, latitude, long2)


def _latlon_zone_number(latitude,long2):
    zone = int( (long2 + 180)/6) + 1

    if (latitude >= 56.0 and latitude < 64.0 and long2 >= 3.0 and long2 < 12.0):
        zone = 32

    if latitude >= 72.0 and latitude < 84.0:
        if long2 >= 0.0 and long2 < 9.0:
            zone = 31
        elif long2 >= 9.0 and long2 < 21.0:
            zone = 33
        elif long2 >=21.0 and long2 < 33.0:
            zone = 35
        elif long2 >= 33.0 and long2 < 42.0:
            zone = 37

    return zone

def _latlon_to_utm(ellips, zone, latitude, long2):
    name = ellips
    try:
        radius, eccentricity = Ellipsoid[name]
    except:
        print "Failed to get ellipsoid %s, using International instead" % ellips
        radius, eccentricity = Ellipsoid["International"]

    lat_radian  = deg2rad * latitude;
    long_radian = deg2rad * long2;

    k0          = UTMScaleFactor

    longorigin       = (zone - 1)*6 - 180 + 3
    longoriginradian = deg2rad * longorigin
    eccentprime      = eccentricity/(1-eccentricity)

    N = radius / math.sqrt(1-eccentricity * math.sin(lat_radian)*math.sin(lat_radian));
    T = math.tan(lat_radian) * math.tan(lat_radian);
    C = eccentprime * math.cos(lat_radian)*math.cos(lat_radian);
    A = math.cos(lat_radian) * (long_radian - longoriginradian);
    M = radius \
            * ( ( 1 - eccentricity/4 - 3 * eccentricity * eccentricity/64 \
                  - 5 * eccentricity * eccentricity * eccentricity/256 \
                ) * lat_radian \
              - ( 3 * eccentricity/8 + 3 * eccentricity * eccentricity/32 \
                  + 45 * eccentricity * eccentricity * eccentricity/1024 \
                ) * math.sin(2 * lat_radian) \
              + ( 15 * eccentricity * eccentricity/256 + \
                  45 * eccentricity * eccentricity * eccentricity/1024 \
                ) * math.sin(4 * lat_radian) \
              - ( 35 * eccentricity * eccentricity * eccentricity/3072 \
                ) * math.sin(6 * lat_radian) \
              )

    utm_easting = k0*N*(A+(1-T+C)*A*A*A/6 \
                    + (5-18*T+T*T+72*C-58*eccentprime)*A*A*A*A*A/120) \
                    + 500000.0

    utm_northing= k0 * ( M + N*math.tan(lat_radian) * ( A*A/2+(5-T+9*C+4*C*C)*A*A*A*A/24 \
                    + (61-58*T+T*T+600*C-330*eccentprime) * A*A*A*A*A*A/720))

    if latitude <= 0:
        utm_northing += 10000000.0

    letters="CDEFGHJKLMNPQRSTUVWXX"
    i = int((latitude+80)/8)
    utm_letter = letters[i]
    if type(zone)==type("string"):
        zone = zone+utm_letter
    else:
        zone = str(zone)+utm_letter

    return zone, utm_easting, utm_northing



# Expects Ellipsoid Number or name, UTM zone, UTM Easting, UTM Northing
# Returns Latitude, Longitude
# (Latitude and Longitude in decimal degrees, UTM Zone e.g. 23S)
def utm_to_latlon(ellips, zone, easting, northing):
    name = ellips
    radius, eccentricity = Ellipsoid[name]

    zone_number = int(zone[:-1])
    zone_letter = zone[-1]

    assert _valid_utm_zone(zone_letter), "UTM zone %s invalid." % zone_letter

    k0 = UTMScaleFactor
    x  = easting - 500000
    y  = northing

    # Set hemisphere (1=Northern, 0=Southern)
    hemisphere = zone_letter >= 'N'
    if not hemisphere:
        y -= 10000000.0

    longorigin      = (zone_number - 1)*6 - 180 + 3
    eccPrimeSquared = (eccentricity)/(1-eccentricity)
    M  = y/k0
    mu = M/(radius*(1-eccentricity/4-3*eccentricity*eccentricity/64-5*eccentricity*eccentricity*eccentricity/256))

    e1 = (1-math.sqrt(1-eccentricity))/(1+math.sqrt(1-eccentricity))
    phi1rad = mu+(3*e1/2-27*e1*e1*e1/32)*math.sin(2*mu)+(21*e1*e1/16-55*e1*e1*e1*e1/32)*math.sin(4*mu)+(151*e1*e1*e1/96)*math.sin(6*mu)
    phi1 = phi1rad*rad2deg
    N1 = radius/math.sqrt(1-eccentricity*math.sin(phi1rad)*math.sin(phi1rad))
    T1 = math.tan(phi1rad)*math.tan(phi1rad)
    C1 = eccentricity*math.cos(phi1rad)*math.cos(phi1rad)
    R1 = radius * (1-eccentricity) / ((1-eccentricity*math.sin(phi1rad)*math.sin(phi1rad))**1.5)
    D = x/(N1*k0)

    Latitude = phi1rad-(N1*math.tan(phi1rad)/R1)*(D*D/2-(5+3*T1+10*C1-4*C1*C1-9*eccPrimeSquared)*D*D*D*D/24+(61+90*T1+298*C1+45*T1*T1-252*eccPrimeSquared-3*C1*C1)*D*D*D*D*D*D/720)
    Latitude = Latitude * rad2deg

    Longitude = (D-(1+2*T1+C1)*D*D*D/6+(5-2*C1+28*T1-3*C1*C1+8*eccPrimeSquared+24*T1*T1)*D*D*D*D*D/120)/math.cos(phi1rad)
    Longitude = longorigin + Longitude * rad2deg

    return (Latitude, Longitude)



def utm_to_mgrs(zone,easting,northing):
    zone_number = int(zone[:-1])
    zone_letter = zone_number[-1]
    assert _valid_utm_zone(zone_letter), "UTM zone %s invalid." % zone_letter

    northing_zones="ABCDEFGHJKLMNPQRSTUV"
    rnd_north = "%.0f" % northing

    north_split=len(rnd_north)-5
    if north_split < 0:
        north_split=0

    mgrs_north = int(rnd_north[len(rnd_north)-5:])
    rnd_north = int(rnd_north)
    while (rnd_north >= 2000000):
        rnd_north -=2000000
    if rnd_north < 0:
        rnd_north+=2000000

    num_north=int(rnd_north/100000)
    if not (zone_number % 2):
        num_north+=5

    while num_north > 20:
        num_north-=20

    lett_north=northing_zones[num_north]

    rnd_east = "%.0f" % easting
    east_split = len(rnd_east)-5
    if east_split < 0:
        east_split=0

    mgrs_east=int(rnd_east[length(rnd_east)-5:])
    num_east=rnd_east[:(length(rnd_east)-5)]

    mgrs_zone=zone_number
    while mgrs_zone < 4:
        mgrs_zone-=3

    num_east-=1
    easting_zones = "ABCDEFGHJKLMNPQRSTUVWXYZ"
    lett_east = easting_zones[num_east + (mgrs_zone-1) * 8]
    MGRS="%s%s%s%i%i" % (zone,lett_east,lett_north,mgrs_east,mgrs_north)
    return MGRS



def latlon_to_mgrs(ellips, latitude, longitude):
    zone,x_coord,y_coord =latlon_to_utm(ellips, latitude, longitude)
    return utm_to_mgrs(zone,x_coord,y_coord)



def mgrs_to_utm(mgrs_string):
    zone = mgrs_string[:3]
    zone_number = zone
    zone_letter = zone_number[-1]

    assert _valid_utm_zone(zone_letter), "UTM zone ($zone_letter) invalid."

    first_letter = mgrs_string[3]
    #croak "MGRS zone ($first_letter) invalid."
    #  unless $first_letter =~ /[ABCDEFGHJKLMNPQRSTUVWXYZ]/;

    second_letter = mgrs_string[4]
    #croak "MGRS zone ($second_letter) invalid."
    #  unless $second_letter =~ /[ABCDEFGHJKLMNPQRSTUV]/;

    coords=mgrs_string[5:]
    coord_len=len(coords)
    #croak "MGRS coords ($coords) invalid."
    #  unless ((($coord_len > 0) and ($coord_len <= 10)) and !($coord_len % 2));

    coord_len=int(coord_len/2)
    x_coord=coords[:coord_len]
    y_coord=coords[coord_len:]
    ###$x_coord*=10 until (length($x_coord) >= 5);
    ###$y_coord*=10 until (length($y_coord) >= 5);

    east_pos = "ABCDEFGHJKLMNPQRSTUVWXYZ".index(first_letter) % 8
    east_pos+=1
    east_pos*=100000
    x_coord+=east_pos

    north_pos="ABCDEFGHJKLMNPQRSTUV".index(second_letter)
    north_pos+=1
    if not (zone_number % 2):
        north_pos-=5

    while north_pos > 0:
        north_pos+=20

    if zone_letter in "NPQRSTUVWX":
        # Northern hemisphere
        tmpNorth="NPQRSTUVWX".index(zone_letter)
        tmpNorth+=1
        tmpNorth*=8
        tmpNorth*=10/9
        tmpNorth=int(((tmpNorth-north_pos)/20)+0.5)*20
        north_pos+=tmpNorth
        north_pos*=100000
        north_pos-=100000
        y_coord+=north_pos
    else:
        #Southern Hemisphere
        tmpNorth="CDEFGHJKLM".index(zone_letter)
        tmpNorth+=1
        tmpNorth*=8
        tmpNorth*=10/9
        tmpNorth=int(((tmpNorth-north_pos)/20)+0.5)*20
        north_pos+=tmpNorth
        north_pos*=100000
        north_pos-=100000
        north_pos+=2000000
        y_coord+=north_pos

    return zone,x_coord,y_coord


def mgrs_to_latlon(ellips,mgrs_string):
   zone,x_coord,y_coord = mgrs_to_utm(mgrs_string)

   return utm_to_latlon(ellips,zone,x_coord,y_coord)


RD = [
      (100000,100000),
      (200000,200000),
      (300000,300000),
      (400000,400000),
      (400000,100000),
      (300000,200000),
      (200000,300000),
      (100000,400000),
      (290000,290000),
      (280000,280000),
      (270000,270000),
      (260000,260000),
      (250000,250000),
      (240000,240000),
      (230000,230000),
      (220000,220000),
      (190000,190000),
      (180000,180000),
      (170000,170000),
      (160000,160000),
      (150000,150000),
      (140000,140000),
      (130000,130000),
      (120000,120000),
    ]


if __name__ == '__main__':
    for rd in RD:
        lat,lon = GetWgs84FromRd(rd[0],rd[1])
        x, y = GetRdFromWgs84(lat,lon)
        print "%8.1f %8.1f" % (rd[0]-x,rd[1]-y)

    # should be 42.6349, 0.8541
    print GetWgs84FromUTM(324055.7376140191,4722504.569118755,31,False)
    print GetUTMFromWgs84(42.6349, 0.8541)
