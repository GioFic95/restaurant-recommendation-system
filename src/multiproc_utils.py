import pandas as _pd
import time as _time
import os as _os


_cuisines_unique = ['Chinese', 'Japanese', 'Mexican', 'Italian', 'Others', 'American', 'Korean', 'Mediterranean', 'Thai', 'Asian Fusion']


def user_business_features(iterable):
    df_in, df_out_name = iterable
    
    df_out = _pd.read_pickle("../dataset/m2_n9/tmp/" + df_out_name + ".pickle") # reads df_out from tmp dir, file df_out_name
    
    count = 1
    tot = len(df_in)
    print("tot:", tot)

    for index, row in df_in.iterrows():
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


        cols = ['av_rat_chinese_cuisine', 'av_rat_japanese_cuisine', 'av_rat_mexican_cuisine', 'av_rat_italian_cuisine', 
                'av_rat_others_cuisine', 'av_rat_american_cuisine', 'av_rat_korean_cuisine', 'av_rat_mediterranean_cuisine',
                'av_rat_thai_cuisine', 'av_rat_asianfusion_cuisine',

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
            print("process {4}\t- row {0}/{1}\t- {2:.3f}%\t- {3}".format(count, tot, percent, _time.asctime(), _os.getppid()))

        count += 1
