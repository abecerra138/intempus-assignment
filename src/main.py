import uvicorn
import json
import multiprocessing
import traceback
import requests
import time
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from starlette.responses import JSONResponse
from argparse import ArgumentParser
from fastapi import Body, FastAPI, status as fastapi_status
from fastapi.staticfiles import StaticFiles

from utils import convert_intempus_projects, read_file_data, convert_local_projects
from intempus_models import UpdatedProjectEntry

################
# GLOBALS
################
PROJECT_DATA = "project_data.json"
INTEMPUS_API = "https://intempus.dk/web/v1"
INTEMPUS_API_KEY = "ec6417f864038d9b3b40fe1ea75b03a2cdf1bcd6"
USERNAME = "alexa.becerra99@gmail.com"
GET_HEADERS = {
    "Authorization": f"ApiKey {USERNAME}:{INTEMPUS_API_KEY}",
    "Accept": "application/json"
}
PUT_HEADERS = {
    "Authorization": f"ApiKey {USERNAME}:{INTEMPUS_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.DEBUG)

file_queue = None
file_listener = None
intempus_queue = None
local_listener = None
intempus_listener = None

################
# PROCESSES
################
def file_listener_process(queue):
    '''
    Updated local projects data file with queued data
    
    :param queue: json formatted projects data
    '''
    while True:
        try:
            #Queue contains json data
            data = queue.get()
            if data is None:
                break
            with open(PROJECT_DATA, "w") as file:
                file.write(data)
            print("Updated local projects data!")
            sys.stdout.flush()
        except Exception:
            traceback.print_exc()

def local_listener_process(queue):
    '''
    Process to push local changes to Intempus /case/{id}
    '''
    while True:
        try:
            #Queue contains python objects, not json Ex: [id, {"name": "test-name"}]
            project = queue.get()
            if project is None:
                break
            
            print(f"Queued changes to Intempus!':\n {project}'!")
            sys.stdout.flush()
            response = requests.put(
                f"{INTEMPUS_API}/case/{project[0]}/",
                headers=PUT_HEADERS,
                json=project[1])
            
            #Retry later
            if response.status_code != 200:
                print(f"Failed to push changes to Intempus!: {response.status_code}:{response.json()}")
                sys.stdout.flush()
                queue.put_nowait(project)
            #Validate return data
            else:
                print(f"Pushed changes to Intempus!")
                sys.stdout.flush()

        except Exception:
            traceback.print_exc()

def intempus_listener_process(queue):
    '''
    Process to check on Intempus /case/ for updated projects data
    '''
    logical_timestamp = None
    while True:
        if logical_timestamp:
            response = requests.get(
                f"{INTEMPUS_API}/case/?logical_timestamp__gt={logical_timestamp}", 
                headers=GET_HEADERS)
        else:
            response = requests.get(f"{INTEMPUS_API}/case/", headers=GET_HEADERS)
            logical_timestamp = response.headers.get("logical-timestamp")

        if response.status_code == 200:
            print(f"Intempus data recieved!:\n {response.json()}")
            sys.stdout.flush()
            intempus_projects = response.json().get("objects")
            local_projects = read_file_data(PROJECT_DATA)

            if not local_projects: #No local data to begin with
                queue.put_nowait(json.dumps(convert_intempus_projects(intempus_projects)))
            else:
                for entry in intempus_projects:
                    id = entry.get("id")

                    if id not in local_projects:
                        local_projects[id] = entry
                    else:
                        local_projects[id] | entry
                queue.put_nowait(json.dumps(local_projects))
        
        time.sleep(1 * 60)

################
# FastAPI
################

@asynccontextmanager
async def lifespan(app: FastAPI):
    global file_queue, file_listener, intempus_queue, local_listener, intempus_listener
    if file_queue is None:
        file_queue = multiprocessing.Queue(-1)
        file_listener = multiprocessing.Process(
            target = file_listener_process, 
            args = (file_queue,)
        )
        file_listener.daemon = True
        file_listener.start()
        logger.debug("File listener process started.")

    if intempus_queue is None:
        intempus_queue = multiprocessing.Queue(-1)
        local_listener = multiprocessing.Process(
            target = local_listener_process, 
            args = (intempus_queue,)
        )
        local_listener.daemon = True
        local_listener.start()
        logger.debug("Local listener process started.")

    intempus_listener = multiprocessing.Process(
        target = intempus_listener_process,
        args = (file_queue,))
    intempus_listener.daemon = True
    intempus_listener.start()
    logger.debug("Intempus listener process started.")
    
    yield

    if file_queue:
        file_queue.put_nowait(None)
    if file_listener and file_listener.is_alive():
        file_listener.join()

    if intempus_queue:
        intempus_queue.put_nowait(None)
    if local_listener and local_listener.is_alive():
        local_listener.join()
    if intempus_listener and intempus_listener.is_alive():
        intempus_listener.join()
        print("Listener process joined.")

app = FastAPI(
    title="Local API Service",
    lifespan=lifespan
)

@app.get(
    "/projects",
    tags=[],
    summary="Get list of projects",
    description="")
def get_projects():
    projects = {}
    try:
        projects = read_file_data(PROJECT_DATA)
    
    except Exception as e:
        message: str = ("Failed to fetch projects: {0}".format(repr(e)))
        return JSONResponse(
            status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"ErrorResponse":[{"detail": message}]}
        )

    return JSONResponse(
        status_code=fastapi_status.HTTP_200_OK,
        content={
            "projects": convert_local_projects(projects)
        }
    )

@app.put(
    "/projects/{id}",
    tags=[],
    summary="Update project",
    description="")
def update_project(id:str, project_data: UpdatedProjectEntry = Body(...)) -> JSONResponse:
    projects = {}
    try:
        projects = read_file_data(PROJECT_DATA)
        if id not in projects:
            raise Exception(f"Project id {id} does not exist!")
        else:
            non_none_values = {k: v for k, v in project_data.model_dump().items() if v is not None}
            projects[id] = projects[id] | non_none_values
            #logger.debug(projects)
            if file_queue:
               file_queue.put_nowait(json.dumps(projects))
            if intempus_queue:
                intempus_queue.put_nowait([id, non_none_values])


    except Exception as e:
        message: str = ("Failed to update project: {0}".format(repr(e)))
        return JSONResponse(
            status_code=fastapi_status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"ErrorResponse":[{"detail": message}]}
        )

    return JSONResponse(
        status_code=fastapi_status.HTTP_200_OK,
        content={
            "projects": convert_local_projects(projects)
        }
    )


def process_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-H", "--host", help="IP of host to run server", default="127.0.0.1"
    )
    parser.add_argument(
        "-p", "--port", help="Port to run server on", default=8001
    )
    args = parser.parse_args()

    settings = {
        "host": args.host,
        "log_level": "debug",
        "port": int(args.port),
        "reload": True,
        "workers": 4
    }
    return settings

def run():
    settings = process_args()
    uvicorn.run("main:app", **settings)