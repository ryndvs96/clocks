
import svgwrite
import time
from math import pi, acos, cos, asin, sin, radians, hypot, degrees, atan2
from svgwrite import mm
from datetime import datetime
import os
import random
import sys

logging = True
# hours matched up with their angles
hours = list(zip([3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5, 4], [((c * 30.0) - 15.0) % 360 for c in range(12)]))
# cover_middle_hours = [1, 4, 8, 11]
# do_left_hours = [1, 4, 8, 11, 12, 9, 5, 2, 3, 6, 7, 10]
# do_right_hours = [1, 4, 8, 11, 12, 10, 7, 3, 2, 5, 6, 9]
cover_middle_hours = [11, 9, 3, 1]
do_left_hours = []
do_right_hours = []

flipx = False

splits = True

base_buffer = 3
### all units are mm
extra_outer_buffer = 7 # mm
outer_radius = 100 # full radius of the clock
inner_radius = 40 # radius to cover the movement piece
shaft_radius = 5 # radius for the shaft piece to fit through
max_tic_width = 5 # in mm
min_tic_to_space_ratio = 2 # ratio of tic to between tic space, relative to 1
between_hour_buffer_angle = 1 # allotted buffer room to prevent hours from seeming smushed
space_to_level_ratio = 1.4 # ratio of level space to level height, relative to 1
num_levels = 5
level_length = (outer_radius - inner_radius) / (num_levels * (space_to_level_ratio + 1))
space_length = level_length * space_to_level_ratio

wood_width = 6.4 #mm

# stand = 5.7 x 6mm



## [87, 87 + 8] to [113, 113 + 8]
## [-101, -101 + 5.75]

all_draws = []

create_gif = True

def replay_for_gif():
    if not create_gif:
        return
    
    dir = './svgs/gif_%s/' % (datetime.now().strftime('%Y%m%d-%H%M%S'))
    log('Dir = %s' % dir)
    width = 0.5
    os.mkdir(dir)
    for i in range(len(all_draws)):
        log('Creating frame %d of %d' % (i+1, len(all_draws)))
        filename = '%s%03dframe.svg' % (dir, (i+1))
        dwg = svgwrite.drawing.Drawing(filename=filename)
        group = svgwrite.container.Group()
        for draw in all_draws[:(i+1)]:
            s = draw[0]
            if s is 'path':
                group.add(
                    dwg.path(
                        d=draw[1],
                        fill=draw[2], 
                        stroke=draw[3], 
                        stroke_width=width))
            elif s is 'line':
                group.add(
                    dwg.line(
                        start=draw[1], 
                        end=draw[2], 
                        stroke=draw[3], 
                        stroke_width=width))
            elif s is 'circle':
                group.add(
                    dwg.circle(
                        center=draw[1], 
                        r=draw[2], 
                        stroke=draw[3], 
                        stroke_width=width,
                        fill=draw[5]))
        dwg.add(group)
        dwg.save()
    

def solve():
    filename = 'svgs/phylo_%s.svg' % datetime.now().strftime('%Y%m%d-%H%M%S')
    log('Creating drawing for %s' % filename)
    dwg = svgwrite.drawing.Drawing(filename=filename)
    
    draw_front(MyDrawing(- outer_radius - extra_outer_buffer - 1, 0, 0.05, dwg))
    
    # draw_base(MyDrawing(- outer_radius - extra_outer_buffer - 1, -2, 0.05, dwg))
    
    # draw_back(MyDrawing(outer_radius + extra_outer_buffer + 1, 0, 0.05, dwg))
    # 
    # draw_base(MyDrawing(outer_radius + extra_outer_buffer + 1, -2, 0.05, dwg))
    
def outs(dwg, indent = False):
    ### Outer rim of clock
    dwg.addCircle(0, 0, outer_radius + extra_outer_buffer)
    
    if indent:
        for i in range(7):
            dwg.addCircle(0, 0, outer_radius + extra_outer_buffer - 1 - (i), 'red')
    
