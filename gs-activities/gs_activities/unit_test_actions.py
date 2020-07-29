# -*- coding: utf-8 -*-

# 创建与 unit test 有关的 action
import json
from datetime import datetime

from gs_activities.action_query import Action, generate_uuid, ActionItem


def create_test_action(uuid: str) -> str:
    action = Action()
    action.act_id = uuid
    action.creator_uuid = generate_uuid()
    action.act_time = datetime.now()
    action.act_description = "action for test"
    action.act = [ActionItem("browser_kw_search_actions/act_batch_google_news_search", para=["Trump Speech", "Trump Hiring"])]
    test_file = f"D:\\gs_uipath\\p2u\\act_{uuid}.js"
    with open(test_file, "w") as json_file:
        json.dump(action.to_dict(), json_file)
    return test_file


def create_seeking_alpha_special_column_action() -> Action:
    test_action = Action()
    test_action.act_id = "seeking_alpha_special_columns_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "query some special columns in seeking alpha"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "seeking_alpha",
                         "function": "special_columns",
                         "ls_paras": ["market-outlook/todays-market",
                                      "stock-ideas/long-ideas",
                                      "market-outlook/economy"]
                         }
                   )
    ]
    return test_action


def create_seeking_alpha_author_info() -> Action:
    test_action = Action()
    test_action.act_id = "seeking_alpha_author_info_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "query author info in seeking alpha"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "seeking_alpha",
                         "function": "author_info",
                         "ls_paras": [
                                      "value-kicker",
                                      # "investing-theory",
                                      # "the-value-trend"
                                      ]
                         }
                   )
    ]
    return test_action


def create_seeking_alpha_symbol_summary() -> Action:
    test_action = Action()
    test_action.act_id = "seeking_alpha_symbol_summary_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "query symbol summary in seeking alpha"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "seeking_alpha",
                         "function": "symbol_summary",
                         "pages": 3,
                         "ls_paras": [
                                        "PDD",
                                      # "NFLX",
                                      # "STX"
                         ]
                         }
                   )
    ]
    return test_action


def create_seeking_alpha_kw_search() -> Action:
    test_action = Action()
    test_action.act_id = "seeking_alpha_kw_search_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "kw search in seeking alpha"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "seeking_alpha",
                         "function": "kw_search",
                         "pages": 3,
                         "ls_paras": [
                                        "trump oil",
                                      "luckin fraud",
                                      "gsx fraud"]
                         }
                   )
    ]
    return test_action


def create_seeking_alpha_earning_calendar() -> Action:
    test_action = Action()
    test_action.act_id = "seeking_alpha_earning_calendar"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "earning_calendar in seeking alpha"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "seeking_alpha",
                         "function": "earning_calendar"
                         }
                   )
    ]
    return test_action


def create_twitter_kw_search() -> Action:
    test_action = Action()
    test_action.act_id = "twitter_kw_search_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "kw search in twitter"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "twitter",
                         "function": "kw_search",
                         "pages": 1000,
                         "ls_paras": [
                                    "(from:realDonaldTrump)",
                                      # "oil (from:realDonaldTrump)",
                                      # "luckin fraud min_retweets:10",
                                      # "gsx fraud min_retweets:10"
                                    ]
                         }
                   )
    ]
    return test_action


def create_twitter_following() -> Action:
    test_action = Action()
    test_action.act_id = "twitter_following_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "kw search in twitter"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "twitter",
                         "function": "following",
                         "pages": 3,
                         "ls_paras": [
                             "realDonaldTrump",
                             "TechCrunch"
                         ]
                         }
                   )
    ]
    return test_action


def create_azure_txt_ana() -> Action:
    test_action = Action()
    test_action.act_id = "azure_txt_ana_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "text analytics use azure"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "azure",
                         "function": "txt_ana",
                         "ls_paras": [
                             {
                                 "doc": "Article",
                                 "pk_field": "uuid",
                                 "pk_val": "BD9341B99C800299E8302C60294F01A1",
                                 "txt_field": "title",
                                 "txt_value": """The spectacular implosion of Luckin Coffee in an accounting fraud has renewed a push in the United States to cut Chinese companies off from Wall Street"""
                             },
                             {
                                 "doc": "Article",
                                 "pk_field": "uuid",
                                 "pk_val": "04CF9288835D237EAAF8ACF179BB4ACE",
                                 "txt_field": "abstract",
                                 "txt_value": """GSX Stock: Berger Montague Investigates Securities Fraud Class Action Claims Against GSX Techedu...
PHILADELPHIA, April 29, 2020 /PRNewswire via COMTEX/ -- PHILADELPHIA, April 29, 2020 /PRNewswire/ -- Berger Montague is investigating securities fraud claims...
marketwatch.com"""

                             },
                             {
                                 "doc": "UserInTwitter",
                                 "pk_field": "user_id",
                                 "pk_val": "Yubico",
                                 "txt_field": "intro",
                                 "txt_value": """Yubico sets new world standards for simple, secure login, preventing unauthorized access to computers, servers, and internet accounts."""
                             }
                         ]
                         }
                   )
    ]
    return test_action


