#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'maximus'
from PIL import Image, ImageDraw, ImageFont
import math
import os
import logging

log = logging.getLogger(__name__)


class Table(object):
    def __init__(self, fontfile, x=0, y=0, palette=None):
        self.x = x
        self.y = y
        self.width_palet = 30
        self.height_palet = 20
        self.yt = y + self.height_palet
        self.indent_x = 5
        self.indent_y = 3
        self.palette = palette
        self.text_label = 'Traffic Load'
        self.rect_xy = []
        self.table_xy()
        self.text = ['0-0%', '0-1%', '1-10%', '10-25%', '25-40%', '40-55%', '55-70%', '70-85%', '85-100%']
        self.fontfile = fontfile
        self.fontcolor = 'black'
        self.fontsize = 12
        self.font = ImageFont.truetype(self.fontfile, size=self.fontsize)
        if not palette:
            self.palette = ('#908C8C', '#FFFFFF', '#8000FF', '#0000FF', '#00EAEA',
                            '#00FF00', '#FFFF00', '#FF6600', '#FF0000')

    def table_xy(self):
        for i in range(0, 9):
            x1 = self.x + self.indent_x
            y1 = self.yt + self.indent_y + self.height_palet * i
            x2 = self.x + self.indent_x + self.width_palet
            y2 = self.yt + self.height_palet * (i + 1)
            self.rect_xy.append((x1, y1, x2, y2))

    def draw_table(self, draw):
        draw.rectangle((self.x, self.y, self.rect_xy[8][2] + 60, self.rect_xy[8][3] + 5), outline='black', fill='white')
        draw.text((self.x + 5, self.y + 5), self.text_label, fill='black', font=self.font)
        for i in range(0, 9):
            draw.rectangle(self.rect_xy[i], fill=self.palette[i], outline=self.palette[i])
            draw.text((self.rect_xy[i][2] + 2, self.rect_xy[i][1] + 2), self.text[i], fill='black', font=self.font)


class Label(object):
    def __init__(self, fontfile, bgcolor='white', fontcolor='black', fontsize=10, outline='black', label=None,
                 point=None):
        self.outline = outline
        self.bgcolor = bgcolor
        self.fontcolor = fontcolor
        self.fontsize = fontsize
        self.fontfile = fontfile
        self.font = ImageFont.truetype(self.fontfile, size=self.fontsize)
        self.name = str(label)
        self.points = [0, 0, 0, 0]
        self.point_name = [0, 0]
        self.font_width = {8: 6, 10: 7, 12: 8, 14: 9, 16: 10, 18: 11}
        # self.font_height = {8: 10, 10: 12, 12: 14, 14: 16, 16: 18, 18: 20}
        if point:
            self.label_xy(point)

    def label_xy(self, point):
        """font_dict = {fontsize:symbol width}
        symbol height = fontsize
        :param point: coordinates where label show"""
        count = len(self.name)
        if count:
            self.points[0] = int(point[0] - count * self.font_width[self.fontsize] / 2 + 1)
            self.points[1] = int(point[1] - self.fontsize/2)
            self.points[2] = int(point[0] + count * self.font_width[self.fontsize] / 2 - 1)
            self.points[3] = int(point[1] + self.fontsize/2 + 1)
            self.point_name[0] = self.points[0] + 2
            self.point_name[1] = self.points[1]


class Node(object):
    """ Node (device) on a map"""
    def __init__(self, fontfile, icon_path,  x=0, y=0, label=None, icon=None, fontsize=10):
        self.x = x
        self.y = y
        self.icon = icon
        self.icon_path = icon_path
        self.icon_point = None
        self.label_obj = None
        if label:
            self.label_obj = Label(label=label, point=[x, y], fontfile=fontfile, fontsize=fontsize)
        if self.icon:
            self.icon_point = self.icon_xy()

    def icon_xy(self):
        if os.path.isfile(self.icon_path + '/' + self.icon):
            im = Image.open(self.icon_path + '/' + self.icon)
        else:
            im = Image.open(self.icon)
        width, height = im.size
        x = int(self.x - width/2)
        y = int(self.y - height/2)
        return [x, y]


