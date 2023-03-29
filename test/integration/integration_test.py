from re import compile, Pattern
from threading import Timer
from subprocess import PIPE, Popen, check_call

command: str = "velocitas exec runtime-local"
regex_dapr_app: Pattern[str] = compile(r".*You\'re up and running! Both Dapr and your app logs will appear here\.\n")
regex_mqtt: Pattern[str] = compile(r".*mosquitto version \d+\.\d+\.\d+ running\n")
regex_vdb: Pattern[str] = compile(r".*Listening on \d+\.\d+\.\d+\.\d+:\d+")
regex_fc: Pattern[str] = compile(r".*dbcfeeder: Connected to data broker")
regex_vs: Pattern[str]= compile(r".*DataBrokerFeederImpl: connected to data broker\.")
timeout_sec: float = 180


def run_command_until_logs_match(command: str, regex_service: Pattern[str], run_with_dapr: bool = False) -> bool:
    successfully_running_dapr: bool = True if not run_with_dapr else False
    successfully_running: bool = False

    proc: Popen[str] = Popen(command.split(" "), stdout=PIPE, bufsize=1, universal_newlines=True)
    timer: Timer = Timer(timeout_sec, proc.kill)
    timer.start()
    for line in iter(proc.stdout.readline, b""):
        print(line)
        if run_with_dapr and regex_dapr_app.search(line):
            successfully_running_dapr = True
        if regex_service is not None and regex_service.search(line):
            successfully_running = True
        if successfully_running and successfully_running_dapr:
            timer.cancel()
            break
    if proc.poll() is not None:
        print(f"Timeout reached after {timeout_sec} seconds, process killed!")
        print(f"No match for Regex: {regex_service}")
        return False
    return successfully_running_dapr and successfully_running


def test_scripts_run_successfully():
    assert 0 == check_call(f"{command} ensure-dapr", shell=True)
    assert run_command_until_logs_match(f"{command} run-mosquitto", regex_mqtt)
    assert run_command_until_logs_match(f"{command} run-vehicledatabroker", regex_vdb, True)
    assert run_command_until_logs_match(f"{command} run-feedercan", regex_fc, True)
    assert run_command_until_logs_match(f"{command} run-vehicleservices", regex_vs, True)