def create_google_news_search() -> Action:
    test_action = Action()
    test_action.act_id = "google_news_search_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "news search in google"
    test_action.act = [
        ActionItem("browser_kw_search_actions/act_multi_nlp_task",
                   para={"site": "google_news",
                         "function": "kw_search",
                         "pages": 5,
                         "ls_paras": [
                                    "拼多多"
                                      # "trump oil",
                                      # "luckin fraud",
                                      # "gsx fraud"
                                ]
                         }
                   )
    ]
    return test_action


def create_detect_monitors() -> Action:
    test_action = Action()
    test_action.act_id = "detect_monitors"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "detect all monitors "
    test_action.act = [
        ActionItem("DesktopRPA/act_desktop_action_dispatch",
                   para={"action": "detect_monitors"}
                   )
    ]
    test_action.result_save_mongo = False
    test_action.no_output = True
    return test_action


def create_general_desktop_browser_action() -> Action:
    test_action = Action()
    test_action.act_id = "general_desktop_browser_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "general_desktop_browser_action"
    test_action.act = [
        ActionItem("DesktopRPA/act_desktop_action_dispatch",
                   para={"action": "general_web_app_on_monitor",
                         "monitor": "DispA2",
                         "tooltip": "hello_world",
                         "cfg_name": "utility/google_translate",
                         "kw": "自然语言",
                         "additional_kw": ""}
                   )
    ]
    test_action.result_save_mongo = False
    test_action.no_output = True
    return test_action


def create_general_desktop_browser_backend_action(cfg_name: str, kw: str = "", additional_kw: str = "") -> Action:
    test_action = Action()
    test_action.act_id = "general_desktop_browser_backend_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "general_desktop_browser_backend_action"
    test_action.act = [
        ActionItem("DesktopRPA/act_desktop_action_dispatch",
                   para={"action": "general_desktop_browser_backend_action",
                         "cfg_name": cfg_name,
                         "kw": kw,
                         "additional_kw": additional_kw
                         }
                   )
    ]
    test_action.result_save_mongo = True
    test_action.no_output = False
    return test_action


def create_cleanup_one_monitor() -> Action:
    test_action = Action()
    test_action.act_id = "cleanup_one_monitor"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "cleanup_one_monitor"
    test_action.act = [
        ActionItem("DesktopRPA/act_desktop_action_dispatch",
                   para={"action": "cleanup_one_monitor",
                         "monitor": "DispA2"}
                   )
    ]
    test_action.result_save_mongo = False
    test_action.no_output = True
    return test_action


def create_tableau_action() -> Action:
    test_action = Action()
    test_action.act_id = "tableau_action"
    test_action.creator_uuid = generate_uuid()
    test_action.act_time = datetime.now()
    test_action.act_description = "tableau_action"
    test_action.act = [
        ActionItem("DesktopRPA/act_desktop_action_dispatch",
                   para={"action": "tableau_act",
                         "tb_file_name": "equity_analysis_v2",
                         "industry": "Telecom Services",
                         "sector": "Communication Services"}
                   )
    ]
    test_action.result_save_mongo = False
    test_action.no_output = True
    return test_action


if __name__ == "__main__":
    # action = create_seeking_alpha_special_column_action()
    # action = create_seeking_alpha_author_info()
    # action = create_seeking_alpha_symbol_summary()
    # action = create_seeking_alpha_kw_search()
    # action = create_seeking_alpha_earning_calendar()
    # action = create_twitter_kw_search()
    # action = create_twitter_following()
    # action = create_azure_txt_ana()
    # action = create_google_news_search()

    action = create_general_desktop_browser_backend_action("structure_data/consensus_estimates_by_investing_dot_com",
                                                           "TSLA", "")

    # action = create_general_desktop_browser_backend_action("us_fin_web/xueqiu_by_symbol", "GSX", "欺诈")

    # for desktop
    # action = create_detect_monitors()
    # action = create_general_desktop_browser_action()
    # action = create_cleanup_one_monitor()
    # action = create_tableau_action()

    test_file = f"D:\\gs_uipath\\debug\\unit_test_acts\\{action.act_id}.js"
    with open(test_file, "w") as json_file:
        json.dump(action.to_dict(), json_file)