sqr_width = 56    

def draw_base(dwg):
    
    sep = 30
    # dwg.addPolarArc(270 + sep, 270 - sep, outer_radius + extra_outer_buffer)
    (x0, y0) = dwg.polarToCartesian(270 - sep, outer_radius + extra_outer_buffer)
    (x1, y1) = dwg.polarToCartesian(270 + sep, outer_radius + extra_outer_buffer)
    ### Do the trig to build the base
    h = (outer_radius + extra_outer_buffer + base_buffer) / cos(radians(sep))
    xdelta = h * sin(radians(sep))
    x2, y2 = (- xdelta,  -outer_radius - extra_outer_buffer - base_buffer)
    x3, y3 = (xdelta,  -outer_radius - extra_outer_buffer - base_buffer)
    
    dwg.addPolarArc(270 - sep, 270 + sep, outer_radius + extra_outer_buffer)
    # print(x0, y0, x1, y1, x2, y2, x3, y3)
    dwg.addLine(x0, y0, x2, y2)
    dwg.addLine(x2, y2, x3, y3)
    dwg.addLine(x3, y3, x1, y1)
    
    dwg.lock()


def draw_front(dwg):
    outs(dwg, True)
    
    ### Inner rim for movement piece to fit through (6mm)
    dwg.addCircle(0, 0, shaft_radius)
    
    # hlf_width = sqr_width / 2.0
    # dwg.addRoundedSquare(sqr_width, 5, 'green')
    # dwg.addLine(hlf_width, - hlf_width, hlf_width, hlf_width, 'green')
    # dwg.addLine(- hlf_width, - hlf_width, hlf_width, - hlf_width, 'green')
    # dwg.addLine(- hlf_width, - hlf_width, - hlf_width, hlf_width, 'green')
    # dwg.addLine(- hlf_width, hlf_width, hlf_width, hlf_width, 'green')
    
    ### Do all the hour wedges
    log('HOURRRS ' + str(hours))
    for (hour, hour_angle) in hours:
        doHourWedges(dwg, hour, hour_angle, (hour in do_right_hours), (hour in do_left_hours), (hour in cover_middle_hours))
    
    deterministicMerge(dwg)  
    
    dwg.lock()  
    
def draw_back(dwg):
    outs(dwg)
    
    # hlf_width = sqr_width / 2.0
    dwg.addRoundedSquare(sqr_width, 5)
    # dwg.addLine(hlf_width, - hlf_width, hlf_width, hlf_width)
    # dwg.addLine(- hlf_width, - hlf_width, hlf_width, - hlf_width)
    # dwg.addLine(- hlf_width, - hlf_width, - hlf_width, hlf_width)
    # dwg.addLine(- hlf_width, hlf_width, hlf_width, hlf_width)
    
    ## 6.4mm x 10mm
    ## [87, 87 + 8] to [113, 113 + 8]
    ## [-101, -101 + 5.75]
    x, y = (-25, -102)
    xdelta = 8
    ydelta = 6.4
    dwg.addLine(x, y, x + xdelta, y)
    dwg.addLine(x, y, x, y + ydelta)
    dwg.addLine(x + xdelta, y, x + xdelta, y + ydelta)
    dwg.addLine(x, y + ydelta, x + xdelta, y + ydelta)
    # 
    x, y = ((0 - x) - xdelta, y)
    dwg.addLine(x, y, x + xdelta, y)
    dwg.addLine(x, y, x, y + ydelta)
    dwg.addLine(x + xdelta, y, x + xdelta, y + ydelta)
    dwg.addLine(x, y + ydelta, x + xdelta, y + ydelta)
    
    # square width 
    swidth = 50
    x = 100
    dwg.addLine(x, y, x + swidth, y)
    dwg.addLine(x + xdelta, y + xdelta, x + swidth - xdelta, y + xdelta)
    
    dwg.addLine(x, y, x, y + swidth)
    dwg.addLine(x + xdelta, y + xdelta, x + xdelta, y + swidth)
    dwg.addLine(x, y + swidth, x + xdelta, y + swidth)
    
    dwg.addLine(x + swidth, y, x + swidth, y + swidth)
    dwg.addLine(x + swidth - xdelta, y + xdelta, x + swidth - xdelta, y + swidth)
    dwg.addLine(x + swidth - xdelta, y + swidth, x + swidth, y + swidth)
    
    ### Do all the hour wedges
    log('HOURRRS ' + str(hours))
    for (hour, hour_angle) in hours:
        doHourWedges(dwg, hour, hour_angle, (hour in do_right_hours), (hour in do_left_hours), (hour in cover_middle_hours))
    
    deterministicMerge(dwg)  
    
    dwg.lock()  
    
