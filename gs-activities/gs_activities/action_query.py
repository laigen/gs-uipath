# -*- coding: utf-8 -*-

# ALERT : py 文件中出现 """ 引用的 comment ，在 uipath 的 "load python script"的activity 中会出现 load error
# NOTE : 在 windows 中运行的 python ，考虑到 uipath 引用该 package 会有问题，尽量将相关的函数等，都写在一个 py 文件里

# 与来自于 DesktopEnv 的 action 相关的内容

import sys
from datetime import datetime
from typing import List, Optional, Mapping, Dict
import glob
import os
import json
import copy
import pickle

# 根据 https://docs.uipath.com/activities/docs/load-script 中的描述，增加这一行代码
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


# 遍历得到某一个文件夹下的文件内容
# NOTE： ui_path file monitor trigger 只能够捕获文件变动的事件信号，但是具体有哪些文件创建了，是无法得到的。
#         所以这里需要使用遍历查询的方法，得到变动的文件清单
def query_files_in_folder(path: str, pattern_filter: str = "*.*") -> List[str]:
    files = glob.glob(os.path.join(path, pattern_filter))
    return files


def create_path_if_not_exist(path: str):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


class ActionItem:
    # Action 的基本定义方式为：
    #   [workflow_name] str ， 调用的 workflow 名称，即 xaml 文件的路径位置及名称信息
    #   [paras] 当前 workflow 的参数对象，是一个 json 格式的文件内容
    #   [next_workflow_name] Optional[str] 下一个workflow 项的名称，适用通过将一些 workflow 拼接起来，完成一个软件的基本功能
    #                                       可以通过 List 的方式查询下一个，但在 python 中提供该信息，可以避免在 uipath 里进行计算

    def __init__(self, workflow_name: str, para: Optional[object] = None):
        self.workflow_name = workflow_name
        self.para = para

    def to_dict(self):
        return {
            "workflow_name": self.workflow_name,
            "para": self.para
        }


class Action:
    def __init__(self):
        self.act_id: str = None  # uuid
        self.creator_uuid: str = None  # uuid of creator
        self.act_time: datetime = None  # action generate time
        self.act_description: Optional[str] = None  # 描述 action 的一些信息。一般含有 action 的创建者信息， 用于 log 给人看
        self.act: List[ActionItem] = None  # 具体的 action 内容
        self.result_save_mongo: bool = True  # add by laigen , 2020.06.04
        self.no_output: bool = False  # add by laigen , 2020.06.05 , 一些 desktop env 不需要有 output

    def to_dict(self):
        return {
            "id": self.act_id,
            "creator": self.creator_uuid,
            "time": self.act_time.isoformat(),
            "description": self.act_description,
            "result_save_mongo": self.result_save_mongo,
            "no_output": self.no_output,
            "act": [a.to_dict() for a in self.act]
        }


def load_action(file_path: str) -> str:
    # 将 action 从本地文件中读取出来，并补充填入 next_workflow_name 的内容（如有）
    with open(file_path, "r") as json_file:
        act_obj = json.load(json_file)
    ls_new_act = list()
    for i in range(len(act_obj["act"])):
        curr_act = copy.copy(act_obj["act"][i])
        if i < len(act_obj["act"]) - 1:  # not last one
            curr_act["next_workflow_name"] = act_obj["act"][i+1]["workflow_name"]
        else:
            curr_act["next_workflow_name"] = None
        ls_new_act.append(curr_act)
    act_obj["act"] = ls_new_act
    return json.dumps(act_obj)


def generate_uuid() -> str:
    import uuid
    return uuid.uuid4().hex.upper()


def _data_exchange_path() -> str:
    # gs desktop env 与 uipath 之间的数据交换目录
    return os.environ.get("GS_UIPATH_DATA_EXCHANGE_PATH", "D:\\gs_uipath")


