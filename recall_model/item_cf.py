# -*- coding: utf-8 -*-

import warnings
from tqdm import tqdm
from datetime import datetime
import numpy as np
warnings.filters('ignore')


class UserCF:
    def __init__(self, data, rec_nums):
        """
        recommend items that are similar to items you clicked on
        """
        self.data = data
        self.user2item_matrix = {}
        self.item_similarity_matrix = {}
        self.related_matrix = {}
        self.rec_nums = rec_nums
        self.topN_item = []
        self.rec_list = []

    def item_similarity(self):
        """
        calculate the similarity of each item
        :return:
        """
        data = self.data
        train_data = data.groupby(['user_id', 'item_id'])['datetime'].count().reset_index()

        print('begin to calculate the user2item_matrix')
        start_time = datetime.time()
        user2item = {}
        for i, row in tqdm(train_data.iterrows()):
            if row[1] not in user2item:
                user2item[int(row[1])] = {}
            user2item[int(row[1])][int(row[2])] = row[3]
        user2item = dict(sorted(user2item.items(), key=lambda x: x[0]))
        self.user2item_matrix = user2item
        end_time = datetime.time()
        print('user2item_matrix is created, it costs {} seconds'.format(end_time - start_time))

        # calculate item_similarity matrix
        N = {}
        C = {}
        print('calculate the item similarity matrix')
        for user, items in tqdm(user2item.items()):
            for i in items.keys():
                if i not in N:
                    N[i] = 0
                N[i] += 1
                if i not in C:
                    C[i] = {}
                for j in items.keys():
                    if i == j:
                        continue
                    if j not in C[i]:
                        C[i][j] = 0
                    C[i][j] += 1

        # calculate final similarity matrix w
        w = {}
        for i, related_item in tqdm(C.items()):
            if i not in w:
                w[i] = {}
            for j, value in related_item.items():
                if j not in w[i]:
                    w[i][j] = {}
                w[i][j] = value / np.sqrt(N[i] * N[j])
        self.related_matrix = w
        return w

    def get_hot_item(self):
        # get the hot item for users
        top_item = list(self.data['item_id'].value_counts()[:self.rec_nums].index)
        self.topN_item = top_item

    def recommend_single(self, user):
        rank = {}
        item_list = self.user2item_matrix[user]
        for i, p in item_list.items():
            for j, q in self.related_matrix[i].items():
                if j not in rank:
                    rank[j] = 0
                if j in item_list:
                    continue
                rank[j] += q

        rank = list(dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:self.rec_nums]))
        # rank = dict(sorted(rank.items(), key=lambda x: x[1], reverse=True)[0:rec_nums])

        if len(rank) < self.rec_nums:
            tmp = [i for i in self.topN_item if i not in rank]
            rank += tmp[0:50-len(rank)]
        return rank

    def recommend_all(self, user_list):
        ranks = []
        for user in tqdm(user_list):
            ranks.append(self.recommend_single(user))
        return ranks

