"""Module for utility functions and classes related to storage domain.

This module provides various utilities for managing and parsing storage
information, including disk sizes and partition information.

Classes:
    DiskSizeValueObject: A class representing a disk size with value and unit.
    PartedParser: A class for parsing partition information from the 'parted'
        command output.
"""

import re
from typing import Dict, List, Tuple, Union, Literal, ClassVar

from pydantic import BaseModel, field_validator

from openvair.libs.log import get_logger
from openvair.modules.storage.domain.exception import (
    PartitionTableInfoNotFound,
    UnsupportedPartitionTableTypeError,
    NotFoundDataInPartitonInfoException,
)

LOG = get_logger(__name__)


class DiskSizeValueObject(BaseModel):
    """A class representing a disk size with value and unit.

    This class is used to encapsulate a disk size, including its value and the
    unit of measurement, providing validation and conversion capabilities.

    Attributes:
        value (Union[int, float]): The numeric value of the disk size.
        unit (Literal['B', 'kB', 'MB', 'GB', 'TB']): The unit of the disk size.
    """

    value: Union[int, float]
    unit: Literal['B', 'kB', 'MB', 'GB', 'TB'] = 'GB'

    @field_validator('value')
    @classmethod
    def value_validator(cls, v: Union[int, float]) -> Union[int, float]:
        """Validate that the value is a positive number.

        Args:
            v (Union[int, float]): The value to validate.

        Returns:
            Union[int, float]: The validated value.

        Raises:
            ValueError: If the value is not positive.
        """
        if v < 0:
            msg = 'Value must be a positive integer'
            raise ValueError(msg)
        return v

    def __str__(self) -> str:
        """Return a string representation of the disk size.

        Returns:
            str: The disk size as a string with its unit.
        """
        return f'{self.value}{self.unit}'


