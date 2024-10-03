"""Factory classes for creating image instances.

This module defines factory classes that are responsible for creating instances
of different image types based on provided data. It implements the Factory
Method pattern to encapsulate the instantiation logic for images stored on
various file systems.

Classes:
    AbstractImageFactory: Abstract base factory class for creating image
        instances.
    ImageFactory: Concrete factory class that creates instances of different
        image types based on storage type.
"""

import abc
from typing import Dict, ClassVar

from openvair.modules.image.domain.base import BaseImage
from openvair.modules.image.domain.remotefs import nfs
from openvair.modules.image.domain.physical_fs import localfs


class AbstractImageFactory(metaclass=abc.ABCMeta):
    """Abstract factory for creating BaseImage instances.

    This class provides an interface for creating image instances based on
    provided data. Subclasses must implement the `get_image` method to
    return an instance of `BaseImage` or its subclasses.
    """

    def __call__(self, db_image: Dict) -> BaseImage:
        """Create an image instance based on the provided data.

        Args:
            db_image (Dict): A dictionary containing the data for the image.

        Returns:
            BaseImage: An instance of `BaseImage` or its subclass.
        """
        return self.get_image(db_image)

    @abc.abstractmethod
    def get_image(self, db_image: Dict) -> BaseImage:
        """Creates an image instance from the given dictionary.

        Args:
            db_image (Dict): A dictionary containing the data for the image.

        Returns:
            BaseImage: An instance of `BaseImage` or its subclass.
        """
        ...


class ImageFactory(AbstractImageFactory):
    """Factory for creating instances of different image types.

    This class selects the appropriate `BaseImage` subclass based on the
    storage type specified in the provided data and creates an instance of it.
    """

    _image_classes: ClassVar = {
        'nfs': nfs.NfsImage,
        'localfs': localfs.LocalFSImage,
    }

    def get_image(self, db_image: Dict) -> BaseImage:
        """Creates an image instance from the given dictionary.

        Args:
            db_image (Dict): A dictionary containing the data for the image.

        Returns:
            BaseImage: An instance of the corresponding `BaseImage` subclass.

        Raises:
            KeyError: If the storage type specified in the dictionary does not
                have a corresponding image class.
        """
        image_class = self._image_classes[db_image['storage_type']]
        return image_class(**db_image)
