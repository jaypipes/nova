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
Defines classes that assist in comparing amounts of resources of the same type.
"""


class AmountSpec(object):
    """Abstract base class for a requested amount specifier

    Interface class that serves to provide a consistent way of comparing
    requested resource "amounts" with the available resources that a compute
    node may advertise.

    Most resources have a simple method of determining whether a requested
    amount exceeds the available amount: simply compare two integers -- used
    vs total -- to arrive at the available amount.

    However, some resources, such as NUMA CPU specifications, are not so
    easy to calculate. Instead, the requested NUMA topology must be compared
    to the used cells, cores, and threads for existing placed guest CPUs.
    """
    pass


class IntegerAmount(AmountSpec):

    """When an amount is simply an integer."""

    def __init__(self, amount):
        """Constructs an amount specifier from a requested integer amount.

        :param amount: Simple integer amount requested of the resource.
        """
        self.amount = amount


class NUMAAmount(AmountSpec):

    """A specifier that models a NUMA cell topology."""

    def __init__(self, topology, is_negative=False):
        """Constructs an amount specifier from a requested NUMA topology.

        :param topology: `nova.virt.hardware.VirtNUMAInstanceTopology` object
                         representing the requested NUMA topology that an
                         instance would like.
        :param is_negative: Boolean indicating the amount should be considered
                            a negative amount -- i.e. the NUMA layout is being
                            "unassigned" from the host topology...
        """
        self.topology = topology
        self.is_negative = is_negative


class UsageSpec(object):

    """Represents the used amount of a particular type of resource."""

    def update(self, amount_spec):
        """Update the used amount of resources by the supplied amount.

        :param amount_spec: `AmountSpec` to modify the usage with.
        """
        raise NotImplementedError

    def has_room_for(self, amount_spec):
        """Determine if there is room to fit the supplied amount of resources.

        :param amount_spec: `AmountSpec` to determine if there is room for.
        :returns True if the supplied requested amount of resources is able
                 to be consumed on the node, False otherwise.

                 If the supplied `amount_spec` is negative, returns False.
        """
        raise NotImplementedError


class IntegerUsage(UsageSpec):

    """Represents the total and used amount of a resource with integers."""

    def __init__(self, total, used):
        self.total = total
        self.used = used

    @property
    def available(self):
        return self.total - self.used

    def update(self, amount_spec):
        """Update the used amount of resources by the supplied amount.

        :param amount_spec: `IntegerAmount` to modify the usage with.
        """
        self.used += amount_spec.amount

    def has_room_for(self, amount_spec):
        """Determine if there is room to fit the supplied amount of resources.

        :param amount_spec: `IntegerAmount` to determine if there is room for.
        :returns True if the supplied requested amount of resources is able
                 to be consumed on the node, False otherwise.

                 If the supplied `amount_spec` is negative, returns False.
        """
        if amount_spec.amount < 1:
            return False
        return amount_spec.amount <= self.available


class NUMAUsage(UsageSpec):

    """Represents the NUMA topology/capacity and the cells that are used."""

    def __init__(self, capacity, topology):
        """Constructs the NUMAUsage object.

        :param capacity: `nova.virt.hardware.VirtNUMALimitTopology` object
                         representing the NUMA topology capacity of the
                         compute node.
        :param topology: `nova.virt.hardware.VirtNUMAHostTopology` object
                         representing the used NUMA cells on the compute node.
        """
        self.capacity = capacity
        self.topology = topology

    def update(self, amount_spec):
        """Update the used amount of resources by the supplied amount.

        :param amount_spec: `NUMAAmount` to modify the usage with.
        """
        instance_tops = [amount_spec.topology]
        # NOTE(jaypipes): usage_from_instances() is actually a classmethod,
        #                 which is why this looks weird here...
        self.topology = self.topology.usage_from_instances(
                self.topology, instance_tops, free=amount_spec.is_negative)

    def has_room_for(self, amount_spec):
        """Determine if there is room to fit the supplied amount of resources.

        We utilize the `nova.virt.hardware` module's functions to determine
        if our used NUMA cells will allow for the supplied NUMA topology to
        be assigned.

        :param amount_spec: `NUMAAmount` to determine if there is room for.
        :returns True if the supplied requested amount of resources is able
                 to be consumed on the node, False otherwise.

                 If the supplied `amount_spec` is negative, returns False.
        """
        if amount_spec.is_negative:
            return False
        instance_tops = [amount_spec.topology]
        # NOTE(jaypipes): Yes, this looks exceedingly weird because the
        #                 claim_test() method interface was brought over from
        #                 the nova.compute.claims.Claim object as-is, and this
        #                 method returns either None, or a string representing
        #                 the fact that the requested resource was more than
        #                 the resource provider could fit. This interface
        #                 should go away in the future entirely.
        return self.topology.claim_test(self.topology, instance_tops,
                                        limits=self.capacity) is None
