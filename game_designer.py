import os
import shutil

# please type in the available OPENAI API KEY in the ""
os.environ["OPENAI_API_KEY"] = ""

from colorama import Fore

from camel.societies import RolePlaying
from camel.utils import print_text_animated
from camel.types import TaskType, ModelType
from ask_gpt import ask_gpt

project_document = None
agile_document = None
ui_document = None
code = None
test_report = None


def stage_create_task(task_prompt, role_taker, role_giver, code_type=None, task_type=None, turn_limit=4,
                      add_giver_msg=False):
    progress = []

    if task_type:
        task_type = TaskType.CODE
    else:
        task_type = TaskType.DEFAULT
    # language = "JavaScript"
    # domain = "Sociology"
    meta_dict = {"language": code_type}

    # camel will call openai api
    role_play = RolePlaying(role_taker, role_giver, task_prompt=task_prompt, model_type=ModelType.GPT_4_TURBO)

    # after each step, the conversation will be stored and remember the previous one
    # task_type=task_type, extend_sys_msg_meta_dicts=[meta_dict, meta_dict],
    # extend_task_specify_meta_dict=meta_dict)

    print(Fore.CYAN + f"Specified task prompt:\n{role_play.task_prompt}\n")

    turn_limit, count = turn_limit, 0
    msg, _ = role_play.init_chat()

    while count < turn_limit:
        count += 1
        #
        role_taker_resp, role_giver_resp = role_play.step(msg)

        print_text_animated(Fore.BLUE + f"{role_giver}:\n\n{role_giver_resp.msg.content}\n")
        print_text_animated(Fore.GREEN + f"{role_taker}:\n\n"f"{role_taker_resp.msg.content}\n")

        # also a checkpoint to interact， e.g., 上一轮，role_taker_resp（pm） design a 9*9 map
        # human can input some guide, concat to 'role_taker_resp.msg.content':

        progress.append(role_taker_resp.msg.content)
        if add_giver_msg:
            progress.append(role_giver_resp.msg.content)

        if "CAMEL_TASK_DONE" in role_giver_resp.msg.content:
            break

        msg = role_taker_resp.msg
    return progress


def lets_meeting(subject, resource, roles, round_limit=3):
    print(Fore.RED + f"Meeting begin, subject: {subject}\n")
    conversations = []
    prompt = f"Attend conversation meeting on subject: {subject}.\nGive your opinion and advice.\n\n***Meeting resources***\n\n{resource}\n\n"
    # using a host, roleplay to each roles once a turn
    #
    for i in range(round_limit):
        for role in roles:
            if conversations:
                turn_prompt = prompt + "\n\n***history conversation***\n\n" + "\n".join(conversations)
            else:
                turn_prompt = prompt
            # Meeting Host is the host, dialogue will be stored in the conversation at the end
            meeting_msg = stage_create_task(turn_prompt, role, f"Meeti+ng Host for {subject}", turn_limit=1,
                                            add_giver_msg=True)
            conversations.extend(meeting_msg)

    # add user intervention after each meeting
    convs = '\n'.join(conversations)
    # print(Fore.RED + f"Meeting is finish, here is coversations:\n{convs}")
    human = input("What's your opinion or instruction?")
    conversations.append(human)

    meeting_report = ask_gpt(
        "Convert the following conversation into a well formatted meeting report:\n\n" + '\n'.join(conversations))
    return meeting_report


