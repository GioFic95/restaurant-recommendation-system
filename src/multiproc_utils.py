import pandas as _pd
import time as _time
import os as _os
import sys as _sys
import traceback as _traceback
from sklearn.metrics.pairwise import cosine_similarity as _cosine_similarity

_cuisines_unique = ['Chinese', 'Japanese', 'Mexican', 'Italian', 'Others', 'American', 'Korean', 'Mediterranean', 'Thai', 'Asian Fusion']

cols_std = ['av_rat_chinese_cuisine', 'av_rat_japanese_cuisine', 'av_rat_mexican_cuisine', 'av_rat_italian_cuisine', 
            'av_rat_others_cuisine', 'av_rat_american_cuisine', 'av_rat_korean_cuisine', 'av_rat_mediterranean_cuisine',
            'av_rat_thai_cuisine', 'av_rat_asianfusion_cuisine']


cols_bin = ['av_rat_chinese_cuisine_bin', 'av_rat_japanese_cuisine_bin', 'av_rat_mexican_cuisine_bin', 
           'av_rat_italian_cuisine_bin', 'av_rat_others_cuisine_bin', 'av_rat_american_cuisine_bin', 
           'av_rat_korean_cuisine_bin', 'av_rat_mediterranean_cuisine_bin', 'av_rat_thai_cuisine_bin', 
           'av_rat_asianfusion_cuisine_bin']


cols_real = ['av_rat_chinese_cuisine_real', 'av_rat_japanese_cuisine_real', 'av_rat_mexican_cuisine_real', 
           'av_rat_italian_cuisine_real', 'av_rat_others_cuisine_real', 'av_rat_american_cuisine_real', 
           'av_rat_korean_cuisine_real', 'av_rat_mediterranean_cuisine_real', 'av_rat_thai_cuisine_real', 
           'av_rat_asianfusion_cuisine_real']

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
        print("Unexpected error:", _traceback.format_exc())
    finally:
        df_out.to_pickle(df_out_name)


def sub_set_coll_scores(review_set, users, restaurants):
    count = 1
    tot = review_set.shape[0]
    
    for rid, row in review_set.iterrows():
        rest_id = row['business_id']
        user_id = row['user_id']
        
        a_u_r = row['cuisine_av_hist']
        a_r = restaurants.loc[rest_id, 'average_stars']
        user_sim = _cosine_similarity(users.loc[user_id, cols_std].values.reshape(1,-1), users[cols_std])
        user_sim = _pd.Series(data=user_sim[0], index=users.index)
        numerator = (user_sim * (a_u_r - a_r)).sum() -  1 * (a_u_r_bin - a_r_bin)
        denominator = user_sim.sum() -1
        
        a_u_r_bin = row['cuisine_av_hist_bin']
        a_r_bin = restaurants.loc[rest_id, 'average_stars_bin']
        user_sim = _cosine_similarity(users.loc[user_id, cols_bin].values.reshape(1,-1), users[cols_bin])
        user_sim = _pd.Series(data=user_sim[0], index=users.index)
        numerator_bin = (user_sim * (a_u_r_bin - a_r_bin)).sum() -  1 * (a_u_r_bin - a_r_bin)
        denominator_bin = user_sim.sum() -1
        
        a_u_r_real = row['cuisine_av_hist_real']
        a_r_real = restaurants.loc[rest_id, 'average_stars_real']
        user_sim = _cosine_similarity(users.loc[user_id, cols_real].values.reshape(1,-1), users[cols_real])
        user_sim = _pd.Series(data=user_sim[0], index=users.index)
        numerator_real = (user_sim * (a_u_r_real - a_r_real)).sum() -  1 * (a_u_r_bin - a_r_bin)
        denominator_real = user_sim.sum() -1
        
        out_cols = ['coll_score', 'coll_score_bin', 'coll_score_real']
        vals = [numerator/denominator, numerator_bin/denominator_bin, numerator_real/denominator_real]
        review_set.loc[rid, out_cols] = vals
        
        if count % 1000 == 0:
            percent = (count/tot)*100
            print("process {4}\t- row {0}/{1}\t- {2:.3f}%\t- {3}"
                  .format(count, tot, percent, _time.asctime(), _os.getpid()))
        
        count += 1


def set_coll_scores(iterable):
    review_set, review_split_name, users, restaurants = iterable
    
    try:
        sub_set_coll_scores(review_set, users, restaurants)
    except:
        print("Unexpected error:", _traceback.format_exc())
    finally:
        review_set.to_pickle(review_split_name)

