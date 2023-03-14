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

import sys
import subprocess
from lib import get_services, get_middleware_type, wrap_in_dapr, MiddlewareType


def deploy_app(executable_path: str, args: list[str]):
    program_args = [executable_path, *args]
    envs = dict()
    for service in get_services():
        service_id = service['id']
        dapr_app_id = f"{service_id.upper()}_DAPR_APP_ID"
        envs[dapr_app_id] = service_id

    if get_middleware_type() == MiddlewareType.DAPR:
        wrap_in_dapr('vehicleapp', 50008, program_args, envs)

    print(program_args)
    #subprocess.check_call(program_args)


if __name__ == '__main__':
    deploy_app(sys.argv[1], sys.argv[2:])