def main(turn_id=1, req=None):
    """
    假设我有K个角色，以开发游戏为例，[user, pm, ac, uid, programmer, tester]
        1. 用户输入目标
        2. product owner self-chat明确目标
        3. 传递给scrum master进行调整成敏捷设计
        4. 敏捷设计的最小需求下发给Designer
        5. 设计+需求发给programmer
        6. tester进行检测
        7. 返回给po，获得用户反馈，进行下一轮

        记忆能力：
        1. 项目初始文档
        2. 敏捷式项目文档
        3. UI设计文档
        4. 开发的代码
        5. 测试报告
    """

    global project_document, agile_document, ui_document, code, test_report

    if turn_id == 1:
        task_prompt = input("Please shortly describe your pygame project:\n")
        print(Fore.YELLOW + f"Original task prompt:\n{task_prompt}\n")

        # turn=1, user input task prompt -> Product Owner -> project document

        # a list to save all the dialogue
        pm_msg = stage_create_task(
            f"{task_prompt} in pygame, in this stage, devise the project and write project document only.",
            "Product Owner", "User")
        # list to well-structured document
        project_document = ask_gpt(
            'Convert the following conversation into a well formatted project document:\n\n' + '\n'.join(pm_msg))
        print(Fore.YELLOW + f"Project document:\n{project_document}\n")

        # allow human to interact with the system
        # print('Please check project document, you can modify it')
        # input('Press any key to continue')
        # 1. save to file
        # 2. human edit file
        # 3. load document from file
        # 4. allow user give some guide to Scrum Master

        # perform a Backlog_Grooming_Meeting
        Backlog_Grooming_Meeting = lets_meeting(
            "Backlog Grooming Meeting, Discuss user stories to be implemented in this iteration.", project_document,
            ["Product Owner", "Scrum Master", "Programmer"])

        # perform a Sprint_Planning_Meeting
        Sprint_Planning_Meeting = lets_meeting(
            "Sprint Planning Meeting, Project Manager creates Product Backlog, Scrum Master selects the Backlog for this iteration and estimate the workload for this iteration.", Backlog_Grooming_Meeting,
            ["Product Owner", "Scrum Master", "Programmer"])

        # turn=2, project document -> Scrum Master -> agile design
        # input project document
        task_prompt = 'Communicate the project document to Scrum Master, simplify & split into smaller stage, then give agile version of document, aim to fast demo\n\n***The following is the project document***\n\n' + project_document + "\n\n***The following is the meeting report of Sprint_Planning_Meeting***\n\n" + Sprint_Planning_Meeting
        #load the previous document
        agile_msg = stage_create_task(task_prompt, "Scrum Master", "Product Owner")
        agile_document = ask_gpt(
            'Convert the following conversation into a well formatted agile document:\n\n' + '\n'.join(agile_msg))
        print(Fore.YELLOW + f"Agile document:\n{agile_document}\n")

        # turn=3, agile document -> designer -> design document
        task_prompt = 'Devise the UI design document, aim to fast demo\n\n***The following is the agile version of project document***\n\n' + agile_document
        ui_msg = stage_create_task(task_prompt, "UI Designer", "Scrum Master")
        ui_document = ask_gpt(
            'Convert the following conversation into a well formatted UI document:\n\n' + '\n'.join(ui_msg))
        print(Fore.YELLOW + f"UI document:\n{ui_document}\n")

        # if needed, we can roleplay between designer and manager to make sure the design is good enough
        # turn=4, agile document + design document -> developer -> code
        task_prompt = 'Develop the game using pygame, the game code should complete and runnable, and in a single source file.\nThe code must fully implemnt the game requirement.\n\n***The following is the UI design document***\n\n' + ui_document + '\n\n***The following is the agile version of project document***\n\n' + agile_document
        dev_msg = stage_create_task(task_prompt, "Computer Programmer", "Product Owner", code_type='Python',
                                    task_type=TaskType.CODE, turn_limit=8)
        code = ask_gpt('Convert the following conversation into a well formatted code:\n\n' + '\n'.join(dev_msg))
        print(Fore.YELLOW + f"Code:\n{code}\n")

        # turn=5, code -> tester -> test report
        task_prompt = 'Check the game codes, give test cases and unit test, write test report.\n\n***The following is the UI design document***\n\n' + ui_document + '\n\n***The following is the agile version of project document***\n\n' + agile_document + '\n\n***The following is the full cods***\n\n' + code
        test_msg = stage_create_task(task_prompt, "Program Tester", "Product Owner")
        test_report = ask_gpt(
            'Convert the following conversation into a well formatted test report:\n\n' + '\n'.join(test_msg))
        print(Fore.YELLOW + f"Test report:\n{test_report}\n")

        # perform a Sprint_Planning_Meeting
        Retrospective_Meeting = lets_meeting(
            "Retrospective Meeting, The team shows the result of this iteration to Product Owner, getting comments and reply.",
            ui_document + '\n' + code + '\n' + test_report,
            ["Product Owner", "UI Designer", "Programmer", "Program Tester"])


    else:
        # using existing documents and codes to start a new turn
        print(Fore.YELLOW + f"New requirements:\n{req}\n")

        # turn=1, user input task prompt -> Product Owner -> project document
        pm_msg = stage_create_task(
            f"Based on new requirements:{req}, update the devise of the project and update project document.\n\n***old project document***\n\n{project_document}",
            "Product Owner", "User")
        project_document = ask_gpt(
            'Convert the following conversation into a well formatted project document:\n\n' + '\n'.join(
                pm_msg) + '\n\nYou need also combine the old project document.\n\n***old project document***\n\n' + project_document)
        print(Fore.YELLOW + f"Project document:\n{project_document}\n")

        # perform a Backlog_Grooming_Meeting
        Backlog_Grooming_Meeting = lets_meeting(
            "Backlog Grooming Meeting, Discuss user stories to be implemented in this iteration.", project_document,
            ["Product Owner", "Scrum Master", "Programmer"])

        # perform a Sprint_Planning_Meeting
        Sprint_Planning_Meeting = lets_meeting(
            "Sprint Planning Meeting, Project Manager creates Product Backlog, Scrum Master selects the Backlog for this iteration and estimate the workload for this iteration.", Backlog_Grooming_Meeting,
            ["Product Owner", "Scrum Master", "Programmer"])

        # turn=2, project document -> Scrum Master -> agile design
        task_prompt = f'Based on new requirements:{req}, Communicate the project document to Scrum Master, simplify & split into smaller stage, then give agile version of document, aim to fast demo\n\n***The following is the project document***\n\n' + project_document + "\n\n***The following is the meeting report of Sprint_Planning_Meeting***\n\n" + Sprint_Planning_Meeting
        agile_msg = stage_create_task(task_prompt, "Scrum Master", "Product Owner")
        agile_document = ask_gpt(
            'Convert the following conversation into a well formatted agile document:\n\n' + '\n'.join(agile_msg))
        print(Fore.YELLOW + f"Agile document:\n{agile_document}\n")

        # turn=3, agile document -> designer -> design document
        task_prompt = f'Based on new requirements:{req}, Devise the UI design document, aim to fast demo\n\n***The following is the agile version of project document***\n\n' + agile_document
        ui_msg = stage_create_task(task_prompt, "UI Designer", "Scrum Master")
        ui_document = ask_gpt(
            'Convert the following conversation into a well formatted UI document:\n\n' + '\n'.join(ui_msg))
        print(Fore.YELLOW + f"UI document:\n{ui_document}\n")

        # if needed, we can roleplay between designer and manager to make sure the design is good enough
        # turn=4, agile document + design document -> developer -> code
        task_prompt = f'Based on new requirements:{req}, Develop the game using pygame, the game code should complete and runnable, and in a single source file.\nThe code must fully implemnt the game requirement.\n\n***The following is the UI design document***\n\n' + ui_document + '\n\n***The following is the agile version of project document***\n\n' + agile_document + f'\n\n***The following is the existing codes***\n\n{code}'
        dev_msg = stage_create_task(task_prompt, "Computer Programmer", "Product Owner", code_type='Python',
                                    task_type=TaskType.CODE, turn_limit=8)
        code = ask_gpt('Convert the following conversation into a well formatted code:\n\n' + '\n'.join(dev_msg))
        print(Fore.YELLOW + f"Code:\n{code}\n")

        # turn=5, code -> tester -> test report
        task_prompt = 'Write test cases and unit test, check if the game codes has bug.\n\n***The following is the UI design document***\n\n' + ui_document + '\n\n***The following is the agile version of project document***\n\n' + agile_document + '\n\n***The following is the full cods***\n\n' + code
        test_msg = stage_create_task(task_prompt, "Program Tester", "Product Owner")
        test_report = ask_gpt(
            'Convert the following conversation into a well formatted test report:\n\n' + '\n'.join(test_msg))
        print(Fore.YELLOW + f"Test report:\n{test_report}\n")

        Retrospective_Meeting = lets_meeting(
            "Retrospective Meeting, The team shows the result of this iteration to Product Owner, getting comments and reply.",
            ui_document + '\n' + code + '\n' + test_report,
            ["Product Owner", "UI Designer", "Programmer", "Program Tester"])

    # save all reports and codes into files
    # remove if exist
    if os.path.exists(f'results/{turn_id}'):
        shutil.rmtree(f'results/{turn_id}')
    os.mkdir(f'results/{turn_id}')
    with open(f'results/{turn_id}/project_document.md', 'w') as f:
        f.write(project_document)
    with open(f'results/{turn_id}/agile_document.md', 'w') as f:
        f.write(agile_document)
    with open(f'results/{turn_id}/ui_document.md', 'w') as f:
        f.write(ui_document)
    with open(f'results/{turn_id}/code.py', 'w') as f:
        f.write(code)
    with open(f'results/{turn_id}/test_report.md', 'w') as f:
        f.write(test_report)
    with open(f'results/{turn_id}/Backlog_Grooming_Meeting.md', 'w') as f:
        f.write(Backlog_Grooming_Meeting)
    with open(f'results/{turn_id}/Sprint_Planning_Meeting.md', 'w') as f:
        f.write(Sprint_Planning_Meeting)
    with open(f'results/{turn_id}/Retrospective_Meeting.md', 'w') as f:
        f.write(Retrospective_Meeting)


if __name__ == '__main__':
    turn = 1
    main(turn_id=turn)

    second = input("Do you need another round? (y/n)")
    second = second.lower()
    while second == 'y':
        turn += 1
        print(f"Please check the current version of project in: results/{turn - 1}")
        new_req = input("Please tell the modification or new requirements: ")
        main(turn_id=turn, req=new_req)
        second = input("Do you need another round? (y/n)")
        second = second.lower()
