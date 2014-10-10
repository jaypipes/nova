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

from nova.resources import amounts
from nova.resources import types
from nova import test
from nova.virt import hardware as hw


class TestTypes(test.NoDBTestCase):

    def test_basic_types(self):
        for res_type in (types.RAM, types.CPU, types.LocalDisk):
            wanted = res_type.make_amount(2)
            self.assertIsInstance(wanted, amounts.IntegerAmount)

            usage = res_type.make_usage(12, 4)
            self.assertIsInstance(usage, amounts.IntegerUsage)

    def test_numa_topology(self):
        cap_top = hw.VirtNUMALimitTopology([
                    hw.VirtNUMATopologyCellLimit(
                        0, set([0, 1, 2, 3]), 1024, 4, 1024),
                    hw.VirtNUMATopologyCellLimit(
                        1, set([4, 6]), 1024, 2, 512)
        ])
        host_top = hw.VirtNUMAHostTopology([
            hw.VirtNUMATopologyCellUsage(0, set([0, 1, 2, 3]), 1024),
            hw.VirtNUMATopologyCellUsage(1, set([4, 6]), 512)
        ])
        inst_top = hw.VirtNUMAInstanceTopology([
            hw.VirtNUMATopologyCell(0, set([0, 1, 2]), 256),
            hw.VirtNUMATopologyCell(1, set([4]), 256),
        ])
        wanted = types.NUMATopology.make_amount(inst_top)
        self.assertIsInstance(wanted, amounts.NUMAAmount)

        usage = types.NUMATopology.make_usage(cap_top, host_top)
        self.assertIsInstance(usage, amounts.NUMAUsage)
