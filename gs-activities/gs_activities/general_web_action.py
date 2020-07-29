# -*- coding: utf-8 -*-

# ALERT : py 文件中出现 """ 引用的 comment ，在 uipath 的 "load python script"的activity 中会出现 load error


# 定义一个 较为通用的 web app action
# Action Def 的 Signature 形如： GeneralWebApp(unique_cfg_name:str,kw1:str , kw2:str)
# cfg 中含有的信息：
#   1) url template , 支持 kw 参与到 url 的产生过程
#
#   2) [optional] type kw area (selector) ,  如有，则 keyword 将输入到该区域
#       2.0) [optional] click (selector) before typing 适用于load page之后，输入框没有直接出现在页面中的情况
#       2.1) [optional] kw function , 对 kw 提供一些基于业务的处理，比如
#                               add "enter" after typing ,  适用于 keyword 输入之后，可以直接按回车
#                               add advance search condition , 适用于在 twitter search 这种场景中，增加一些限定条件，这部分如有入参，将来自于 kw2
#
#   3) [optional] click (selector) after typing , 如有，则用于输入之后的按钮点击，一般是 run search，不支持通过按 enter 的方式
#
#   4) [optional] detected no data selector , 如有，则发现该 uiElement 存在时，将主动关闭该 tab
#
#   5) [optional] extract data selector ，适用于提取一部分数据提交到 mongo 中进行保存
#                   第一阶段先不支持该功能，难点主要在于怎么把这类输出的 csv table 通用化。
#                       并且有很多 constraint ，比如： 不能有各种类型的翻页，不能定制交互抓一些补充的数据
#                   还有一个限制在于，客户使用 DesktopRPA时，未必在 GS 的局域网里，但action result 上传到 mongo 依赖于 对 mongo的访问能力。
#                                                                                   （可以做一个http api的方式，打破该限制）


# NOTE: 将设置文件从 json 改为 xml ， 因为有些 select 是 multiline string , json 输入这种格式的文件较为复杂


import json
import os
import sys

# 根据 https://docs.uipath.com/activities/docs/load-script 中的描述，增加这一行代码
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


# 适用于当网页加载完成后，如果需要有一个 click 动作（切换到一个非URL访问的section时），定义这个内容
# added by laigen , 2020.06.19
KEY_SELECTOR_OF_LOAD_FINISHED_CLICK = "selector_of_load_finished_click"
# 用于提取表格内容的数据
KEY_TABLE_EXTRACT_META = "table_extract_meta"

# 取数据的 next link 按钮
KEY_NEXT_LINK = "selector_of_next_link"

# table 最多取多少行数据
KEY_MAX_TABLE_ROWS = "max_table_rows"

KEY_ADDITIONAL_KW_SELECTOR = "additional_kw_selector"

KEY_PUBLISH_TIME_PREPROCESS = "publish_time_preprocess"

KEY_ARTICLE_SITE = "article_site"

KEY_RANDOM_SLEEP = "random_sleep"

# 某种情况下，真正要访问的页面并不是第一个所打开的页面，此时需要先进行一次页面跳转
# 该 Selector 适用于通过 click 的方式，可能会弹出一个新的网页。此时必须先获取到该 url，然后通过 browser.navigate 的方式导航到新的网页
KEY_REDIRECT_ELE_SELECTOR = "redirect_ele_selector"
KEY_REDIRECT_ELE_ATTR = "redirect_ele_attr"

ALL_ADDITIONAL_KEYS = [KEY_SELECTOR_OF_LOAD_FINISHED_CLICK, KEY_TABLE_EXTRACT_META, KEY_NEXT_LINK, KEY_MAX_TABLE_ROWS,
                       KEY_ADDITIONAL_KW_SELECTOR, KEY_PUBLISH_TIME_PREPROCESS, KEY_ARTICLE_SITE, KEY_RANDOM_SLEEP,
                       KEY_REDIRECT_ELE_SELECTOR, KEY_REDIRECT_ELE_ATTR]

# 为了避免 uipath 出错，准备了一个空的 cfg dict 用于拼接错误信息返回
ERR_CFG = {"name": "error", "url": "", "keyword": ""}


