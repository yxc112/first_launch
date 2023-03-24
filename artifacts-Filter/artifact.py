import pandas as pd
from jsonpath import jsonpath

from dict import attribute_dict, position_dict, set_dict
from rarity import rarity


def good_to_mona():
    good = pd.read_json('good.json')
    f = pd.DataFrame(good['artifacts'].to_list())
    # columns rename

    f.rename(dict(zip(['setKey', 'slotKey',
                       'mainStatKey', 'substats', 'rarity'], ['setName', 'position', 'mainTag', 'normalTags',
                                                            'star'])), axis=1, inplace=True)
    # 修改setKey 首字母大写改小写
    f['setName'] = f['setName'].apply(lambda x: x[0].lower()+x[1:])
    # 修改slotKey 字典匹配
    position_dict = dict(zip(["flower",
                              "plume",
                              "sands",
                              "goblet",
                              "circlet"], ["flower",
                                           "feather",
                                           "sand",
                                           "cup",
                                           "head", ]))
    f['position'] = f['position'].map(position_dict)

    # 修改mainStatKey
    main_dict = dict(zip(["heal_", "critDMG_", "critRate_", "atk", "atk_", "eleMas", "enerRech_", "hp_", "hp", "def_", "def", "electro_dmg_", "pyro_dmg_",
                          "hydro_dmg_", "cryo_dmg_", "anemo_dmg_", "geo_dmg_", "physical_dmg_", "dendro_dmg_"],
                         ["cureEffect", "criticalDamage", "critical", "attackStatic", "attackPercentage",
                         "elementalMastery",
                          "recharge",
                          "lifePercentage",
                          "lifeStatic",
                          "defendPercentage",
                          "defendStatic",
                          "thunderBonus",
                          "fireBonus",
                          "waterBonus",
                          "iceBonus",
                          "windBonus",
                          "rockBonus",
                          "physicalBonus",
                          "dendroBonus", ]))
    f['mainTag'] = f['mainTag'].map(main_dict)
    f['mainTag'] = f['mainTag'].apply(lambda x: {'name': x, 'value': 0.0})

    def value_func(v, k): return v if k in [
        'lifeStatic', 'elementalMastery', 'defendStatic', "attackStatic"] else v/100

    f['normalTags'] = f['normalTags'].apply(lambda x: [
                                            {'name': main_dict[v['key']], 'value':value_func(v['value'], main_dict[v['key']])} for v in x])
    f['omit'] = False

    #f.to_json('good2mona.json')
    return f


class Artifact:
    def __init__(self):
        self.abstract = None
        self.star = None
        self.set = None
        self.set_chs = None
        self.position = None
        self.position_chs = None
        self.level = None
        self.main = pd.Series([], dtype='float64')
        self.raw_sec = pd.Series([], dtype='float64')
        self.main_chs = None
        self.sec_chs = None
        self.sec = pd.Series([], dtype='float64')  # 副词条归一化
        self.rarity = 0

    def read(self, art_dict: dict):
        self.star = art_dict['star']
        self.set = art_dict['setName']
        self.lock = art_dict['lock']
        self.set_chs = set_dict[self.set]["chs"]
        self.position = art_dict['position']
        self.position_chs = position_dict[self.position]
        self.level = art_dict['level']
        self.abstract = '{}星 {} {}; 等级:{}'.format(
            self.star, self.set_chs, self.position_chs, self.level)
        self.main[jsonpath(art_dict, "$.mainTag.name")[0]] = 1
        self.raw_sec = pd.Series(jsonpath(art_dict, "$.normalTags[*].value"),
                                 index=jsonpath(art_dict, "$.normalTags[*].name"))
        self.main_chs = '主属性为:' + \
            '【{}】'.format(
                jsonpath(attribute_dict, "$.{}.chs".format(self.main.index[0]))[0])
        sec_index = []
        for i in range(len(self.raw_sec.index.tolist())):
            sec_index += [jsonpath(attribute_dict,
                                   "$.{}.chs".format(self.raw_sec.index[i]))[0]]
        temp_sec_chs = pd.Series(self.raw_sec.values, index=sec_index)
        self.sec_chs = '副属性为: '
        for i in range(len(temp_sec_chs)):
            if temp_sec_chs[i] < 1:
                self.sec_chs += '{}--{}; '.format(
                    temp_sec_chs.index[i], '{:.1%}'.format(temp_sec_chs[i]))
            else:
                self.sec_chs += '{}--{}; '.format(
                    temp_sec_chs.index[i], '{:.0f}'.format(temp_sec_chs[i]))
        for i in range(len(self.raw_sec)):
            self.sec[self.raw_sec.index[i]] = \
                self.raw_sec[i] / jsonpath(attribute_dict,
                                           "$.{}.average".format(self.raw_sec.index[i]))[0]
        if self.level <=4 and self.star >= 4:  # 筛选合格的胚子
        #if self.star >= 4:  # 筛选合格的胚子
            if len(self.sec) == 3:  # 初始3词缀
                rarity_list = [self.position, 3] + \
                    self.main.index.tolist() + self.sec.index.tolist()
                self.rarity = rarity(rarity_list)
            elif len(self.sec) == 4:
                if self.star < 4:  # 初始4词缀
                    rarity_list = [self.position, 3] + \
                        self.main.index.tolist() + self.sec.index.tolist()
                    self.rarity = rarity(rarity_list)
                elif self.star >= 4:
                    max_normalize = self.sec.max()  # 归一值中的最大值
                    if max_normalize > 1.2:  # 大于1.2，初始4词条
                        rarity_list = [
                            self.position, 4] + self.main.index.tolist() + self.sec.index.tolist()
                        self.rarity = rarity(rarity_list)
                    else:  # 小于1.2，初始3词条
                        rarity_list = [
                            self.position, 4] + self.main.index.tolist() + self.sec.index.tolist()
                        self.rarity = rarity(rarity_list)


if __name__ == '__main__':
    pass