def deterministicMerge(dwg):
    ### Merge the arms
    centers = []
    
    # gma is center 
    centers.append((hourToAngle(12), 1))
    
    # merge 2 and 4 (nick, emily)
    result = mergeArms(dwg, hourToAngle(4), hourToAngle(2), max_tic_width, 1, 1, 3)
    centers.append((result, 3))
    
    # merge 8 and 10 (natalia, peter)
    result = mergeArms(dwg, hourToAngle(10), hourToAngle(8), max_tic_width, 1, 1, 3)
    centers.append((result, 3))
    
    # merge (5,6,7) (kyler, tyler, ryan)
    result = mergeArms3(dwg, hourToAngle(7), hourToAngle(6), hourToAngle(5), max_tic_width, 1, 3)
    centers.append((result, 3))
    
    connectCenters(dwg, centers)
    
def connectCenters(dwg, centers):
    log('centers: ' + str(centers))
    centers.sort()
    log('centers: ' + str(centers))
    for i in range(len(centers)):
        (angle0, level) = centers[i]
        angle1 = centers[(i + 1) % len(centers)][0]
        log(' angle0, level, angle1 = %f, %f, %f' % (angle0, level, angle1))
        # connect to center
        dwg.addPolarDoubleLine(
            angle0, 
            inner_radius, 
            outer_radius - (level + 1) * level_length - level * space_length,
            max_tic_width)
        dwg.addPolarArcMeetDoubleLine(
            angle0,
            angle1,
            inner_radius,
            max_tic_width)

def mergeArms3(dwg, angle0, angle1, angle2, width, level, new_level):
    level += 1
    dwg.addPolarDoubleLineRight(
        angle0, 
        outer_radius - ((new_level + 1) * level_length + new_level * space_length),
        outer_radius - (level * level_length + (level - 1) * space_length),
        width)
    dwg.addPolarDoubleLineLeft(
        angle0, 
        outer_radius - (new_level * level_length + new_level * space_length),
        outer_radius - (level * level_length + (level - 1) * space_length),
        width)
    dwg.addPolarDoubleLineLeft(
        angle1, 
        outer_radius - ((new_level) * level_length + new_level * space_length),
        outer_radius - (level * level_length + (level - 1) * space_length),
        width)
    dwg.addPolarDoubleLineRight(
        angle1, 
        outer_radius - ((new_level) * level_length + new_level * space_length),
        outer_radius - (level * level_length + (level - 1) * space_length),
        width)
    dwg.addPolarDoubleLineLeft(
        angle2, 
        outer_radius - ((new_level + 1) * level_length + new_level * space_length),
        outer_radius - (level * level_length + (level - 1) * space_length),
        width)
    dwg.addPolarDoubleLineRight(
        angle2, 
        outer_radius - (new_level * level_length + new_level * space_length),
        outer_radius - (level * level_length + (level - 1) * space_length),
        width)
    dwg.addPolarArc(
        angle0 + widthToAngle(max_tic_width, outer_radius - (new_level * level_length + new_level * space_length)) / 2.0,
        angle1 - widthToAngle(max_tic_width, outer_radius - (new_level * level_length + new_level * space_length)) / 2.0,
        outer_radius - (new_level * level_length + new_level * space_length))
    dwg.addPolarArc(
        angle1 + widthToAngle(max_tic_width, outer_radius - (new_level * level_length + new_level * space_length)) / 2.0,
        angle2 - widthToAngle(max_tic_width, outer_radius - (new_level * level_length + new_level * space_length)) / 2.0,
        outer_radius - (new_level * level_length + new_level * space_length))
    dwg.addPolarArc(
        angle0 - widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        halfAngle(angle0, angle2) - widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        outer_radius - ((new_level + 1) * level_length + new_level * space_length))
    dwg.addPolarArc(
        halfAngle(angle0, angle2) + widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        angle2 + widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        outer_radius - ((new_level + 1) * level_length + new_level * space_length))
    return halfAngle(angle0, angle2)        
    
