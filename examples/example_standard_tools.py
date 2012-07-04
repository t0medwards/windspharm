import os
import urllib2

import numpy as np
import matplotlib as mpl
mpl.rcParams['mathtext.default'] = 'regular'
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap, addcyclic
from netCDF4 import Dataset

from windspharm.standard import VectorWind
from windspharm.tools import prep_data, recover_data, order_latdim


if __name__ == '__main__':

    # Download U and V wind fields.
    u_remote = os.path.join('ftp://ftp.cdc.noaa.gov', 'Datasets',
            'ncep.reanalysis.derived', 'pressure', 'uwnd.mon.1981-2010.ltm.nc')
    u_local = 'uwnd.mon.ltm.nc'
    if not os.path.exists(u_local):
        ncremote = urllib2.urlopen(u_remote)
        nclocal = open(u_local, 'wb')
        nclocal.write(ncremote.read())
        nclocal.close()
        ncremote.close()
    v_remote = os.path.join('ftp://ftp.cdc.noaa.gov', 'Datasets',
            'ncep.reanalysis.derived', 'pressure', 'vwnd.mon.1981-2010.ltm.nc')
    v_local = 'vwnd.mon.ltm.nc'
    if not os.path.exists(v_local):
        ncremote = urllib2.urlopen(v_remote)
        nclocal = open(v_local, 'wb')
        nclocal.write(ncremote.read())
        nclocal.close()
        ncremote.close()

    # Read wind data.
    ncin = Dataset(u_local)
    lon = ncin.variables['lon'][:]
    lat = ncin.variables['lat'][:]
    lev = ncin.variables['level'][:]
    uwnd = ncin.variables['uwnd'][:]
    ncin.close()
    ncin = Dataset(v_local)
    vwnd = ncin.variables['vwnd'][:]
    ncin.close()

    # Prepare the input data for input.
    uwnd, uinfo = prep_data(uwnd, 'tzyx')
    vwnd, vinfo = prep_data(vwnd, 'tzyx')

    # Reverse the latitude dimension if necessary, we need 90N to 90S.
    lat, uwnd, vwnd = order_latdim(lat, uwnd, vwnd, axis=0)

    # Create a VectorWind instance.
    w = VectorWind(uwnd, vwnd, gridtype='regular')

    # Compute streamfunction and velocity potential.
    sf, vp = w.sfvp()

    # Re-shape and re-order results back to the original shape of the
    # inputs.
    sf = recover_data(sf, uinfo)
    vp = recover_data(vp, uinfo)
    
    # Pick the field for December at 200 hPa and add a cyclic point.
    sf_d_200, lon_c = addcyclic(sf[11, 9], lon)
    vp_d_200, lon_c = addcyclic(vp[11, 9], lon)

    # Set up a map projection to plot the results.
    m = Basemap(projection='cyl', resolution='c', llcrnrlon=0, llcrnrlat=-90,
            urcrnrlon=360.01, urcrnrlat=90)
    x, y = m(*np.meshgrid(lon_c, lat))

    # Plot streamfunction at 200 hPa for December.
    plt.figure()
    clevs = [-120, -100, -80, -60, -40, -20, 0, 20, 40, 60, 80, 100, 120]
    m.contourf(x, y, sf_d_200*1e-06, clevs, cmap=plt.cm.RdBu_r, extend='both')
    m.drawcoastlines()
    m.drawparallels((-90, -60, -30, 0, 30, 60, 90), labels=[1,0,0,0])
    m.drawmeridians((0, 60, 120, 180, 240, 300, 360), labels=[0,0,0,1])
    plt.colorbar(orientation='horizontal')
    plt.title('Streamfunction ($10^6$m$^2$s$^{-1}$)', fontsize=16)
    plt.savefig('example_standard_tools_0.png')

    # Plot velocity potential at 200 hPa for December.
    plt.figure()
    clevs = [-10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10]
    m.contourf(x, y, vp_d_200*1e-06, clevs, cmap=plt.cm.RdBu_r, extend='both')
    m.drawcoastlines()
    m.drawparallels((-90, -60, -30, 0, 30, 60, 90), labels=[1,0,0,0])
    m.drawmeridians((0, 60, 120, 180, 240, 300, 360), labels=[0,0,0,1])
    plt.colorbar(orientation='horizontal')
    plt.title('Velocity Potential ($10^6$m$^2$s$^{-1}$)', fontsize=16)
    plt.savefig('example_standard_tools_1.png')
