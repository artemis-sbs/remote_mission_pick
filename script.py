import sbslibs
from  sbs_utils.handlerhooks import *
from sbs_utils.gui import Gui
from sbs_utils.mast.maststorypage import StoryPage
from sbs_utils.mast.maststory import MastStory

from sbs_utils.mast.mast import Mast
from sbs_utils.mast.pollresults import PollResults
from sbs_utils.mast.label import label

from sbs_utils.procedural.gui import gui_row, gui_icon, gui, gui_section, gui_text, gui_content, gui_change, gui_update, gui_button, gui_represent
from sbs_utils.procedural.execution import AWAIT, get_shared_variable, jump, set_shared_variable
from sbs_utils.procedural.timers import timeout
from sbs_utils.procedural.cosmos import sim_create, sim_resume
from sbs_utils.procedural.query import safe_int
from sbs_utils.widgets.listbox import list_box_control
import os
from sbs_utils.fs import get_missions_dir, get_mission_name

def get_mission_list():
    this_mission = get_mission_name()
    missions = []
    dir = get_missions_dir()
    file_list = os.listdir(dir)
    for file in file_list:
        if not os.path.isdir(os.path.join(dir, file)):
            continue
        if file == this_mission:
            continue
        if os.path.isfile(os.path.join(dir, file, "description.txt")):
            file1 = open(os.path.join(dir, file, "description.txt"), 'r')
            lines = file1.readlines()
            while len(lines) < 3:
                lines.append("")
            mission = {"name": file, 
                    "category":lines[0],
                    "desc":lines[1],
                    "icons":[] }
            for i in lines[2:]:
                i = i.split()
                
                if len(i)>=2:
                    # icon = {"index": safe_int(i[0]), "color": i[1]}
                    icon = f"icon_index:{safe_int(i[0])};color:{i[1]};"
                    mission["icons"].append(icon)

            missions.append(mission)
    return missions

                


@label()
def main_gui():
    #yield PollResults.OK_RUN_AGAIN
    # gui_reroute_server(server_start)


    lb_sec = gui_section("area: 0,15,40,100")
    sbs.suppress_client_connect_dialog(0)
    sim_create()
    sim_resume()
    
    missions = get_mission_list()
    mission_name = missions[0]["name"]
    #set_shared_variable('mission', mission_name)
    
    lb_missions = list_box_control(
                missions, 
                text=lambda x: f"{x['name']}",
                title=lambda : "text:missions;justify:center;",
                icon=lambda x: x['icons'],
                select=True,
                background="#1571",
                title_background="#1575",
                convert_value=lambda x: f"{x['name']}"
                )
    
        

    def select():
        #mission = get_variable('mission')
        mission_sel = lb_missions.get_selected()
        if len(mission_sel) >0:
            mission = mission_sel[0]

            set_shared_variable("mission", mission.get('name'))

            #update_icons(mission)
            gui_update("cat", f"text: {mission['category']}")
            gui_update("desc", f"text: {mission['desc']}")
        yield PollResults.OK_YIELD

    gui_content(lb_missions, var="mission")
    lb_missions.set_value(mission_name)
    gui_change("mission", select) 

    #
    # Property column
    #
    gui_section("area: 45,15,100,100")

    cat = missions[0]["category"] if len(missions)!=0 else "no missions"
    desc = missions[0]["desc"] if len(missions)!=0 else "no missions"

    gui_row(style="row-height: 45px")
    gui_text(f"text: {cat}", style="tag:cat;")
    gui_row(style="row-height: 45px")
    
    # create_icons(missions[0])

    

    gui_row()
    gui_text(f"text: {desc}", style="tag:desc;padding:0,20px;")
    
    yield AWAIT(gui({"start": start}))

def update_icons(mis):
    for c in range(6):
        if c < len(mis['icons']):
            i = mis['icons'][c]
            gui_update(f"icon-{c}", f"icon_index: {i['index']};color:{i['color']};")
        else:
            gui_update(f"icon-{c}", f"icon_index:1000;color:#0000;")

def create_icons(mis):
    for c in range(6):
        if c < len(mis['icons']):
            i = mis['icons'][c]
        #    gui_icon(f"icon_index: {i['index']};color:{i['color']};",style=f"tag: icon-{c};")
        else:
            i = {"index": 1000, "color": "#0000"}
        #     gui_text(f"",style=f"tag: icon-{c};")
        gui_icon(i,style=f"tag: icon-{c};")
    


@label()
def start():
    mission = get_shared_variable("mission")
    if mission is not None:
        sbs.run_next_mission(mission)

    yield AWAIT(gui({"back": main_gui}, timeout=timeout(10)))
    yield jump(main_gui)
    


class SimpleAiPage(StoryPage):
    story = MastStory()
    main_server = main_gui
    main_client = main_gui



Mast.include_code = True

Gui.server_start_page_class(SimpleAiPage)
Gui.client_start_page_class(SimpleAiPage)