def mergeArms(dwg, angle0, angle1, width, level0, level1, new_level):
    level0 += 1
    level1 += 1
    dwg.addPolarDoubleLineRight(
        angle0, 
        outer_radius - ((new_level + 1) * level_length + new_level * space_length),
        outer_radius - (level0 * level_length + (level0 - 1) * space_length),
        width)
    dwg.addPolarDoubleLineLeft(
        angle0, 
        outer_radius - (new_level * level_length + new_level * space_length),
        outer_radius - (level0 * level_length + (level0 - 1) * space_length),
        width)
    dwg.addPolarDoubleLineLeft(
        angle1, 
        outer_radius - ((new_level + 1) * level_length + new_level * space_length),
        outer_radius - (level1 * level_length + (level1 - 1) * space_length),
        width)
    dwg.addPolarDoubleLineRight(
        angle1, 
        outer_radius - (new_level * level_length + new_level * space_length),
        outer_radius - (level1 * level_length + (level1 - 1) * space_length),
        width)
    dwg.addPolarArc(
        angle0 + widthToAngle(max_tic_width, outer_radius - (new_level * level_length + new_level * space_length)) / 2.0,
        angle1 - widthToAngle(max_tic_width, outer_radius - (new_level * level_length + new_level * space_length)) / 2.0,
        outer_radius - (new_level * level_length + new_level * space_length))
    dwg.addPolarArc(
        angle0 - widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        halfAngle(angle0, angle1) - widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        outer_radius - ((new_level + 1) * level_length + new_level * space_length))
    dwg.addPolarArc(
        halfAngle(angle0, angle1) + widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        angle1 + widthToAngle(max_tic_width, outer_radius - ((new_level + 1) * level_length + new_level * space_length)) / 2.0,
        outer_radius - ((new_level + 1) * level_length + new_level * space_length))
    return halfAngle(angle0, angle1)
        
    
