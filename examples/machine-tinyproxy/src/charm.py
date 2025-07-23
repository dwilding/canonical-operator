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

import dataclasses
import logging

import ops

import tinyproxy

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class TinyproxyConfig:
    """Schema for the configuration of the tinyproxy charm."""

    slug: str = "example"
    """Configures the path of the reverse proxy."""

    def __post_init__(self):
        tinyproxy.check_slug(self.slug)  # Raises ValueError if slug is invalid.


class TinyproxyCharm(ops.CharmBase):
    """Charm the application."""

    def __init__(self, framework: ops.Framework) -> None:
        super().__init__(framework)
        framework.observe(self.on.collect_unit_status, self._on_collect_status)
        framework.observe(self.on.install, self._on_install)
        framework.observe(self.on.start, self._on_start)
        framework.observe(self.on.config_changed, self._on_config_changed)

    def _on_collect_status(self, event: ops.CollectStatusEvent):
        """Report the status of tinyproxy (runs after each event)."""
        try:
            self.load_config(TinyproxyConfig)
        except ValueError as e:
            event.add_status(ops.BlockedStatus(str(e)))
        if not tinyproxy.is_installed():
            event.add_status(ops.MaintenanceStatus("Waiting for tinyproxy to be installed"))
        if not tinyproxy.is_running():
            event.add_status(ops.MaintenanceStatus("Waiting for tinyproxy to start"))
        event.add_status(ops.ActiveStatus())

    def _on_install(self, event: ops.InstallEvent) -> None:
        """Install tinyproxy on the machine."""
        if not tinyproxy.is_installed():
            tinyproxy.install()

    def _on_start(self, event: ops.StartEvent) -> None:
        """Handle start event."""
        self._configure_and_restart()

    def _on_config_changed(self, event: ops.ConfigChangedEvent) -> None:
        """Handle config-changed event."""
        self._configure_and_restart()

    def _configure_and_restart(self) -> None:
        """Ensure that tinyproxy is running with the correct configuration."""
        try:
            config = self.load_config(TinyproxyConfig)
        except ValueError:
            return
        if not tinyproxy.is_installed():
            return
        config_changed = tinyproxy.ensure_config(8888, config.slug)
        if not tinyproxy.is_running():
            tinyproxy.start()
        elif config_changed:
            tinyproxy.reload_config()


if __name__ == "__main__":  # pragma: nocover
    ops.main(TinyproxyCharm)
