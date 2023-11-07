import numpy as np
import pandas as pd
import fitsio
import os
import glob
import matplotlib.pyplot as plt

def list_nights_in_release(release_path='/global/cfs/cdirs/desi/spectro/redux/iron/exposures/', min_night=20210415):
    dirs = glob.glob(release_path+'/*')
    dirs.sort()
    nights = []
    for d in dirs:
        night = int(d.split('/')[-1])
        if night >= min_night:
            nights.append(night)
    return nights
    
def list_exps(date):
    exps_daily = pd.read_csv("/global/cfs/cdirs/desi/spectro/redux/daily/exposures-daily.csv")
    #print(exps_daily.keys())
    ii = (exps_daily["NIGHT"]==date)
    #print(exps_daily["NIGHT"][ii])
    exps_daily = exps_daily[ii]
    return exps_daily

def read_sky_sframe(sframe_file):
    #print(sframe_file)
    try:
        h = fitsio.FITS(sframe_file)
        sel = h["FIBERMAP"]["OBJTYPE"].read() == "SKY"
        sky = h["FLUX"].read()[sel,:]
    except:
        sky = None
    return sky

def compute_sframe_difference(data_release_path, daily_path, date, expid, output_path="./data/"):
    filename = 'sky_diff_sframe_{}_{:08d}.csv'.format(date, expid)
    out_filename = os.path.join(output_path, filename)
    n_petals = 10
    bands = ['b', 'r', 'z']
    summary = {}
    summary['band'] = []
    summary['petal'] = []
    summary['diff_mean'] = []
    summary['diff_std'] = []
    summary['expid'] = []
    summary['night'] = []
    for i in range(n_petals):
        for band in bands:
            filename_A = '{}/{}/{:08d}/sframe-{}{}-{:08d}.fits'.format(data_release_path, date, expid, band, i, expid)
            sky_petal_A = read_sky_sframe(filename_A)
            filename_B = '{}/{}/{:08d}/sframe-{}{}-{:08d}.fits'.format(daily_path, date, expid, band, i, expid)
            sky_petal_B = read_sky_sframe(filename_B)
            if sky_petal_A is not None and sky_petal_B is not None:
                sky_diff = sky_petal_B-sky_petal_A
           #     proba = ient.compute_probability_distribution_2D(sky_petal)
           #     entropy =  ient.compute_entropy(proba)
                summary['band'].append(band)
                summary['petal'].append(i)
                summary['diff_mean'].append(sky_diff.mean())
                summary['diff_std'].append(sky_diff.std())
                summary['expid'].append(expid)
                summary['night'].append(date)
                #print(date, expid, band, i, sky_diff.mean(), sky_diff.std())
    entropy_df = pd.DataFrame.from_dict(summary)

    #os.makedirs(output_path, exist_ok=True) 
    entropy_df.to_csv(out_filename)
    
    #print(summary)
    
def data_comparison_release_vs_daily(data_release_path, daily_path, date, output_path="./data"):
    exps = list_exps(date)
    # compute differences
    dates = list(exps["NIGHT"])
    expids = list(exps["EXPID"])
    for date, expid in zip(dates, expids):
        compute_sframe_difference(data_release_path, daily_path, date, expid, output_path=output_path)
        

nights = list_nights_in_release()
print(nights, len(nights))

iron_path = '/global/cfs/cdirs/desi/spectro/redux/iron/exposures/'
daily_path = '/global/cfs/cdirs/desi/spectro/redux/daily/exposures/'

for date in nights:
    print(date)
    data_comparison_release_vs_daily(iron_path, daily_path, date, output_path='../data/')