def _py_activities_path() -> str:
    return os.path.join(os.environ.get("GS_PY_ACTIVITIES_PATH", "D:\work\gs-activities"), "gs_activities")


from xml.etree import cElementTree as ElementTree


class XmlListConfig(list):
    def __init__(self, aList):
        for element in aList:
            if element:
                # treat like dict
                if len(element) == 1 or element[0].tag != element[1].tag:
                    self.append(XmlDictConfig(element))
                # treat like list
                elif element[0].tag == element[1].tag:
                    self.append(XmlListConfig(element))
            elif element.text:
                text = element.text.strip()
                if text:
                    self.append(text)


class XmlDictConfig(dict):
    def __init__(self, parent_element):
        if parent_element.items():
            self.update(dict(parent_element.items()))
        for element in parent_element:
            if element:
                # treat like dict - we assume that if the first two tags
                # in a series are different, then they are all different.
                if len(element) == 1 or element[0].tag != element[1].tag:
                    aDict = XmlDictConfig(element)
                # treat like list - we assume that if the first two tags
                # in a series are the same, then the rest are the same.
                else:
                    # here, we put the list in dictionary; the key is the
                    # tag name the list elements all share in common, and
                    # the value is the list itself
                    aDict = {element[0].tag: XmlListConfig(element)}
                # if the tag has attributes, add those to the dict
                if element.items():
                    aDict.update(dict(element.items()))
                self.update({element.tag: aDict})
            # this assumes that if you've got an attribute in a tag,
            # you won't be having any text. This may or may not be a
            # good idea -- time will tell. It works for the way we are
            # currently doing XML configuration files...
            elif element.items():
                self.update({element.tag: dict(element.items())})
            # finally, if there are no child tags and no attributes, extract
            # the text
            else:
                self.update({element.tag: element.text})


def _append_missing_fields(rlt_dict):
    for k in ALL_ADDITIONAL_KEYS + ["kw_input_selector", "no_data_selector"]:
        if k not in rlt_dict:  # 新增加的内容项，避免把所有的 cfg 文件都改一次，这里填入缺省值
            rlt_dict[k] = ""


def get_web_action_cfg(cfg_name: str, kw: str, additional_kw: str = "") -> str:
    # 先做简单的测试，以后将读取配置文件后返回

    # cfg_name 形如 social/twitter
    category, file_name = tuple(cfg_name.split("/"))
    # NOTE： os.path.dirname(os.path.abspath(__file__)) 这种方式无法得到 py 文件在 uipath 中执行的正确路径，该 py 文件会被 copy 到一个发布环境执行
    js_file = os.path.join(_py_activities_path(), "general_web_actions", category,
                           f"{file_name}.xml")
    if not os.path.exists(js_file):
        ret = ERR_CFG.copy()
        ret["error"] = f"{js_file} is not existed!"
        _append_missing_fields(ret)
        return json.dumps(ret)
    # import codecs
    # with codecs.open(js_file, "r", "utf-8-sig") as f:
    #     ret_cfg = json.load(f)

    tree = ElementTree.parse(js_file)
    root = tree.getroot()
    ret_cfg = XmlDictConfig(root)

    # kw in url encoder
    if ret_cfg["url"].find("{kw}") >= 0:
        from urllib import parse
        ret_cfg["url"] = ret_cfg["url"].format(kw=parse.quote_plus(kw))

    # ret_cfg["keyword"] = f"{kw}[[k(enter)]]"
    ret_cfg["keyword"] = f"{kw}\r\n"  # NOTE: 目前使用 SimulateType 的方式， [k(enter)] 会被当做普通字符，所以用 回车的 ASCII
    ret_cfg["error"] = ""  # 这里保留出错的信息，比如 无效的 cfg_name 等，便于 uipath 进行处理
    _append_missing_fields(ret_cfg)
    return json.dumps(ret_cfg)


if __name__ == "__main__":
    print(get_web_action_cfg("structure_data/consensus_estimates_by_investing_dot_com", "AAPL", ""))