class Link(object):
    """ A line between two Nodes. The line contains two arrows: one for an input
    value and one for an output value"""
    def __init__(self, fontfile, node_a, node_b, bandwidth=1000, width=5, palette=None, fontsize=10):
        self.node_a = node_a
        self.node_b = node_b
        self.fontfile = fontfile
        self.fontsize = fontsize
        self.bandwidth = bandwidth
        self.width = float(width)
        if not palette:
            self.palette = ('#908C8C', '#FFFFFF', '#8000FF', '#0000FF', '#00EAEA',
                            '#00FF00', '#FFFF00', '#FF6600', '#FF0000')
        else:
            self.palette = palette

        self.input_points = self._get_input_arrow_points()
        self.output_points = self._get_output_arrow_points()

        self.incolor = None
        self.outcolor = None
        self.in_label = None
        self.out_label = None

    @staticmethod
    def _middle(x, y):
        """ Return a middle point coordinate between 2 given points """
        return int(x+(y-x)/2)

    @staticmethod
    def _new_x(a, b, x, y):
        """ Calculate "x" coordinate """
        return int(math.cos(math.atan2(y, x) + math.atan2(b, a))*math.sqrt(x*x+y*y))

    @staticmethod
    def _new_y(a, b, x, y):
        """ Calculate "y" coordinate """
        return int(math.sin(math.atan2(y, x) + math.atan2(b, a))*math.sqrt(x*x+y*y))

    def data(self, in_bps=0000, out_bps=749890567):
        in_mps = in_bps/1000000
        out_mps = out_bps/1000000
        self._fill_arrow(in_mps, out_mps)
        in_name, out_name = self._name(in_mps, out_mps)
        in_point = self._get_input_label_point()
        out_point = self._get_output_label_point()
        self.in_label = Label(self.fontfile, label=in_name, point=in_point, fontsize=self.fontsize)
        self.out_label = Label(self.fontfile, label=out_name, point=out_point, fontsize=self.fontsize)

    @staticmethod
    def _name(in_mps, out_mps):
        if in_mps <= 999:
            in_label = str(round(in_mps, 2)) + 'M'
        else:
            in_ps = in_mps/1000
            in_label = str(round(in_ps, 2)) + 'G'

        if out_mps <= 999:
            out_label = str(round(out_mps, 2)) + 'M'
        else:
            out_ps = out_mps/1000
            out_label = str(round(out_ps, 2)) + 'G'

        return in_label, out_label

    def _fill_arrow(self, in_mps, out_mps):
        switch = ((0, 0, 1), (1, 1, 2), (2, 2, 10), (3, 10, 25), (4, 25, 40), (5, 40, 55), (6, 55, 70), (7, 70, 85),
                  (8, 85, 100), (8, 100, 100000))

        in_percent = math.ceil(in_mps * 100 / self.bandwidth)
        out_percent = math.ceil(out_mps * 100 / self.bandwidth)
        for sw in switch:
            if in_percent in range(sw[1], sw[2]):
                self.incolor = self.palette[sw[0]]
            if out_percent in range(sw[1], sw[2]):
                self.outcolor = self.palette[sw[0]]

    def _get_arrow_points(self, x1, y1, x2, y2, width):
        """
        Calculate points of an arrow
        @param x1: x of first point
        @param y1: y of first point
        @param x2: x of second point
        @param y2: y of second point
        @param width: width of arrow
        """
        points = [(x1+self._new_x(x2 - x1, y2 - y1, 0, width),
                  y1+self._new_y(x2 - x1, y2 - y1, 0, width)),

                  (x2+self._new_x(x2 - x1, y2 - y1, -4 * width, width),
                  y2+self._new_y(x2 - x1, y2 - y1, -4 * width, width)),

                  (x2+self._new_x(x2 - x1, y2 - y1, -4 * width, 2 * width),
                  y2+self._new_y(x2 - x1, y2 - y1, -4 * width, 2 * width)),

                  (x2, y2),

                  (x2+self._new_x(x2 - x1, y2 - y1, -4 * width, -2 * width),
                  y2+self._new_y(x2 - x1, y2 - y1, -4 * width, -2 * width)),

                  (x2+self._new_x(x2 - x1, y2 - y1, -4 * width, -width),
                  y2+self._new_y(x2 - x1, y2 - y1, -4 * width, -width)),

                  (x1+self._new_x(x2 - x1, y2 - y1, 0, -width),
                  y1+self._new_y(x2 - x1, y2 - y1, 0, -width))]
        return points

    def _get_input_label_point(self):
        label_x = self._middle(self.node_a.x, self._middle(self.node_a.x, self.node_b.x))
        label_y = self._middle(self.node_a.y, self._middle(self.node_a.y, self.node_b.y))
        return [label_x, label_y]

    def _get_input_arrow_points(self):
        """
        Calculating points of the input arrow
        """
        points = self._get_arrow_points(
                self.node_a.x,
                self.node_a.y,
                self._middle(self.node_a.x, self.node_b.x),
                self._middle(self.node_a.y, self.node_b.y),
                self.width,
                )
        return points

    def _get_output_label_point(self):
        label_x = self._middle(self.node_b.x, self._middle(self.node_b.x, self.node_a.x))
        label_y = self._middle(self.node_b.y, self._middle(self.node_b.y, self.node_a.y))
        return [label_x, label_y]

    def _get_output_arrow_points(self):
        """
        Calculating points of the output arrow
        """
        points = self._get_arrow_points(
                self.node_b.x,
                self.node_b.y,
                self._middle(self.node_b.x, self.node_a.x),
                self._middle(self.node_b.y, self.node_a.y),
                self.width,
                )
        return points


