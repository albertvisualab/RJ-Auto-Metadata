# src/utils/stop_flag.py
# RJ Auto Metadata
# Copyright (C) 2026 Riiicil
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# src/utils/stop_flag.py
"""Central stop flag for all providers and processing modules.

This module is the single source of truth for the force-stop state.
All API modules, processing utilities, and UI code must use this module
instead of maintaining their own per-module flags.
"""

_FORCE_STOP: bool = False


def is_stop_requested() -> bool:
    """Return True if a stop has been requested."""
    return _FORCE_STOP


def set_force_stop() -> None:
    """Activate the global stop flag. All running processes will check this."""
    global _FORCE_STOP
    _FORCE_STOP = True


def reset_force_stop() -> None:
    """Clear the global stop flag. Call only after the processing thread is confirmed dead."""
    global _FORCE_STOP
    _FORCE_STOP = False
