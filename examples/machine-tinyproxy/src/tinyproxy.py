# Copyright 2025 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Functions for managing and interacting with tinyproxy."""

import logging
import shutil
import subprocess

from charmlibs import pathops
from charms.operator_libs_linux.v0 import apt

logger = logging.getLogger(__name__)

CONFIG_FILE = "/etc/tinyproxy/tinyproxy.conf"
PID_FILE = "/var/run/tinyproxy.pid"


def ensure_config(port: int, slug: str) -> bool:
    """Ensure that tinyproxy is configured. Return True if any changes were made."""
    config = f"""\
PidFile "{PID_FILE}"
Port {port}
Timeout 600
ReverseOnly Yes
ReversePath "/{slug}/" "http://www.example.com/"
"""
    return pathops.ensure_contents(CONFIG_FILE, config)


def install() -> None:
    """Use apt to install the tinyproxy executable."""
    apt.update()
    apt.add_package("tinyproxy-bin")
    # TODO: Handle errors. See https://charmhub.io/operator-libs-linux/libraries/apt


def is_installed() -> bool:
    """Return whether the tinyproxy executable is available."""
    return shutil.which("tinyproxy") is not None


def is_running() -> bool:
    """Return whether tinyproxy is running."""
    return pathops.LocalPath(PID_FILE).exists()


def start() -> None:
    """Start tinyproxy."""
    subprocess.run(["tinyproxy"], check=True)


def reload_config() -> None:
    """Ask tinyproxy to reload configuration."""
    ...