class Map(object):
    def __init__(self, links, nodes, table=None, len_x=800, len_y=800, bgcolor=None, ):
        # Link instance
        self.bgcolor = bgcolor
        self.links = links
        self.table = table
        self.nodes = nodes
        self.image = self.create_image(len_x, len_y)
        self.draw = ImageDraw.Draw(self.image)

    def create_image(self, x, y):
        """ Create a new image with a white background
        :param y: size image y
        :param x: size image x
        """
        img = Image.new("RGBA", (x, y), self.bgcolor)
        return img

    def _draw_polygon(self, points, color):
        """
        Draw the polygon (the arrow) for giving points
        @param points: list of points
        @param color: inside color of polygon (arrow)
        """

        self.draw.polygon(points, fill=color, outline='black')

    def _draw_label(self, label):
        self.draw.rectangle(label.points, fill=label.bgcolor, outline=label.outline)
        self.draw.text((label.point_name[0:2]), label.name, fill=label.fontcolor,
                       font=label.font)

    def _draw_icon(self, icon, icon_point):
        if os.path.isfile(str(os.path.dirname(os.path.abspath(__file__))) + '/icons/' + icon):
            im = Image.open(str(os.path.dirname(os.path.abspath(__file__))) + '/icons/' + icon)
        else:
            im = Image.open(icon)
        im.convert("RGBA")
        self.image.paste(im, (icon_point[0], icon_point[1]), mask=im)

    def draw_arrows(self):
        for link in self.links:
            # draw input arrow
            self._draw_polygon(link.input_points, link.incolor)
            # draw output arrow
            self._draw_polygon(link.output_points, link.outcolor)

    def draw_labels(self):
        """ Draw labels method"""
        if self.nodes:
            for node in self.nodes:
                if node.label_obj:
                    self._draw_label(node.label_obj)
        if self.links:
            for link in self.links:
                self._draw_label(link.in_label)
                self._draw_label(link.out_label)

    def draw_icons(self):
        if self.nodes is not None:
            for node in self.nodes:
                if node.icon:
                    self._draw_icon(node.icon, node.icon_point)

    def do(self):
        if self.table:
            self.table.draw_table(self.draw)
        self.draw_arrows()
        self.draw_icons()
        self.draw_labels()

    def show(self):
        self.image.show()

    def save_img(self, path=str()):
        """
        Save the image to the file path
        @param path: path to the file
        """
        self.image.save(path, "PNG")
