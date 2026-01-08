import json


def convert_intempus_projects(projects: list):
    converted_projects = {}
    for project in projects:
        converted_projects[project.get("id")] = project

    return converted_projects

def convert_local_projects(projects: dict):
    if projects:
        return list(projects.values())
    else:
        return []


def read_file_data(file):
    try:
        local_projects = {}
        with open(file, "r") as file:
            local_projects = json.load(file)

        return local_projects
    except json.decoder.JSONDecodeError:
        return {}
    except Exception as e:
        print("Error reading local projects file!")
        raise

