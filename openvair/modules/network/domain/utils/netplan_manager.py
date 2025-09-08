"""Netplan configuration management.

This module provides classes and methods to manage Netplan configurations,
including creating, updating, and deleting network bridges and interfaces
in YAML configuration files.

Classes:
    NetplanManager: Manager for handling Netplan configurations.
"""

import os
import shutil
from typing import Any, Dict, Optional
from pathlib import Path

from openvair.libs.log import get_logger
from openvair.libs.cli.models import ExecuteParams
from openvair.libs.cli.executor import execute
from openvair.modules.network.config import NETPLAN_DIR
from openvair.libs.data_handlers.yaml.parser import read_yaml, write_yaml
from openvair.modules.network.domain.exceptions import (
    NetplanFileNotFoundException,
)
from openvair.libs.data_handlers.yaml.serializer import deserialize_yaml
from openvair.modules.network.libs.template_rendering.network_renderer import (
    NetworkRenderer,
)

LOG = get_logger(__name__)


class NetplanManager:
    """Manager for handling Netplan configurations.

    This class provides methods to manage Netplan configurations, such as
    creating, updating, and deleting network bridges and interfaces in YAML
    configuration files.

    Attributes:
        netplan_dir (Path): Path to the directory containing Netplan
            configuration files.
    """

    def __init__(self) -> None:
        """Initialize NetplanManager.

        This constructor initializes the Netplan manager and creates a directory
        for storing backup configurations if it does not already exist.
        """
        self.netplan_dir = Path(NETPLAN_DIR)
        self.bkp_netplan_dir = self.netplan_dir / 'bkp'
        self.bkp_netplan_dir.mkdir(exist_ok=True)
        self.network_renderer = NetworkRenderer()

    @staticmethod
    def apply() -> None:
        """Apply the current Netplan configuration."""
        execute(
            'netplan apply',
            params=ExecuteParams(  # noqa: S604
                shell=True, run_as_root=True, raise_on_error=True
            ),
        )

    def create_ovs_bridge_yaml_file(self, data: Dict) -> None:
        """Create a YAML configuration file for an OVS bridge.

        Args:
            data (Dict): The data for the OVS bridge configuration, including
                the name of the bridge and other relevant settings.
        """
        bridge_name: str = data['name']
        LOG.info(f'Creating config file for bridge: {bridge_name}')
        bridge_yaml: str = self.network_renderer.create_ovs_bridge_netplan_yaml(
            data
        )

        bridge_data: Dict[str, Any] = deserialize_yaml(bridge_yaml)
        bridge_file: Path = self._generate_iface_yaml_path(bridge_name)

        write_yaml(bridge_file, bridge_data)
        LOG.info(f'Config file for bridge {bridge_name} created: {bridge_file}')

    def create_iface_yaml(
        self,
        iface_name: str,
        *,
        data: Optional[Dict] = None,
    ) -> Path:
        """Create a new YAML configuration file for a network interface.

        If the file does not exist, this method creates it. Optionally,
        additional data can be provided for the interface configuration.

        Args:
            iface_name (str): The name of the network interface.
            data (Dict): The configuration data for the interface.

        Returns:
            Path: The path to the newly created configuration file.
        """
        LOG.info(f'Creating config file for main port: {iface_name}')

        iface_data: Dict[str, Any] = {'name': iface_name}
        if data:
            iface_data.update(data)

        iface_yaml: str = self.network_renderer.create_iface_yaml(iface_data)
        iface_parsed_data: Dict[str, Any] = deserialize_yaml(iface_yaml)

        iface_file: Path = Path(self._generate_iface_yaml_path(iface_name))
        write_yaml(iface_file, iface_parsed_data)

        LOG.info(f'Config file for {iface_name} was created: {iface_file}')
        return iface_file

    def delete_iface_yaml(self, iface_file: Path) -> None:
        """Delete YAML configuration file for a network interface.

        This method removes the specified YAML file from the filesystem.

        Args:
            iface_file (Path): The path to the file containing the interface
                configuration.
        """
        iface_file.unlink()

    def get_iface_data_from_yaml(
        self,
        iface_name: str,
        iface_file: Path,
    ) -> Dict:
        """Retrieve interface data from a YAML configuration file.

        This method loads and returns the configuration data for a specific
        network interface from a given YAML file.

        Args:
            iface_file (Path): The path to the file containing the interface.
            iface_name (str): The name of the interface to retrieve data for.

        Returns:
            Dict: The data for the specified network interface.
        """
        all_file_data: Dict[str, Any] = read_yaml(iface_file)
        iface_data: Dict[str, Any] = all_file_data['network']['ethernets'][
            iface_name
        ]
        return iface_data

    def get_bridge_data_from_yaml(
        self,
        bridge_name: str,
        iface_file: Path,
    ) -> Dict:
        """Retrieve bridge data from a YAML configuration file.

        This method loads and returns the configuration data for a specific
        network bridge from a given YAML file.

        Args:
            iface_file (Path): The path to the file containing the bridge.
            bridge_name (str): The name of the bridge to retrieve data for.

        Returns:
            Dict: The data for the specified bridge.
        """
        all_file_data: Dict[str, Any] = read_yaml(iface_file)
        iface_data: Dict[str, Any] = all_file_data['network']['bridges'][
            bridge_name
        ]
        return iface_data

    def change_iface_yaml_file(
        self,
        iface_name: str,
        iface_file: Path,
        iface_data: Dict,
    ) -> None:
        """Modify the YAML configuration file for a specific network interface.

        Args:
            iface_name (str): The name of the network interface to modify.
            iface_file (Path): The path to file with interface.
            iface_data (Dict): The new configuration data for the interface.
        """
        LOG.info(f'Editing iface config file: {iface_file}...')
        config_data_with_iface: Dict[str, Any] = read_yaml(iface_file)
        config_data_with_iface['network']['ethernets'][iface_name] = iface_data
        write_yaml(iface_file, config_data_with_iface)

    def backup_iface_yaml(self, iface_file: Path) -> None:
        """Create a backup of a network interface YAML configuration file.

        Args:
            iface_file (Path): Config file for bkp.
        """
        LOG.info(f'Making backup config file: {iface_file}')
        backup_file_full_path = self.bkp_netplan_dir / f'{iface_file.name}.BKP'
        LOG.info(f'Copying port file config to: {backup_file_full_path}...')
        shutil.copy(iface_file, str(backup_file_full_path))

    def restore_backup_file(self, bkp_file: Path) -> None:
        """Restoring bkp iface file into netplan directory

        Args:
            bkp_file (Path): Path to file for restore
        """
        LOG.info(f'Restorting file: {bkp_file} into {self.netplan_dir}')
        shutil.move(
            str(bkp_file), self.netplan_dir / bkp_file.name.rstrip('.BKP')
        )

    def get_path_yaml(self, iface_name: str) -> Path:
        """Find the Netplan file with configuration for a given interface.

        Args:
            iface_name (str): The name of the network interface to search for.

        Raises:
            NetplanFileNotFoundException: If no configuration file is found
                containing the specified interface.

        Returns:
            Path: The path to the file containing the interface configuration.
        """
        LOG.info(f'Searching config file for port: {iface_name}')
        return self._find_iface_yaml_file(iface_name, self.netplan_dir)

    def get_bkp_path_yaml(self, iface_name: str) -> Path:
        """Find backup netplan YAML file in backup dirrectory

        Args:
            iface_name (str): The name of the network interface to search for.

        Raises:
            NetplanFileNotFoundException: If no configuration file is found
                containing the specified interface.

        Returns:
            Path: The path to the backup file containing the interface
                configuration.
        """
        LOG.info(f'Searching backup file for {iface_name}...')
        return self._find_iface_yaml_file(iface_name, self.bkp_netplan_dir)

    def rename_file_as_main_port(self, iface_file: Path) -> Path:
        """Getting netplan file and rename its with suffix _MAIN_PORT"""
        LOG.info(f'Renaming file {iface_file} as main port...')
        self._check_file_existence(iface_file)

        iface_file = iface_file.rename(
            f'{iface_file.absolute()}'.replace('.yaml', '_MAIN_PORT.yaml')
        )
        LOG.info(f'Main port file is: {iface_file}')

        self._check_file_existence(iface_file)
        LOG.info('File for main port succesfull rnamed')
        return iface_file

    def _check_file_existence(self, iface_file: Path) -> None:
        if not iface_file.exists():
            message = f'File {iface_file.absolute()} not exists'
            error = NetplanFileNotFoundException(message)
            LOG.error(error)
            raise error

    def _generate_iface_yaml_path(self, iface_name: str) -> Path:
        """Generate a unique name for a new bridge YAML configuration file.

        This method generates a unique YAML filename for the bridge based on the
        existing files in the Netplan directory, incrementing the prefix for the
        new file.

        Args:
            iface_name (str): The name of the bridge.

        Returns:
            str: The path to the new YAML file for the bridge.
        """
        existing_files = [
            f for f in os.listdir(self.netplan_dir) if f.endswith('.yaml')
        ]

        # Determine the maximum prefix in existing files
        max_prefix = 0
        for file in existing_files:
            try:
                prefix = int(file.split('-')[0])
                if prefix > max_prefix:
                    max_prefix = prefix
            except ValueError:
                continue

        # The new file will have a prefix 1 greater than the current maximum
        new_prefix = max_prefix + 1
        new_filename = f'{new_prefix:02d}-{iface_name}.yaml'
        return Path(self.netplan_dir) / new_filename

    def _find_iface_yaml_file(self, iface_name: str, directory: Path) -> Path:
        """Find the Netplan file with configuration for a given interface.

        Args:
            iface_name (str): The name of the network interface to search for.
            directory (Path): Directory where need to find file

        Raises:
            NetplanFileNotFoundException: If no configuration file is found
                containing the specified interface.

        Returns:
            Path: The path to the file containing the interface configuration.
        """
        # TODO Подумать, а если файла 2  # noqa: RUF003
        file_with_iface = None
        for filename in os.listdir(directory):
            input_file = directory / filename
            if input_file.is_file():
                LOG.info(f'Checking file: {input_file}')
                config = read_yaml(input_file)
                if self._is_iface_in_yaml(iface_name, config['network']):
                    file_with_iface = input_file
                    LOG.info(f'File found: {file_with_iface}')

        if not file_with_iface:
            error = NetplanFileNotFoundException(iface_name)
            LOG.info(error)
            raise error
        return file_with_iface

    def _is_iface_in_yaml(
        self, iface_name: str, config: Dict[str, Dict]
    ) -> bool:
        """Check if an interface is present in the Netplan configuration.

        This method checks if the given network interface or bridge is present
        in the provided Netplan YAML configuration.

        Args:
            iface_name (str): The name of the network interface or bridge.
            config (Dict): The parsed YAML configuration data.

        Returns:
            bool: True if the interface or bridge is present, False otherwise.
        """
        return bool(
            config.get('ethernets', {}).get(iface_name)
            or config.get('bridges', {}).get(iface_name)
        )
