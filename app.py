import argparse
import json
import logging
import subprocess
import time
from enum import Enum
from typing import TypedDict

from flask import Flask, jsonify, request

# Basically copy cat of
# https://www.truenas.com/community/threads/chart-application-restart-flow.104390/

# Don' take this script too seriously as this was hacked together for my usecase only

app = Flask(__name__)
JobID = str


class AppStatus(Enum):
    ACTIVE = "ACTIVE"
    STOPPED = "STOPPED"
    DEPLOYING = "DEPLOYING"


class JobStatus(Enum):
    WAITING = "WAITING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"


class Switch(Enum):
    ON = 1
    OFF = 0


class RestartRequest(TypedDict):
    uri: str
    username: str
    password: str
    api_key: str
    service_id: str


def get_app_status(base_command: str, service_id: str) -> AppStatus:
    process = f'{base_command} call chart.release.query \'[["id","=","{service_id}"]]\''
    result = json.loads(subprocess.getoutput(process))
    return AppStatus(result[0]["status"])


def get_job_status(base_command: str, job_id: JobID) -> JobStatus:
    process = f'{base_command} call core.get_jobs \'[["id", "=",{job_id}]]\''
    result = json.loads(subprocess.getoutput(process))
    return JobStatus(result[0]["state"])


def switch_service(base_command: str, service_id: str, action: Switch) -> None:
    logging.info(f"Will scale service {service_id} to {action.value}.")
    payload = json.dumps({"replica_count": action.value})
    process = f"{base_command} call chart.release.scale '{service_id}' '{payload}'"
    job_id: JobID = subprocess.getoutput(process)
    logging.info(f"Created scale job {job_id}")
    while True:
        if get_job_status(base_command, job_id) in [
            JobStatus.WAITING,
            JobStatus.RUNNING,
        ]:
            logging.info(f"Waiting for Job {job_id} to finish")
            time.sleep(0.5)
        else:
            logging.info(f"Job {job_id} succeeded")
            break


def restart_service(base_command: str, service_id: str):
    if get_app_status(base_command, service_id) not in [
        AppStatus.ACTIVE,
        AppStatus.DEPLOYING,
    ]:
        logging.error(f"Service {service_id} is not active/deploying.")
        return
    switch_service(base_command, service_id, Switch.OFF)
    switch_service(base_command, service_id, Switch.ON)


def main():
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--service-id", required=False, help="The service ID to restart"
    )
    parser.add_argument(
        "--start-api", action=argparse.BooleanOptionalAction, required=False
    )
    parser.add_argument("-u", "--uri", required=False)
    parser.add_argument("-U", "--username", required=False)
    parser.add_argument("-P", "--password", required=False)
    args = parser.parse_args()

    if all([args.start_api, args.service_id]):
        parser.error("Either choose the API or service-id not both")

    if args.start_api:
        api()
    else:
        if not all([args.service_id, args.uri, args.username, args.password]):
            parser.error("Provide service-id, uri, username, password")
        restart_service(
            base_command=f"midclt -u {args.uri} -U {args.username} -P {args.password}",
            service_id=args.service_id,
        )
        logging.info("Guess it worked, as this is the end of the script.")


@app.route("/restart", methods=["POST"])
def restart():
    content = request.json
    if not content:
        return jsonify(success=False, error="No valid restart request.")

    r: RestartRequest = content
    restart_service(
        base_command=f"midclt -u {r['uri']} -U {r['username']} -P {r['password']}",
        service_id=r["service_id"],
    )
    return jsonify(success=True, error="")


def api():
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=True)


if __name__ == "__main__":
    main()
