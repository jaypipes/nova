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
from nova import test
from nova.virt import hardware as hw


class TestAmountSpecs(test.NoDBTestCase):

    def test_integer_comparisons(self):
        u = amounts.IntegerUsage(10, 8)
        a = amounts.IntegerAmount(2)

        self.assertTrue(u.has_room_for(a))
        u.update(a)
        self.assertFalse(u.has_room_for(a))

        b = amounts.IntegerAmount(-3)
        # has_room_for() should return False for any negative amount.
        self.assertFalse(u.has_room_for(b))
        u.update(b)
        self.assertTrue(u.has_room_for(a))
        self.assertEqual(7, u.used)
        self.assertEqual(3, u.available)

    def test_numa_comparisons(self):
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
        u = amounts.NUMAUsage(cap_top, host_top)
        a = amounts.NUMAAmount(inst_top)

        self.assertTrue(u.has_room_for(a))
        u.update(a)
        self.assertFalse(u.has_room_for(a))

        b = amounts.NUMAAmount(inst_top, is_negative=True)
        # has_room_for() should return False for any negative amount.
        self.assertFalse(u.has_room_for(b))
        u.update(b)
        self.assertTrue(u.has_room_for(a))
