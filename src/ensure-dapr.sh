#!/bin/bash
# Copyright (c) 2022-2023 Robert Bosch GmbH and Microsoft Corporation
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

echo "#######################################################"
echo "### Ensure dapr                                     ###"
echo "#######################################################"

# Function to initialize Dapr
init_dapr()
{
      set -e
      echo "Initialize dapr runtime $DEFAULT_DAPR_RUNTIME_VERSION ..."
      dapr uninstall
      dapr init --runtime-version $DEFAULT_DAPR_RUNTIME_VERSION
      echo "=========================="
      dapr --version
      echo "=========================="
}

DEFAULT_DAPR_CLI_VERSION=$(echo $VELOCITAS_APP_MANIFEST | jq .dependencies.dapr.cli.version | tr -d '"')
DEFAULT_DAPR_RUNTIME_VERSION=$(echo $VELOCITAS_APP_MANIFEST | jq .dependencies.dapr.runtime.version | tr -d '"')

INSTALLED_DAPR_CLI_VERSION=$(dapr --version | grep "CLI version: " | sed 's/^.*: //' | sed 's/\s*//g')
INSTALLED_DAPR_RUNTIME_VERSION=$(dapr --version | grep "Runtime version: " | sed 's/^.*: //' | sed 's/\s*//g')

# Check dapr CLI
if [ "${INSTALLED_DAPR_CLI_VERSION}" != "${DEFAULT_DAPR_CLI_VERSION}" ]; then
      echo "Install dapr CLI $DEFAULT_DAPR_CLI_VERSION"
      wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash -s $DEFAULT_DAPR_CLI_VERSION
else
      echo "Dapr CLI $DEFAULT_DAPR_CLI_VERSION is already installed."
fi

# check dapr runtime
if [ "${INSTALLED_DAPR_RUNTIME_VERSION}" != "${DEFAULT_DAPR_RUNTIME_VERSION}" ]; then
      init_dapr
else
      echo "Dapr Runtime already Initialized."
      echo "=========================="
      dapr --version
      echo "=========================="
fi