def _pc_info_file() -> str:
    return os.path.join(_data_exchange_path(), "machine", "pc_info.json")


def _md5_str(s: str) -> str:
    import hashlib
    return hashlib.md5(s.encode("utf-8")).digest().hex().upper()


def move_act_file(path: str, success: bool = True):
    # 将 act 文件挪到 log path 中，规则为：
    #  DATA_ROOT\logs\finished\act_{uuid}.js , 执行成功的 action
    #  DATA_ROOT\logs\error\act_{uuid}.js , 执行失败的 action
    target_path = os.path.join(_data_exchange_path(), "logs", "finished" if success else "error")
    if not os.path.exists(target_path):
        os.makedirs(target_path, exist_ok=True)
    file_name = os.path.split(path)[-1]
    os.rename(path, os.path.join(target_path, file_name))


def save_azure_text_ana_result(path: str, ana_txt: str, ana_js_result: str, extra_info: List[str]):
    file_path = os.path.join(path, f"{_md5_str(ana_txt)}.pkl")
    map_rlt = dict()
    if extra_info:
        if len(extra_info) == 4:
            # new List(of String)(new String() {doc,pk_field,pk_val,txt_field})
            map_rlt["doc"] = extra_info[0]
            map_rlt["pk_field"] = extra_info[1]
            map_rlt["pk_val"] = extra_info[2]
            map_rlt["txt_field"] = extra_info[3]
    map_rlt["txt_value"] = ana_txt
    map_rlt["ana_result"] = ana_js_result
    with open(file_path, "wb") as f:
        pickle.dump(map_rlt, f, protocol=4)
    return


# 因为 Desktop Env 和 gs_activities 之间没有 共用的 object ， 以下的 object 会 duplicate 一份
class MonitorPosition:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

    def __repr__(self):
        return f"({self.x},{self.y})-({self.x + self.width},{self.y + self.height})"

    def to_dict(self) -> Dict:
        return {"x": self.x, "y": self.y, "width": self.width, "height": self.height}

    @classmethod
    def from_dict(cls, dict_obj) -> 'MonitorPosition':
        return cls(dict_obj["x"], dict_obj["y"], dict_obj["width"], dict_obj["height"])


class Monitor:
    def __init__(self, name: str, row_idx: int, col_idx: int):
        self.name = name
        self.row_idx = row_idx
        self.col_idx = col_idx
        self.pos: MonitorPosition = None

    def __repr__(self):
        s = f"[{self.name}({self.row_idx},{self.col_idx})]"
        if self.pos is not None:
            s += str(self.pos)
        return s

    def to_dict(self) -> Dict:
        return {"name": self.name, "row_idx": self.row_idx, "col_idx": self.col_idx, "pos": self.pos.to_dict()}

    @classmethod
    def from_dict(cls, dict_obj) -> 'Monitor':
        obj = cls(dict_obj["name"], dict_obj["row_idx"], dict_obj["col_idx"])
        obj.pos = MonitorPosition.from_dict(dict_obj["pos"])
        return obj


class PCInfo:
    def __init__(self, account: str, machine: str, monitors: List[Monitor]):
        self.account: str = account
        self.machine: str = machine
        self.monitors: Mapping[str, Monitor] = {m.name: m for m in monitors}

    def to_dict(self) -> Dict:
        return {"account": self.account, "machine": self.machine,
                "monitors": [v.to_dict() for k, v in self.monitors.items()]}

    @classmethod
    def from_dict(cls, dict_obj) -> 'PCInfo':
        return cls(dict_obj["account"], dict_obj["machine"],
                   [Monitor.from_dict(sub_dict) for sub_dict in dict_obj["monitors"]])


