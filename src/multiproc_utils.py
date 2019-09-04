import pandas as _pd
import numpy as _np
import time as _time
import os as _os
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

rev_cols = ['user_id', 'stars', 'bin_truth_score', 'real_truth_score']


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


def aggregate(grouped):
    d = {}
    non_fake = _np.ma.masked_where(grouped['bin_truth_score'] <= 0, grouped['stars']).compressed()
    
    d['stars'] = grouped['stars'].mean()
    d['stars_bin'] = non_fake.mean()
    d['stars_real'] = _np.average(grouped['stars'], weights=grouped['real_truth_score'])
    
    return _pd.Series(d, index=['stars', 'stars_bin', 'stars_real'])


def sub_set_coll_scores(review_set, review_hist, users, restaurants):
    count = 1
    tot = review_set.shape[0]
    rest_id = None

    for rid, row in review_set.iterrows():
        user_id = row['user_id']
        curr_user = users.loc[user_id]
        old_rest_id = rest_id
        rest_id = row['business_id']

        if old_rest_id != rest_id:
            review_rest_new = review_set.loc[review_set.business_id == rest_id, rev_cols]
            review_rest_old = review_hist.loc[review_hist.business_id == rest_id, rev_cols]
            tmp_review_rest = _pd.concat([review_rest_new, review_rest_old])
            tmp_review_rest = tmp_review_rest.groupby('user_id').apply(aggregate)
            tmp_user_rest = users.loc[users.index.isin(tmp_review_rest.index)]

        review_rest = tmp_review_rest.drop(user_id)
        user_rest = tmp_user_rest.drop(user_id)
        assert review_rest.shape[0] == user_rest.shape[0], "different shapes: " + str(review_rest.shape) + " vs " + str(user_rest.shape)

        a_u = row['cuisine_av_hist']
        a_u_bin = row['cuisine_av_hist_bin']
        a_u_real = row['cuisine_av_hist_real']

        if user_rest.empty:
            res = 0
            res_bin = 0
            res_real = 0

        else:
            a_r = restaurants.loc[rest_id, 'average_stars']
            a_u_r = review_rest['stars']
            user_sim = _cosine_similarity(curr_user[cols_std].values.reshape(1, -1), user_rest[cols_std])
            user_sim = _pd.Series(data=user_sim[0], index=user_rest.index)
            user_sim.where(user_sim > 0.5, 0, inplace=True)
            numerator = (user_sim * (a_u_r - a_r)).sum()
            denominator = user_sim.sum()
            res = numerator / denominator

            a_r_bin = restaurants.loc[rest_id, 'average_stars_bin']
            a_u_r_bin = review_rest['stars_bin'].fillna(a_r_bin)
            user_sim = _cosine_similarity(curr_user[cols_bin].values.reshape(1, -1), user_rest[cols_bin])
            user_sim = _pd.Series(data=user_sim[0], index=user_rest.index)
            user_sim.where(user_sim > 0.5, 0, inplace=True)
            numerator_bin = (user_sim * (a_u_r_bin - a_r_bin)).sum()
            denominator_bin = user_sim.sum()
            res_bin = numerator_bin / denominator_bin

            a_r_real = restaurants.loc[rest_id, 'average_stars_real']
            a_u_r_real = review_rest['stars_real']
            user_sim = _cosine_similarity(curr_user[cols_real].values.reshape(1, -1), user_rest[cols_real])
            user_sim = _pd.Series(data=user_sim[0], index=user_rest.index)
            user_sim.where(user_sim > 0.5, 0, inplace=True)
            numerator_real = (user_sim * (a_u_r_real - a_r_real)).sum()
            denominator_real = user_sim.sum()
            res_real = numerator_real / denominator_real

        out_cols = ['coll_score', 'coll_score_bin', 'coll_score_real']
        vals = [a_u + res, a_u_bin + res_bin, a_u_real + res_real]
        review_set.loc[rid, out_cols] = vals

        if count % 1000 == 0:
            percent = (count / tot) * 100
            print("process {4}\t- row {0}/{1}\t- {2:.3f}%\t- {3}"
                  .format(count, tot, percent, _time.asctime(), _os.getpid()))

        count += 1


def set_coll_scores(iterable):
    review_set, review_split_name, review_hist, users, restaurants = iterable

    try:
        sub_set_coll_scores(review_set, review_hist, users, restaurants)
    except:
        print("Unexpected error:", _traceback.format_exc())
    finally:
        review_set.to_pickle(review_split_name)
