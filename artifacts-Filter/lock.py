import os
import time
from configparser import ConfigParser

import pandas as pd
from tqdm import tqdm

import pdb
from artifact import Artifact, good_to_mona
from build import load_build


proDir = os.path.split(os.path.realpath(__file__))[0]

cfg = ConfigParser()
cfg.read(proDir + '/config/screen.ini')

score_threshold = float(cfg.items('screen')[0][1])
rarity_threshold = float(cfg.items('screen')[1][1])


def sort_art(df: pd.DataFrame):
    k = 0  #
    sorted_df = df.iloc[0:1]
    while k != df.shape[0] - 1:
        for t in range(k, df.shape[0]):
            if t < df.shape[0]:
                if df.iloc[t]['adaptScore'] != df.iloc[k]['adaptScore']:
                    p = t - k  # 切片长度
                    slice_sort = df.iloc[k:k + p]
                    slice_sort = slice_sort.sort_values(by='difficulty', ascending=False)
                    sorted_df = pd.concat([sorted_df, slice_sort])
                    k = t  # 下一次起点
            else:
                if df.iloc[t]['adaptScore'] == df.iloc[k]['adaptScore']:
                    p = t - k + 1  # 切片长度
                    slice_sort = df.iloc[k:k + p]
                    slice_sort = slice_sort.sort_values(by='difficulty', ascending=False)
                    sorted_df = pd.concat([sorted_df, slice_sort])
                    k = t  # 最终的终点
        break
    sorted_df = sorted_df[1:]
    return sorted_df


def adapt(art: Artifact, df: pd.DataFrame):
    """对每一个build进行适配性评分"""
    d_temp = {}
    p = 0
    best_score = 0
    for i,row in df.iterrows():  # 遍历build库
        fitness = 0  # 对该build的适配度
        build_adapt = pd.Series([], dtype='float64')
        fitness += art.main.multiply(row['{}MainWeights'.format(art.position)]).dropna().sum()  # 主属性加权和
        fitness += art.sec.multiply(row['secWeights']).dropna().sum()  # 副属性加权和
        if art.set not in row['sets']:  # 非套装扣0.6
            fitness -= 0.6
        if art.star < 5:  # 非五星扣0.6
            fitness -= 0.6
        adapt_score = fitness / row['best_{}'.format(art.position)]  # 适配分 = 适配度 / 最佳适配度
        # 将build-评分-难度储存到列表中，并以指针为key储存到字典中
        build_adapt['buildName'] = row['buildName']
        build_adapt['adaptScore'] = adapt_score
        build_adapt['difficulty'] = row['{}Difficulty'.format(art.position)]
        d_temp[p] = build_adapt
        p += 1
    art_adapt = pd.DataFrame(d_temp).T  # 字典压缩成df数据表
    best_score = art_adapt['adaptScore'].max()  # 获得最佳适配度
    # 以适配度为第一优先级、毕业难度为第二优先级对df数据表进行排序
    art_adapt = art_adapt.sort_values(by='adaptScore', ascending=False)
    art_adapt = sort_art(art_adapt)
    # 装入圣遗物评分列表前要先筛选掉不合格的适配评分
    art_adapt = art_adapt[art_adapt['adaptScore'] > score_threshold]
    return best_score, art_adapt


if __name__ == '__main__':
    build_df = load_build(reload=False)
    print('正在分析圣遗物......')
    print('只显示适配度大于{}, 或稀有度大于{}的圣遗物.'.format(
        '{:.1%}'.format(score_threshold), '{:.1f}'.format(rarity_threshold)))

    lock_list = []
    artifacts = good_to_mona()
    #pdb.set_trace()
    art_d=[]
    now_lock_list = []
    for idx,artifact in tqdm(artifacts.iterrows(),total=len(artifacts)):
        if artifact.lock:
            now_lock_list.append(idx)
            # temp_best, temp_art_df = adapt(a, build_df)
            # max_difficulty = temp_art_df['difficulty'].max()
            # if ((temp_best > score_threshold) and (max_difficulty>3) ) or (a.rarity > rarity_threshold):  # 筛选最佳适配度或稀有度达标的圣遗物
            #     if not a.lock:
            #         lock_list.append(idx)
            #     art_score = pd.Series([], dtype='float64')
            #     art_score['artAbstract'] = a.abstract
            #     art_score['artMain'] = a.main_chs
            #     art_score['artSec'] = a.sec_chs
            #     art_score['artRarity'] = a.rarity
            #     art_score['bestScore'] = temp_best
            #     art_score['eachScore'] = temp_art_df
            #     art_d.append(art_score)
    
    # all_score = pd.DataFrame(art_d)
    # all_score = all_score.sort_values(by='bestScore', ascending=False)
    # print('共有{}件圣遗物, 显示其中{}件'.format(len(artifacts), all_score.shape[0]))
    # all_words = []
    # for i in range(all_score.shape[0]):
    #     print('<============================【{}】============================>'.format(i+1))
    #     words = []
    #     words.append(all_score.iloc[i]['artAbstract'])
    #     words.append(all_score.iloc[i]['artMain'])
    #     words.append(all_score.iloc[i]['artSec'])
    #     words.append('该圣遗物最佳评分为:【{}】, 稀有度为{}.'.
    #           format('{:.1%}'.format(all_score.iloc[i]['bestScore']),
    #                  '{:.1f}'.format(all_score.iloc[i]['artRarity'])))
    #     words.append('---------build列表---------')
    #     temp = all_score.iloc[i]['eachScore']
    #     if temp.shape[0] > 10:
    #         temp = temp.iloc[0:10]
    #     for j in range(temp.shape[0]):
    #         words.append('对BUILD:[{}]的适配度为【{}】,该部位完美毕业难度为: {}'.format(
    #             temp.iloc[j]['buildName'], '{:.1%}'.format(temp.iloc[j]['adaptScore']),
    #             '{:.1f}'.format(temp.iloc[j]['difficulty'])))
    #     words = '\n'.join(words)
    #     print(words)
    #     all_words.append(words)
    # all_score.to_csv(proDir + '/result/result.csv')
    # all_score['result'] = all_words
    # all_score['result'].to_csv(proDir + '/result/result_words.csv')
    # with open(proDir + '/result/lock.json','w') as handler:
    #     handler.write(str(lock_list))
    with open(proDir + '/result/now_lock.json','w') as handler:
        handler.write(str(now_lock_list))
    # input('请按任意键继续...')
    # time.sleep(999)
    # print('999秒后自动关闭窗口')
