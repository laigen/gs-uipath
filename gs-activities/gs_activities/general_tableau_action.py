# -*- coding: utf-8 -*-

# ALERT : py 文件中出现 """ 引用的 comment ，在 uipath 的 "load python script"的activity 中会出现 load error

# tableau action 分几个步骤
# a) click dashboard tab
# b) [loop] find textbox and input , then click enter

import sys
import os
import json

# 根据 https://docs.uipath.com/activities/docs/load-script 中的描述，增加这一行代码
sys.path.append(os.path.dirname(os.path.realpath(__file__)))

ERR_CFG = {
    "tab_idx": 1,
    # "industry": "<wnd app='tableau.exe' cls='Qt5QWindowIcon' title='Tableau - equity_analysis_v2' /><ctrl role='editable text' idx='3' />",
    # "sector": "<wnd app='tableau.exe' cls='Qt5QWindowIcon' title='Tableau - equity_analysis_v2' /><ctrl role='editable text' idx='5' />",
}


def _py_activities_path() -> str:
    return os.path.join(os.environ.get("GS_PY_ACTIVITIES_PATH", "D:\work\gs-activities"), "gs_activities")


def get_tableau_action_cfg(tb_file_name: str) -> str:
    js_file = os.path.join(_py_activities_path(), "general_tableau_actions", f"{tb_file_name}.json")
    if not os.path.exists(js_file):
        ret = ERR_CFG.copy()
        ret["error"] = f"{js_file} is not existed!"
        return json.dumps(ret)

    with open(js_file, "r") as f:
        ret_cfg = json.load(f)

    for k, v in ret_cfg.items():
        if isinstance(v, str) and v.find("{file_name}") >= 0:
            ret_cfg[k] = v.format(file_name=tb_file_name)
    ret_cfg["error"] = ""
    return json.dumps(ret_cfg)


if __name__ == "__main__":
    print(get_tableau_action_cfg("equity_analysis_v2"))