def abs_distance(x1: int, y1: int, x2: int, y2: int) -> float:
    from math import sqrt
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def mapping_monitor_name_2_position(pos_list: List[str]):
    path_env_info = os.path.join(_data_exchange_path(), "machine")
    if not os.path.exists(path_env_info):
        os.makedirs(path_env_info, exist_ok=True)

    # 将 monitor name 与 position 进行映射，并保存到相应的配置化文件
    ls_monitors_pos = [MonitorPosition(*map(lambda p: int(p), x.split(","))) for x in pos_list]
    # print(ls_monitors_pos)
    machine_js = os.path.join(_data_exchange_path(), "machine.json")
    # TODO: machine.json 文件不存在时候的报错
    assert os.path.exists(machine_js)
    with open(machine_js, "r") as json_file:
        machine_info = json.load(json_file)

    ls_all_monitor: List[Monitor] = list()
    all_monitor_names: List[List[str]] = machine_info["monitors"]
    for row_idx, m_in_row in enumerate(all_monitor_names, start=0):
        for col_idx, m in enumerate(m_in_row, start=0):
            if m:
                ls_all_monitor.append(Monitor(m, row_idx, col_idx))
    for monitor in ls_all_monitor:
        # monitor 不多，这里不做性能优化，比如：已经匹配的从排序列表中剔除
        monitor.pos = sorted(ls_monitors_pos, key=lambda pos: abs_distance(pos.x, pos.y, monitor.col_idx * 1920,
                                                                           monitor.row_idx * 1080))[0]
    pc_info = PCInfo(machine_info["account"], machine_info["machine"], ls_all_monitor)
    with open(_pc_info_file(), "w+") as f:
        json.dump(pc_info.to_dict(), f)


def monitor_count() -> int:
    if not os.path.exists(_pc_info_file()):
        return 0
    with open(_pc_info_file(), "r") as f:
        dict_obj = json.load(f)
    pc = PCInfo.from_dict(dict_obj)
    return len(pc.monitors)


def monitor_position(monitor_name: str) -> List[int]:
    err_return = [-10000, -10000]
    if not os.path.exists(_pc_info_file()):
        return err_return
    with open(_pc_info_file(), "r") as f:
        dict_obj = json.load(f)
    pc = PCInfo.from_dict(dict_obj)
    if monitor_name not in pc.monitors:
        return err_return
    else:
        return [pc.monitors[monitor_name].pos.x, pc.monitors[monitor_name].pos.y]


def account_and_machine() -> List[str]:
    err_return = ["", ""]
    if not os.path.exists(_pc_info_file()):
        return err_return
    with open(_pc_info_file(), "r") as f:
        dict_obj = json.load(f)
    pc = PCInfo.from_dict(dict_obj)
    return [pc.account, pc.machine]


# NOTE : 大段落的文字，许要经过 base64 之后，才能作为 cmd 的方式进行数据传递
def encode_base64_str_2_str(s: str) -> str:
    import base64
    return base64.b64encode(s.encode("utf-8")).decode("ascii")


def decode_base64_str_2_str(s: str) -> str:
    import base64
    return str(base64.b64decode(s.encode("ascii")), "utf-8")


def save_cmd_str(event_source: str, hot_key: str = None, symbol: str = None, begin: str = None, end: str = None,
                 freq: str = None, paragraph: str = None) -> str:
    import codecs
    path_env_info = os.path.join(_data_exchange_path(), "machine")
    if not os.path.exists(path_env_info):
        os.makedirs(path_env_info, exist_ok=True)
    ls_cmd_paras = []
    if event_source:
        ls_cmd_paras.append(f"--evt_source {encode_base64_str_2_str(event_source)}")
    if hot_key:
        ls_cmd_paras.append(f"--hot_key {hot_key}")
    if symbol:
        ls_cmd_paras.append(f"--symbol {symbol}")
    if begin:
        ls_cmd_paras.append(f"--begin {begin}")
    if end:
        ls_cmd_paras.append(f"--end {end}")
    if freq:
        ls_cmd_paras.append(f"--freq {freq}")
    if paragraph:
        ls_cmd_paras.append(f"--paragraph {encode_base64_str_2_str(paragraph)}")

    cmd = " ".join(ls_cmd_paras)
    with codecs.open(os.path.join(path_env_info, "cmd.txt"), "w", "utf-8-sig") as f:
        f.write(cmd)
    return cmd


