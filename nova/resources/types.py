#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Defines types of resources that are tracked/requested/consumed by users
in a cloud.
"""

from nova.resources import amounts


class ResourceType(object):
    """Classes of resources that may be consumed by a user."""
    _AMOUNT_SPEC_CLASS = amounts.IntegerAmount
    _USAGE_SPEC_CLASS = amounts.IntegerUsage
    _STRING_NAME = 'Unknown'

    def __str__(self):
        return self._STRING_NAME

    @classmethod
    def make_amount(cls, *args, **kwargs):
        """Factory to create an amount specifier for this type of resource.

        Since each type of resource may have a different way of comparing
        amounts of the resource, this factory method takes care of passing
        arguments to the appropriate `nova.resources.amounts.AmountSpec`
        class that should be constructed for this resource type.
        """
        return cls._AMOUNT_SPEC_CLASS(*args, **kwargs)

    @classmethod
    def make_usage(cls, *args, **kwargs):
        """Factory to create a usage specifier for this type of resource.

        Since each type of resource may have a different way of comparing
        amounts of the resource, this factory method takes care of passing
        arguments to the appropriate `nova.resources.amounts.UsageSpec`
        class that should be constructed for this resource type.
        """
        return cls._USAGE_SPEC_CLASS(*args, **kwargs)


class RAM(ResourceType):
    _STRING_NAME = 'RAM'


class CPU(ResourceType):
    _STRING_NAME = 'CPU'


class LocalDisk(ResourceType):
    _STRING_NAME = 'LocalDisk'


class NUMATopology(ResourceType):
    _STRING_NAME = 'NUMATopology'
    _AMOUNT_SPEC_CLASS = amounts.NUMAAmount
    _USAGE_SPEC_CLASS = amounts.NUMAUsage
