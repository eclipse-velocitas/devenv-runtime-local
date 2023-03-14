# Copyright (c) 2023 Robert Bosch GmbH and Microsoft Corporation
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

import os
from pprint import pprint
import json
import subprocess

from lib import get_script_path, get_services, get_middleware_type, wrap_in_dapr, replace_variables, get_cache_data, MiddlewareType


def get_container_runtime_executable() -> str:
    return "docker"


def json_obj_to_flat_map(obj, prefix: str = '', separator: str = '.') -> dict[str]:
    result = dict[str]()
    if isinstance(obj, dict):
        for key, value in obj.items():
            nested_key = f"{prefix}{separator}{key}"
            result.update(json_obj_to_flat_map(value, nested_key, separator))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            nested_key = f"{prefix}{separator}{index}"
            result.update(json_obj_to_flat_map(value, nested_key, separator))
    else:
        nested_key = f"{prefix}"
        result[nested_key] = obj

    return result


def run_service(service_spec):
    print(f"Running '{service_spec['id']}'")

    no_dapr = False
    service_config = service_spec['config']
    container_image = None
    service_port = None
    env_vars = dict()
    args = []

    cache_vars = json_obj_to_flat_map(json.loads('{ "vspec_path": "./my_locl_file.txt", "deep": { "nested": 3 }, "list": [ 3, 1, 4] }'), 'builtin.cache')

    for config_entry in service_config:
        if config_entry['key'] == 'image':
            container_image = replace_variables(config_entry['value'], cache_vars)
        elif config_entry['key'] == 'env':
            pair = config_entry['value'].split('=')
            env_vars[pair[0].strip()] = replace_variables(pair[1].strip(), cache_vars)
        elif config_entry['key'] == 'port':
            service_port = replace_variables(config_entry['value'], cache_vars)
        elif config_entry['key'] == 'no-dapr':
            no_dapr = config_entry['value']
        elif config_entry['key'] == 'arg':
            args.append(replace_variables(config_entry['value'], cache_vars))

    program_args = [
        get_container_runtime_executable(),
        "run",
        *[f"-e {key}={value}" for key, value in env_vars.items()],
        container_image,
        *args
        ]

    if not no_dapr and get_middleware_type() == MiddlewareType.DAPR:
        wrap_in_dapr(
            service_spec['id'],
            service_port,
            program_args,
            env_vars)

    pprint(program_args)
    subprocess.Popen(program_args, start_new_session=True)


def run_services() -> None:
    for service in get_services():
        run_service(service)


if __name__ == '__main__':
    run_services()
