import pandas as _pd
import time as _time
import os as _os
import sys as _sys

_cuisines_unique = ['Chinese', 'Japanese', 'Mexican', 'Italian', 'Others', 'American', 'Korean', 'Mediterranean', 'Thai', 'Asian Fusion']


def sub_user_business_features(df_in, df_out):
    is_nan = True
    count = 1
    tot = len(df_in)
    print("tot:", tot)

    for index, row in df_in.iterrows():
        if not row.isna().all():
            uid = index
            vals = []

            for cuisine in _cuisines_unique:
                cuisine_av = cuisine + "_av"
                vals.append(row[cuisine_av])

            for cuisine in _cuisines_unique:
                cuisine_av_bin = cuisine + "_av_bin"
                vals.append(row[cuisine_av_bin])

            for cuisine in _cuisines_unique:
                cuisine_av_real = cuisine + "_av_real"
                vals.append(row[cuisine_av_real])

            cols = ['av_rat_chinese_cuisine', 'av_rat_japanese_cuisine', 'av_rat_mexican_cuisine',
                    'av_rat_italian_cuisine', 'av_rat_others_cuisine', 'av_rat_american_cuisine',
                    'av_rat_korean_cuisine', 'av_rat_mediterranean_cuisine', 'av_rat_thai_cuisine',
                    'av_rat_asianfusion_cuisine',

                    'av_rat_chinese_cuisine_bin', 'av_rat_japanese_cuisine_bin', 'av_rat_mexican_cuisine_bin',
                    'av_rat_italian_cuisine_bin', 'av_rat_others_cuisine_bin', 'av_rat_american_cuisine_bin',
                    'av_rat_korean_cuisine_bin', 'av_rat_mediterranean_cuisine_bin', 'av_rat_thai_cuisine_bin',
                    'av_rat_asianfusion_cuisine_bin',

                    'av_rat_chinese_cuisine_real', 'av_rat_japanese_cuisine_real', 'av_rat_mexican_cuisine_real',
                    'av_rat_italian_cuisine_real', 'av_rat_others_cuisine_real', 'av_rat_american_cuisine_real',
                    'av_rat_korean_cuisine_real', 'av_rat_mediterranean_cuisine_real', 'av_rat_thai_cuisine_real',
                    'av_rat_asianfusion_cuisine_real']

            df_out.loc[uid, cols] = vals

            if (count % 1000) == 0:
                percent = (count / tot) * 100
                print("process {4}\t- row {0}/{1}\t- {2:.3f}%\t- {3}"
                      .format(count, tot, percent, _time.asctime(), _os.getpid()))

            count += 1
        else:
            if is_nan:
                print("is nan:", row)
                is_nan = False
            count += 1
            continue


def user_business_features(iterable):
    df_in, df_out, df_out_name = iterable
    
    try:
        sub_user_business_features(df_in, df_out)
    except:
        print("Unexpected error:", _sys.exc_info()[0])
    finally:
        df_out.to_pickle(df_out_name)