def _machine_info() -> Dict:
    machine_js = os.path.join(_data_exchange_path(), "machine.json")
    assert os.path.exists(machine_js)
    with open(machine_js, "r") as json_file:
        machine_info = json.load(json_file)
    return machine_info


def dash_py_cmd() -> str:
    dict_machine = _machine_info()
    return dict_machine.get("ubuntu_cmd","ubuntu1804") + ' run python3 "' + "/".join([dict_machine.get("desktop_env"), "desktop_state", "dash_in_wsl.py"]) + '"'


def desktop_env_py_cmd() -> str:
    dict_machine = _machine_info()
    return dict_machine.get("ubuntu_cmd", "ubuntu1804") + ' run python3 "' + "/".join(
        [dict_machine.get("desktop_env"), "uipath", "action_srvs.py"]) + '"'


def selector_xml_extract_app(xml_str: str) -> str:
    try:
        import xml.etree.ElementTree as ET
        # 处理非单根的 xml 会有问题，所以这里修改字符串，使其符合单根的情况
        root = ET.fromstring(f"<root>{xml_str}</root>")
        return next(iter(root)).get("app")
    except Exception as ex:
        print(ex)
        return ""


def dump_kv_2_json(keys: List[str], vals: List[str], file_path: str):
    if len(keys) != len(vals):
        return
    dict_v = {}
    for k, v in zip(keys, vals):
        dict_v[k] = v
    with open(file_path, "w") as json_file:
        json.dump(dict_v, json_file)


if __name__ == "__main__":
    # print(query_files_in_folder("""D:\\gs_uipath\\p2u""", "*.csv"))
    # act_file = create_test_action(generate_uuid())
    # move_act_file(act_file, False)
    # print(load_action("D:\\gs_uipath\\p2u\\act_sample1.js"))
    # create_path_if_not_exist(f"D:\\gs_uipath\\u2p\\{generate_uuid()}")
    # save_azure_text_ana_result("D:\\gs_uipath\\debug", "a", "b")
    # mapping_monitor_name_2_position(["1912,1,1936,1056", "-16,1072,1936,1056", "-8,-8,1936,1056", "1904,1081,1936,1056"])

    # print(account_and_machine())

    # f_path = os.path.join(_data_exchange_path(), "machine","pc_info.json")
    # with open(f_path,"r") as f:
    #     dict_obj = json.load(f)
    # pc = PCInfo.from_dict(dict_obj)
    # print(pc.monitors)
    # save_clipboard_str("abcd")
    # print(desktop_env_py_cmd())
    # print(selector_xml_extract_app("<wnd app='emstart.exe' cls='CMainFrameUI' title='Choice金融终端' /><wnd ctrlname='QuoteMainView' /><wnd ctrlname='_CtrlQuoteMain' />"))
    # print(selector_xml_extract_app("<wnd app='notepad++.exe' cls='Notepad++' title='*C:\\Eastmoney\\Choice\\user\\login\\6150365919529052\\CustomBlockV2Ba*' /><wnd cls='Scintilla' idx='1' title='N' />"))
    # print(selector_xml_extract_app("<wnd app='tableau.exe' cls='Qt5QWindowIcon' title='Tableau - equity_analysis_v2' /><ctrl idx='207' role='client' />"))
    # print(selector_xml_extract_app("<html app='chrome.exe' title='python base64 string - Google Search' /><webctrl tag='BODY' />"))
    # dump_kv_2_json(["a", "b", "c"], ["1", "2", "中文"], "D:\\gs_uipath\\u2p\\general_desktop_browser_backend_action\\abc.js")
    pass
