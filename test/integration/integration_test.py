# Copyright (c) 2023 Robert Bosch GmbH
#
# This program and the accompanying materials are made available under the
# terms of the Apache License, Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# SPDX-License-Identifier: Apache-2.0

import subprocess, re


def running_script_with_log(command, regex):
    successfully_running = False
    built_regex = re.compile(regex)
    proc = subprocess.Popen(command.split(" "), stdout=subprocess.PIPE, bufsize=1, universal_newlines=True)
    for line in iter(proc.stdout.readline, ""):
        print(line)
        if re.match(built_regex, line):
            successfully_running = True
            break
        if proc.poll() is not None:
            break
    return successfully_running


def ensure_dapr(command):
    dapr = subprocess.check_call(command, shell=True)
    return 0 == dapr

def test_all_scripts():
    command = "velocitas exec runtime-local"
    regex = r".*You\'re up and running! Dapr logs will appear here\.\n"
    dapr = ensure_dapr(command + " ensure-dapr")
    mqtt = running_script_with_log(command + " run-mosquitto", r".*mosquitto version \d+\.\d+\.\d+ running\n")
    vdb = running_script_with_log(command + " run-vehicledatabroker", regex)
    vs = running_script_with_log(command + " run-vehicleservices", regex)
    fc = running_script_with_log(command + " run-feedercan", regex)
    assert True == (dapr and mqtt and vs and fc and vdb)