class PartedParser:
    """A class for parsing partition information from the 'parted' output.

    This class provides methods for extracting and parsing partition information
    from the output of the 'parted print' command.

    Attributes:
        HEADER_TMP_MSDOS (str): Header template for MSDOS partition tables.
        HEADER_TMP_GPT (str): Header template for GPT partition tables.
        HEADER_PATTERN (re.Pattern): Compiled regex pattern to match headers.
        SIZE_TO_BYTES (ClassVar): Mapping of size units to byte values.
    """

    HEADER_TMP_MSDOS = (
        r'Number\s*Start\s*End\s*Size\s*Type\s*File system\s*Flags'
    )
    HEADER_TMP_GPT = r'Number\s*Start\s*End\s*Size\s*File system\s*Name\s*Flags'
    HEADER_PATTERN = re.compile(r'(File system|\w+)')
    SIZE_TO_BYTES: ClassVar = {
        'B': 1,
        'kB': 1024,
        'MB': 1024**2,
        'GB': 1024**3,
        'TB': 1024**4,
    }

    def parse_partitions_info(self, print_stdout: str) -> Dict:
        """Collect partition information from parsed data rows.

        Args:
            print_stdout (str): Information about partitions from 'parted print'
                command.

        Returns:
            Dict: Information about partitions.
        """
        LOG.info(
            "Parsing partition information from 'parted print' command output."
        )
        data_rows = self._collect_data_rows_from_print(print_stdout)
        header_indexes = self._collect_headers_with_column_length(data_rows[0])

        partitions = {}
        for index, row in enumerate(data_rows[1:]):
            part_info = {}

            for param_name, value_str_length in header_indexes.items():
                start = value_str_length['start']
                end = (
                    len(row)
                    if param_name == 'Flags'
                    else value_str_length['end']
                )
                info = {param_name: row[start:end].strip()}

                param_dict = {}
                param_dict.update(info)
                part_info.update(param_dict)

            part_info['Start'] = part_info['Start'].replace(',', '.')
            part_info['End'] = part_info['End'].replace(',', '.')
            part_info['Size'] = part_info['Size'].replace(',', '.')
            partitions.update({index: part_info})

        return partitions

    def get_byte_value(self, size_str: str) -> float:
        """Convert a size string to a float value in bytes.

        Args:
            size_str (str): The size string to convert.

        Returns:
            float: The size in bytes.
        """
        LOG.info('Converting size string to bytes float value.')
        number, unit = self._parse_size(size_str)
        return float(number * self.SIZE_TO_BYTES[unit])

    def _collect_data_rows_from_print(
        self, parted_print_output: str
    ) -> List[str]:
        """Get data rows from the output of the 'parted' command.

        Args:
            parted_print_output (str): The output of the 'parted' command.

        Returns:
            List[str]: Data rows extracted from the output.
        """
        LOG.info("Extracting data rows from the 'parted' command output.")
        partition_table_type = self._get_partiton_table_type(
            parted_print_output
        )
        start_index = self._get_start_index_of_partition_table(
            partition_table_type, parted_print_output
        )

        return parted_print_output[start_index:].strip().splitlines()

    def _get_partiton_table_type(self, parted_print_output: str) -> str:
        """Find and return type of partition table"""
        partition_table_str = re.compile('Partition Table:').search(
            parted_print_output
        )
        if not partition_table_str:
            error = PartitionTableInfoNotFound(parted_print_output)
            LOG.error(str(error))
            raise error

        partition_table_start_index = partition_table_str.start()
        return (
            parted_print_output[partition_table_start_index:]
            .strip()
            .splitlines()
        )[0]

    def _get_start_index_of_partition_table(
        self,
        partition_table_type: str,
        parted_print_output: str,
    ) -> int:
        """Find and return start index of partitions data"""
        headers = self._get_headers(partition_table_type)

        part_info = re.compile(headers).search(parted_print_output)
        if not part_info:
            error = NotFoundDataInPartitonInfoException(str(part_info))
            LOG.error(str(error))
            raise error
        return part_info.start()

    def _get_headers(self, partition_table_type: str) -> str:
        """Find and return headers of partiton table"""
        if 'gpt' in partition_table_type:
            headers = self.HEADER_TMP_GPT
        elif 'msdos' in partition_table_type:
            headers = self.HEADER_TMP_MSDOS
        else:
            error = UnsupportedPartitionTableTypeError(partition_table_type)
            LOG.error(str(error))
            raise error
        return headers

    def _collect_headers_with_column_length(
        self, headers_str: str
    ) -> Dict[str, Dict[str, int]]:
        """Extract headers from the headers string.

        Args:
            headers_str (str): The headers string.

        Returns:
            Dict[str, Dict[str, int]]: The extracted headers with column
                lengths.
        """
        LOG.info('Extracting headers from the headers string.')
        matches = re.finditer(self.HEADER_PATTERN, headers_str)

        header_indexes = {
            headers_str[match.start() : match.end()]: {
                'start': match.start(),
                'end': match.end(),
            }
            for match in matches
        }

        matches = re.finditer(self.HEADER_PATTERN, headers_str)
        header_order = [
            headers_str[match.start() : match.end()] for match in matches
        ]

        for col_index, header in enumerate(header_order):
            if header != 'Flags':
                header_indexes[header].update(
                    {
                        'end': header_indexes[header_order[col_index + 1]][
                            'start'
                        ]
                    }
                )
            else:
                header_indexes[header].update({'end': 75})

        return header_indexes

    @staticmethod
    def _parse_size(size_str: str) -> Tuple[float, str]:
        """Parse a size string into a numeric value and unit.

        Args:
            size_str (str): The size string to parse.

        Returns:
            Tuple[float, str]: A tuple containing the numeric value and unit.
        """
        LOG.info('Parsing size string into numeric value and unit.')
        unit = ''
        value = ''
        for char in list(size_str[::-1]):
            if char.isalpha():
                unit = char + unit
            else:
                value = char + value

        return float(value), unit
