#! /usr/bin/env python
# -*- coding:utf-8 -*-

import os
import time
import datetime
import calendar

import sklearn.linear_model as lm
import sklearn.datasets as ds

from extract_profile_features import extract_profile_features
from extract_balance_features import extract_balance_features
from extract_interest_features import extract_interest_features


def get_last_month_today(today):
     last_month = today.replace(day = 1) - datetime.timedelta(days = 1)
     last_month_days = calendar.monthrange(last_month.year, last_month.month)[-1]
     tmp_day = today.day if today.day <= last_month_days else last_month_days
     last_month_today = today.replace(month = last_month.month, day = tmp_day)
     return last_month_today.strftime('%Y%m%d')


def is_mon_to_thur(today):
     weekday = today.weekday()
     return weekday>=0 and weekday<=3


def predict():
    path = os.path.abspath(os.path.dirname(__file__))
    user_profile_file_path = path + '/user_profile_table.csv'
    profile_features = extract_profile_features(user_profile_file_path)
    interest_file_path = path + '/mfd_day_share_interest.csv'
    interest_features = extract_interest_features(interest_file_path)
    user_balance_file_path = path + '/user_balance_table.csv'
    balance_features = extract_balance_features(user_balance_file_path)

    #feacture = profile_features + interest_features + balance_features
    #every user for every day
    x = []
    y1 = []
    y2 = []
    for key, val in balance_features.iteritems():
        uid, today = key.split(':')
        #print 'today:', today
        profile = profile_features[uid]
        today_ = datetime.datetime(*time.strptime(today, '%Y%m%d')[:3])
        yestoday = (today_ - datetime.timedelta(days = 1)).strftime('%Y%m%d')
        #print 'yestoday:', yestoday
        tmp_key = '%s:%s' % (uid, yestoday)
        if tmp_key not in balance_features:
            tmp_key = key
        yestoday_balance = balance_features[tmp_key]
        last_month_today = get_last_month_today(today_)
        #print 'last_month_today', last_month_today
        tmp_key = '%s:%s' % (uid, last_month_today)
        if tmp_key not in balance_features:
            tmp_key = key
        last_month_today_balance = balance_features[tmp_key]
        is_mon_to_thur_ = [is_mon_to_thur(today_),] #是否周一到周四
        #print 'is_mon_to_thur:', is_mon_to_thur_
        feature = profile + yestoday_balance +\
            last_month_today_balance + is_mon_to_thur_ #+\
            #interest_features[today]
        #print 'feature:', feature
        x.append(feature)
        y1.append(val[0])
        y2.append(val[1])

    clf1 = lm.LinearRegression()
    clf1.fit(x, y1)
    clf2 = lm.LinearRegression()
    clf2.fit(x, y2)
    purchase = []
    redeem = []
    for i in xrange(1, 31):
        today = '201409%02d' % (i,)
        p = 0
        r = 0
        for uid, val in profile_features.iteritems():
            key = '%s:%s' % (uid, today)
            profile = profile_features[uid]
            today_ = datetime.datetime(*time.strptime(today, '%Y%m%d')[:3])
            yestoday = (today_ - datetime.timedelta(days = 1)).strftime('%Y%m%d')
            #print 'yestoday:', yestoday
            tmp_key = '%s:%s' % (uid, yestoday)
            if tmp_key not in balance_features:
                tmp_key = key
            yestoday_balance = balance_features[tmp_key]
            last_month_today = get_last_month_today(today_)
            #print 'last_month_today', last_month_today
            tmp_key = '%s:%s' % (uid, last_month_today)
            if tmp_key not in balance_features:
                tmp_key = key
            last_month_today_balance = balance_features[tmp_key]
            is_mon_to_thur_ = [is_mon_to_thur(today_),] #是否周一到周四
            #print 'is_mon_to_thur:', is_mon_to_thur_
            feature = profile + yestoday_balance +\
                last_month_today_balance + is_mon_to_thur_ #+\
                #interest_features[today]
            p += clf1.predict([feature,])[0]
            r += clf2.predict([feature,])[0]
        print 'date\tp\tr'
        print '%s\t%s\t%s' % (today, p, r)
        purchase.append(p)
        redeem.append(r)


if __name__ == '__main__':
    predict()
