# intempus-assignment

## Purpose


## Design
This FastAPI server allows the user to GET and PUT changes to the projects data stored locally in `project_data.json`, while simultaneously running processes to handle the updating of the local data from Intempus.

Spawning from the server startup are 3 processes:

1. A file writer process to handle any changes queued to the local json file
2. A process to handle propagate local changes made up to Intempus
3. A process to fetch Intempus data and update the local json file as needed

Assumptions/Compromises/Time Constraints:
- User cannot POST a new project from the REST endpoints
- Set a time sleep of 60 seconds for how often to check Intempus for new data. Ideally this should be configurable
- Pytest cases for multiprocessing queue checks


## Deploy
In one terminal run the FastAPI server call with:
```bash
$ virtualenv -p /usr/bin/python3 <env name> ('venv' in this case)
$ source venv/bin/activate
$ pip install -r requirements.txt
$ cd src
$ python3 src/main -p 8002 (Port defaults to 8001 is not specified)
```

Open another terminal and make calls to the server:
GET:
Windows:
```bash
$ curl.exe -X GET http://127.0.0.1:8001/projects -H "Accept: application/json"
```
Linux:
```bash
$ curl -X GET http://127.0.0.1:8001/projects -H "Accept: application/json"
```

PUT:
Windows:
```bash
$ curl.exe -X PUT http://127.0.0.1:8001/projects/9584687 -H "Content-Type: application/json" -d "{\"name\":\"test-put\"}"
```

Linux:
```bash
$ curl -X PUT http://127.0.0.1:8001/projects/9584687 -H "Content-Type: application/json" -d '{"name":"test-put"}'
```

## Testing
Assuming the requirements were already installed above, run tests in root of project folder:
```bash
$ cd ..
$ python3 -m pytest
```