def doHourWedges(dwg, hour, center, should_do_right=False, should_do_left=False, cover_middle=False):
    log('Doing hour wedge ' + str(hour))
    # dwg.addPolarLine(center + 15.0, 20, 40)
    allotted_angle = 30.0 - between_hour_buffer_angle
    ideal_tic_widths = hour * widthToAngle(max_tic_width, outer_radius - level_length)
    ideal_space_widths = allotted_angle - ideal_tic_widths
    ideal_space_widths -= allotted_angle / (hour + 1)
    print(hour, allotted_angle, ideal_tic_widths, ideal_space_widths, min_tic_to_space_ratio)
    if ideal_space_widths > 0 and ideal_tic_widths / ideal_space_widths <= min_tic_to_space_ratio:
        # We have enough room to use the max_tic_width_angle
        tic_width = max_tic_width
    else:
        # We don't have enough space so we shorten the angle
        bits = allotted_angle / (hour * (min_tic_to_space_ratio + 1))
        bits *= (min_tic_to_space_ratio + 1)
        tic_width = bits
        
    start = center + between_hour_buffer_angle / 2.0
    angles = allotted_angle / (hour + 1)
        
    # right barrier
    dwg.addPolarArc(
        center, 
        start + angles - widthToAngle(tic_width, outer_radius - level_length) / 2.0, 
        outer_radius - level_length)
    if should_do_right:
        dwg.addPolarArc(
            center,
            center + 15.0 - ((widthToAngle(max_tic_width, outer_radius - (2 * level_length) - space_length) / 2.0) if not cover_middle else 0),
            outer_radius - (2 * level_length) - space_length)
        dwg.addPolarArc(    
            center, 
            start + angles - widthToAngle(tic_width, outer_radius - (level_length) - space_length) / 2.0, 
            outer_radius - (level_length) - space_length)
        dwg.addPolarDoubleLineRight(
            start + angles,
            outer_radius - level_length - space_length,
            outer_radius - level_length,
            tic_width)
    else: 
        dwg.addPolarArc(
            start + angles - widthToAngle(tic_width, outer_radius - (2 * level_length) - space_length) / 2.0,
            center + 15.0 - ((widthToAngle(max_tic_width, outer_radius - (2 * level_length) - space_length) / 2.0) if not cover_middle else 0),
            outer_radius - (2 * level_length) - space_length)
        dwg.addPolarDoubleLineRight(
            start + angles,
            outer_radius - 2 * level_length - space_length,
            outer_radius - level_length,
            tic_width)
    # left barrier
    dwg.addPolarArc(
        start + (hour * angles) + widthToAngle(tic_width, outer_radius - level_length) / 2.0, 
        center + 30.0, 
        outer_radius - level_length)
    if should_do_left:
        dwg.addPolarArc(
            center + 15.0 + ((widthToAngle(max_tic_width, outer_radius - (2 * level_length) - space_length) / 2.0) if not cover_middle else 0),
            center + 30.0,
            outer_radius - (2 * level_length) - space_length)
        dwg.addPolarArc(
            start + (hour * angles) + widthToAngle(tic_width, outer_radius - (level_length) - space_length) / 2.0, 
            center + 30.0, 
            outer_radius - (level_length) - space_length)
        dwg.addPolarDoubleLineLeft(
            start + (hour * angles),
            outer_radius - level_length - space_length,
            outer_radius - level_length,
            tic_width)
    else:
        dwg.addPolarArc(
            center + 15.0 + ((widthToAngle(max_tic_width, outer_radius - (2 * level_length) - space_length) / 2.0) if not cover_middle else 0),
            start + (hour * angles) + widthToAngle(tic_width, outer_radius - (2 * level_length) - space_length) / 2.0,
            outer_radius - (2 * level_length) - space_length)
        dwg.addPolarDoubleLineLeft(
            start + (hour * angles),
            outer_radius - 2 * level_length - space_length,
            outer_radius - level_length,
            tic_width)
    for i in range(1, hour):
        dwg.addWedgeMeetDoubleLine(
            start + (i * angles),
            start + ((i + 1) * angles), 
            outer_radius - level_length - space_length, 
            outer_radius - level_length, 
            tic_width)
        
def log(s):
    if logging:
        print(s)

