#!/usr/bin/env python3
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

"""Charm the application."""

import logging

import ops

# A standalone module for workload-specific logic (no charming concerns):
import tinyproxy

logger = logging.getLogger(__name__)


class TinyproxyCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        framework.observe(self.on.install, self._on_install)
        framework.observe(self.on.start, self._on_start)

    def _on_install(self, event: ops.InstallEvent) -> None:
        """Install tinyproxy on the machine."""
        if not tinyproxy.is_installed():
            tinyproxy.install()

    def _on_start(self, event: ops.StartEvent) -> None:
        """Handle start event."""
        self.unit.status = ops.MaintenanceStatus("starting workload")
        self._configure_and_restart()
        self.unit.status = ops.ActiveStatus()

    def _configure_and_restart(self) -> None:
        """Ensure that tinyproxy is running with the correct configuration."""
        if not tinyproxy.is_installed():
            return
        config_changed = tinyproxy.ensure_config(8888, "example")
        if not tinyproxy.is_running():
            tinyproxy.start()
        elif config_changed:
            tinyproxy.reload_config()


if __name__ == "__main__":  # pragma: nocover
    ops.main(TinyproxyCharm)
