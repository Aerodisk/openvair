"""YAML configuration generator for app modules.

This module provides a function to generate an YAML configuration for an app
modules using Jinja2 templates. The generated YAML is based on the provided
data.

"""

from typing import Dict
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from openvair.libs.templating.config import TEMPLATES_DIR

JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,
    trim_blocks=True,
    lstrip_blocks=True,
)


def create_ovs_bridge_netplan_yaml(ovs_bridge_data: Dict) -> str:
    """Generate the Netplan configuration file for ovs bridge

    It using the specified template and data.
    """
    ovs_bridge_netplan_template = 'netplan_bridge_template.yaml.j2'
    template = JINJA_ENV.get_or_select_template(ovs_bridge_netplan_template)
    return template.render(ovs_bridge_data)


def create_iface_yaml(port_data: Dict) -> str:
    """Generate the Netplan configuration file for interface

    It using the specified template and data.
    """
    port_netplan_template = 'port_netplan_template.yaml.j2'
    template = JINJA_ENV.get_or_select_template(port_netplan_template)
    return template.render(port_data)


# For test
if __name__ == '__main__':
    dynamic_data = {
        'bridge_name': 'br0',
        'dhcp4': True,
        'addresses': [],
        'interfaces': ['ens5'],
        'stp': False,
        'forward_delay': 0,
    }

    static_data = {
        'bridge_name': 'br1',
        'dhcp4': False,
        'addresses': ['192.168.2.100/24'],
        'gateway4': '192.168.2.1',
        'nameservers': ['1.1.1.1', '8.8.8.8'],
        'interfaces': ['ens6'],
        'stp': True,
        'forward_delay': 15,
    }
    dynamic_yaml = create_ovs_bridge_netplan_yaml(dynamic_data)
    static_yaml = create_ovs_bridge_netplan_yaml(static_data)

    output_dir = Path(__file__).parent
    dynamic_res = Path(f'{output_dir}/dynamic.yaml')
    static_res = Path(f'{output_dir}/static.yaml')
    with Path.open(dynamic_res, 'w') as f:
        f.write(dynamic_yaml)

    with Path.open(static_res, 'w') as f:
        f.write(static_yaml)