class MyDrawing:
    ### CONSTANTS ###
    def __init__(self, xcenter, ycenter, stroke_width, dwg):
        self.x_offset = xcenter
        self.y_offset = ycenter
        self.line_stroke_color = 'blue'
        self.line_stroke_width = stroke_width * mm
        self.group = svgwrite.container.Group()
        self.dwg = dwg
        
    def lock(self):
        self.dwg.add(self.group)
        self.dwg.save()
    
    def addPolarArc(self, angle0, angle1, radius, color = None):
        angle0 = angle0 % 360
        angle1 = angle1 % 360
        if angle0 == angle1:
            return
        angle1 = 360 if angle1 == 0 else angle1
        if angle0 is None or angle1 is None or radius is None:
            return
        log('\tAdding polar arc: %3.4fdegs to %3.4fdegs at radius %3.4f centered at (%3.4f, %3.4f)' % (angle0, angle1, radius, self.x_offset, self.y_offset))
        if angle1 > angle0 and angle1 - angle0 > 180:
            log('\trecursing 1')
            self.addPolarArc(angle0, halfAngle(angle0, angle1), radius, color)
            self.addPolarArc(halfAngle(angle0, angle1), angle1, radius, color)
            return
        if angle1 < angle0 and 360 - angle1 + angle0 > 180:
            log('\trecursing 2')
            self.addPolarArc(angle0, 360, radius, color)
            self.addPolarArc(0, angle1, radius, color)
            return
        (x0, y0) = self.polarToCartesian(angle0, radius)
        (x1, y1) = self.polarToCartesian(angle1, radius)
        self.addArc(x0, y0, x1, y1, radius, color)
                
    ### If arc is larger than 180, this will fail
    def addArc(self, x0, y0, x1, y1, radius, color = None):
        log('\t\tAdding Cartesian Arc: (%3.4f, %3.4f) to (%3.4f, %3.4f) with radius %3.4f' % (x0, y0, x1, y1, radius))
        """ Adds an arc that bulges to the right as it moves from p0 to p1 """
        x0, y0, x1, y1 = self.offset(x0, y0, x1, y1)
        if flipx:
            a, b = (x0, y0)
            x0, y0 = (x1, y1)
            x1, y1 = (a, b)
        x0, y0, x1, y1, radius = mmToPx(x0), mmToPx(y0), mmToPx(x1), mmToPx(y1), mmToPx(radius)
        log('\t\t\tPixel coords: (%3.4f, %3.4f) to (%3.4f, %3.4f) with radius %3.4f' % (x0, y0, x1, y1, radius))
        args = {'x0':x0, 
                'y0':-y0, 
                'xradius':radius, 
                'yradius':radius, 
                'ellipseRotation':0, #has no effect for circles
                'x1':(x1-x0), 
                'y1':-(y1-y0)}
        all_draws.append(
            ('path', 
            'M %(x0)f,%(y0)f a %(xradius)f,%(yradius)f %(ellipseRotation)f 0,0 %(x1)f,%(y1)f'%args,
            'none',
            (self.line_stroke_color if color is None else color),
            self.line_stroke_width))
        self.group.add(
            self.dwg.path(
                d='M %(x0)f,%(y0)f a %(xradius)f,%(yradius)f %(ellipseRotation)f 0,0 %(x1)f,%(y1)f'%args,
                fill='none', 
                stroke=(self.line_stroke_color if color is None else color), 
                stroke_width=self.line_stroke_width))
                
    def addRoundedSquare(self, size, radius, color = None):
        height = mmToPx(size - 2 * radius)
        startx, starty, _, _ = self.offset((size / 2.0) - radius, size / 2.0, 0, 0)
        if not flipx:
            startx = startx - size + 2*radius
        radius = mmToPx(radius)
        
        log('SQUARE: starting %f, %f' % (startx, starty))
        
        args = {'startx':mmToPx(startx), 
                'starty':-mmToPx(starty), 
                'radius':radius, 
                'xdiff':radius, 
                'ydiff':radius,
                'height':height}
                
        # "M100,100 h200 a20,20 0 0 1 20,20 v200 a20,20 0 0 1 -20,20 h-200 a20,20 0 0 1 -20,-20 v-200 a20,20 0 0 1 20,-20 z" />
        strf = 'M%(startx)f,%(starty)f h%(height)f a%(radius)f,%(radius)f 0 0 1 %(xdiff)f,%(ydiff)f v%(height)f a%(radius)f,%(radius)f 0 0 1 -%(xdiff)f,%(ydiff)f h-%(height)f a%(radius)f,%(radius)f 0 0 1 -%(xdiff)f,-%(ydiff)f v-%(height)f a%(radius)f,%(radius)f 0 0 1 %(xdiff)f,-%(ydiff)f z'
        all_draws.append(
            ('path', 
            strf%args,
            'none',
            (self.line_stroke_color if color is None else color),
            self.line_stroke_width))
        self.group.add(
            self.dwg.path(
                d=strf % args,
                fill='none', 
                stroke=(self.line_stroke_color if color is None else color), 
                stroke_width=self.line_stroke_width))
        
    def addCircle(self, cx, cy, radius, color = None):
        log('\tAdding circle: center (%3.4f, %3.4f) with radius %3.4f' % (cx, cy, radius))
        cx, cy, _, _ = self.offset(cx, cy, 0, 0)
        all_draws.append(
            ('circle', 
            (cx * mm, -cy * mm),
            radius * mm,
            (self.line_stroke_color if color is None else color),
            self.line_stroke_width,
            'none'))
        self.group.add(
            self.dwg.circle(
                center=(cx * mm, -cy * mm), 
                r=radius * mm, 
                stroke=(self.line_stroke_color if color is None else color), 
                stroke_width=self.line_stroke_width,
                fill='none'))
    
    def addPolarLine(self, angle, r0, r1, xdelta=0.0, ydelta=0.0):
        log('\tAdding polar line: angle %3.4fdegs from radius %3.4f to %3.4f' % (angle, r0, r1))
        (x0, y0) = self.polarToCartesian(angle, r0)
        (x1, y1) = self.polarToCartesian(angle, r1)
        return self.addLine(x0 + xdelta, y0 + ydelta, x1 + xdelta, y1 + ydelta)
        
    def addPolarLineWithBuffer(self, angle, r0, r1, buffer):
        log('\tAdding buffered polar line: angle %3.4fdegs from radius %3.4f to %3.4f with buffer %3.2f' % (angle, r0, r1, buffer))
        xdelta, ydelta = self.perpendicularOffset(angle, buffer)
        (x0, y0) = self.polarToCartesian(angle, r0)
        (x1, y1) = self.polarToCartesian(angle, r1)
        return self.addLine(x0 + xdelta, y0 + ydelta, x1 + xdelta, y1 + ydelta)
        
    def addLine(self, x0, y0, x1, y1, color = None):
        x0, y0, x1, y1 = self.offset(x0, y0, x1, y1)
        log('\t\tCartesian line: (%3.4f, %3.4f) to (%3.4f, %3.4f)' % (x0, y0, x1, y1))
        all_draws.append(
            ('line', 
            (x0 * mm, -y0 * mm),
            (x1 * mm, -y1 * mm),
            (self.line_stroke_color if color is None else color),
            self.line_stroke_width))
        self.group.add(
            self.dwg.line(
                start=(x0 * mm, -y0 * mm), 
                end=(x1 * mm, -y1 * mm), 
                stroke=(self.line_stroke_color if color is None else color), 
                stroke_width=self.line_stroke_width))
        return x0, y0, x1, y1
    
    def addWedge(self, angle0, angle1, r0, r1, buffer):
        log('\tAdding wedge: angle %3.4fdegs to angle %3.4f from radius %3.4f to %3.4f with %3.4f buffer' % (angle0, angle1, r0, r1, buffer))
        xdelta, ydelta = self.perpendicularOffset(angle0, buffer)
        x0, y0, x1, y1 = self.addPolarLine(angle0, r0, r1, xdelta, ydelta)
        xdelta, ydelta = self.perpendicularOffset(angle1, buffer)
        x2, y2, x3, y3 = self.addPolarLine(angle1, r0, r1, -xdelta, -ydelta)
        self.addArc(x0, y0, x2, y2, r0)
        self.addArc(x1, y1, x3, y3, r1)
        
    def addPolarArcWithBuffer(self, angle1, angle0, r0, buffer):
        if angle0 is None or angle1 is None or r0 is None or buffer is None:
            return
        log('\tAdding polar arc with buffer: angle %3.4fdegs from radius %3.4f to %3.4f with %3.4f buffer' % (angle0, angle1, r0, buffer))
        xdelta, ydelta = self.perpendicularOffset(angle0, buffer)
        xdelta1, ydelta1 = self.perpendicularOffset(angle1, buffer)
        (x0, y0) = self.polarToCartesian(angle0, r0)
        (x2, y2) = self.polarToCartesian(angle1, r0)
        self.addArc(x2 + xdelta1, y2 + ydelta1, x0 - xdelta, y0 - ydelta, r0)
    
    def addWedgeMeetDoubleLine(self, angle0, angle1, r0, r1, width):
        self.addPolarDoubleLineLeft(angle0, r0, r1, width)
        self.addPolarDoubleLineRight(angle1, r0, r1, width)
        self.addPolarArcMeetDoubleLine(angle0, angle1, r0, width)
        self.addPolarArcMeetDoubleLine(angle0, angle1, r1, width)
    
    def addPolarArcMeetDoubleLine(self, angle0, angle1, r, width):
        (x0, y0) = self.polarToCartesian(angle0, r)
        (x1, y1) = self.polarToCartesian(angle1, r)
        x0delta, y0delta = self.perpendicularOffset(angle0, width)
        angle0, rad0 = self.cartesianToPolar(x0 + x0delta, y0 + y0delta)
        x1delta, y1delta = self.perpendicularOffset(angle1, width)
        angle1, rad1 = self.cartesianToPolar(x1 - x1delta, y1 - y1delta)
        self.addPolarArc(angle0, angle1, r)
    
    def addPolarDoubleLine(self, angle, r0, r1, width):
        self.addPolarDoubleLineLeft(angle, r0, r1, width)
        self.addPolarDoubleLineRight(angle, r0, r1, width)
        
    def addPolarDoubleLineLeft(self, angle, r0, r1, width):
        log('\tAdding polar line left: angle %3.4fdegs from radius %3.4f to %3.4f with buffer %3.2f' % (angle, r0, r1, width))
        (x0, y0) = self.polarToCartesian(angle, r0)
        (x1, y1) = self.polarToCartesian(angle, r1)
        xdelta, ydelta = self.perpendicularOffset(angle, width)
        self.addLine(x0 + xdelta, y0 + ydelta, x1 + xdelta, y1 + ydelta)
        
    def addPolarDoubleLineRight(self, angle, r0, r1, width):
        log('\tAdding polar line right: angle %3.4fdegs from radius %3.4f to %3.4f with buffer %3.2f' % (angle, r0, r1, width))
        (x0, y0) = self.polarToCartesian(angle, r0)
        (x1, y1) = self.polarToCartesian(angle, r1)
        xdelta, ydelta = self.perpendicularOffset(angle, width)
        self.addLine(x0 - xdelta, y0 - ydelta, x1 - xdelta, y1 - ydelta)
    
    def offset(self, x0, y0, x1, y1):
        if flipx:
            x0 = - x0
            x1 = - x1
        return (x0 + self.x_offset, y0 + self.y_offset, x1 + self.x_offset, y1 + self.y_offset)
        
    def perpendicularOffset(self, angle, width):
        perp = angle + 90.0
        return (cos(radians(perp)) * width / 2.0, sin(radians(perp)) * width / 2.0)
        
    def polarToCartesian(self, angle, radius):
        return (radius * cos(radians(angle * 1.0)), radius * sin(radians(angle * 1.0)))
    
    def cartesianToPolar(self, x, y):
        radius = hypot(x, y)
        rad = atan2(y, x)
        deg = rad * (180 / pi)
        return deg % 360, radius

def halfAngle(angle0, angle1):
    if angle1 >= angle0:
        ret = ((angle1 + angle0) / 2.0) % 360
    else:
        ret = halfAngle(angle1, angle0 + 360)
    return ret
    
def widthToAngle(width, radius):
    return 360 * (width / (radius * 2 * pi))
    
def hourToAngle(hour):
    hs = list(zip([3, 2, 1, 12, 11, 10, 9, 8, 7, 6, 5, 4], [((c * 30.0) - 15.0) % 360 for c in range(12)]))
    for (i, j) in hs:
        if i == hour:
            return (j + 15.0) % 360
    return None
    
def mmToPx(length):
    return 3.78 * length
    # return 3.788975 * length
    # return 3.543307 * length
    
solve()

replay_for_gif()
