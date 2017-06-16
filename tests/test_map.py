#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'

from unittest import TestCase
from mapping import Map, Node, Table, Link
import os
import hashlib
import warnings


class TestMap(TestCase):

    def setUp(self):
        self.hash = '43228a6d34e15561dcb179a9e4388489e4634093348a57f34801a12fd548f203'
        self.root_path = str(os.path.dirname(os.path.abspath(__file__))).replace('tests', '')
        self.font_path = self.root_path + 'fonts'
        self.font_path_fn = self.root_path + 'fonts/DejaVuSansMono.ttf'
        self.icon_path = self.root_path + 'icons'
        self.cfg_path = self.root_path + 'mapcfgs'
        self.img_path = self.root_path + 'mapimgs'

        a = Node(self.font_path_fn, self.icon_path, x=300, y=30, label='host-A', icon='Router96.png')
        b = Node(self.font_path_fn, self.icon_path, x=750, y=30, label='host-B', icon='Router96.png')
        c = Node(self.font_path_fn, self.icon_path, x=30, y=750, label='host C', icon='Router96.png')
        d = Node(self.font_path_fn, self.icon_path, x=750, y=750, label='HOST-D', icon='Router96.png')
        e = Node(self.font_path_fn, self.icon_path, x=400, y=400, label='host-E', icon='Router96.png')

        link_a = Link(self.font_path_fn, a, e, bandwidth=1000, width=10)
        link_a.data(in_bps=0, out_bps=123345123)
        link_b = Link(self.font_path_fn, b, e, bandwidth=100, width=15)
        link_b.data(in_bps=54123456, out_bps=114987654)
        link_c = Link(self.font_path_fn, c, e, bandwidth=10000)
        link_c.data(in_bps=841123456, out_bps=5147987654)
        link_d = Link(self.font_path_fn, d, e, bandwidth=100, width=15)
        link_d.data(in_bps=73456852, out_bps=987654)
        link_e = Link(self.font_path_fn, a, b, bandwidth=100, width=15)
        link_e.data(in_bps=73456852, out_bps=987654)

        table = Table(self.font_path_fn, x=700, y=350, dt=False)
        self.new_map = Map([link_a, link_b, link_c, link_d, link_e], [a, b, c, d, e], table=table, len_x=800, len_y=800)

    def test_map(self):
        warnings.simplefilter("ignore", ResourceWarning)
        self.new_map.do()
        # new_map.show()
        self.new_map.save_img(self.img_path + '/test.png')
        self.assertEqual(self.hash, hashlib.sha256(open(self.img_path + '/test.png', 'rb').read()).hexdigest())
        # self.fail()

if __name__ == '__main__':
    TestMap()
