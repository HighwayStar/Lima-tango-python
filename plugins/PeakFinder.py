############################################################################
# This file is part of LImA, a Library for Image Acquisition
#
# Copyright (C) : 2009-2011
# European Synchrotron Radiation Facility
# BP 220, Grenoble 38043
# FRANCE
#
# This is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.
############################################################################

import itertools
import weakref
import PyTango
import sys
import numpy
import processlib
from Lima import Core
from .Utils import getDataFromFile,BasePostProcess
from Lima.Server import AttrHelper

def grouper(n, iterable, padvalue=None):
    return zip(*[itertools.chain(iterable, itertools.repeat(padvalue, n-1))]*n)

computing_modes_list = ["MAXIMUM", "CM"]

#PeakFinderTask = Core.Processlib.Tasks.PeakFinderTask

#==================================================================
#   PeakFinder Class Description:
#
#
#==================================================================


class PeakFinderDeviceServer(BasePostProcess) :

#--------- Add you global variables here --------------------------
    PEAK_FINDER_TASK_NAME = "PeakFinderTask"
#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self,cl, name):
        self.__peakFinderMgr = None
        
        self.__ComputingMode = {'MAXIMUM' : 0,
                                'CM' : 1}

        BasePostProcess.__init__(self,cl,name)
        PeakFinderDeviceServer.init_device(self)

    def set_state(self,state) :
        if(state == PyTango.DevState.OFF) :
            if(self.__peakFinderMgr) :
                self.__peakFinderMgr = None
                ctControl = _control_ref()
                extOpt = ctControl.externalOperation()
                extOpt.delOp(self.PEAK_FINDER_TASK_NAME)
        elif(state == PyTango.DevState.ON) :
            if not self.__peakFinderMgr:
                ctControl = _control_ref()
                extOpt = ctControl.externalOperation()
                self.__peakFinderMgr = extOpt.addOp(Core.PEAKFINDER,self.PEAK_FINDER_TASK_NAME,
                                                    self._runLevel)
            self.__peakFinderMgr.clearCounterStatus()
            
        PyTango.Device_4Impl.set_state(self,state)

#------------------------------------------------------------------
#    Read BufferSize attribute
#------------------------------------------------------------------
    def read_BufferSize(self, attr):
        value_read = self.__peakFinderMgr.getBufferSize()
        attr.set_value(value_read)


#------------------------------------------------------------------
#    Write BufferSize attribute
#------------------------------------------------------------------
    def write_BufferSize(self, attr):
        data = attr.get_write_value()
        self.__peakFinderMgr.setBufferSize(data)

#------------------------------------------------------------------
#    Read ComputingMode attribute
#------------------------------------------------------------------
    def read_ComputingMode(self, attr):
        value_read = self.__peakFinderMgr.getComputingMode()
        attr.set_value(AttrHelper.getDictKey(self.__ComputingMode,value_read))


#------------------------------------------------------------------
#    Write ComputingMode attribute
#------------------------------------------------------------------
    def write_ComputingMode(self, attr):
        data = attr.get_write_value()
        t = AttrHelper.getDictValue(self.__ComputingMode,data)
        self.__peakFinderMgr.setComputingMode(t)
            
#------------------------------------------------------------------
#    Read CounterStatus attribute
#------------------------------------------------------------------
    def read_CounterStatus(self, attr):
        value_read = self.__peakFinderMgr.getCounterStatus()
        attr.set_value(value_read)


#==================================================================
#
#    PeakFinder command methods
#
#==================================================================

    def setMaskFile(self,argin) :
        mask = getDataFromFile(*argin)
        self.__peakFinderMgr.setMask(mask)
    
    def readPeaks(self) :
        peakResultCounterList = self.__peakFinderMgr.readPeaks()
        if peakResultCounterList:
            listSize = len(peakResultCounterList)
            if listSize :
                returnArray = numpy.zeros(len(peakResultCounterList) * 3,dtype = numpy.double)
                indexArray = 0
                for result in peakResultCounterList:
                    returnArray[indexArray:indexArray+3] = (float(result.frameNumber),
                                                            result.x_peak,
                                                            result.y_peak)
                    indexArray += 3
                return returnArray
        return numpy.array([],dtype = numpy.double)

#==================================================================
#
#    PeakFinderClass class definition
#
#==================================================================
class PeakFinderDeviceServerClass(PyTango.DeviceClass):

    #	 Class Properties
    class_property_list = {
	}


    #	 Device Properties
    device_property_list = {
	}


    #	 Command definitions
    cmd_list = {
        'setMaskFile':
            [[PyTango.DevVarStringArray,"Full path of mask file"],
             [PyTango.DevVoid,""]],
        'readPeaks':
            [[PyTango.DevVoid,""],
             [PyTango.DevVarDoubleArray,"frame number,x,y"]],
	'Start':
            [[PyTango.DevVoid,""],
             [PyTango.DevVoid,""]],
	'Stop':
            [[PyTango.DevVoid,""],
             [PyTango.DevVoid,""]],
	}


    #	 Attribute definitions
    attr_list = {
	'BufferSize':
	    [[PyTango.DevLong,
	    PyTango.SCALAR,
	    PyTango.READ_WRITE]],
	'CounterStatus':
	    [[PyTango.DevLong,
	    PyTango.SCALAR,
	    PyTango.READ]],
	'RunLevel':
	    [[PyTango.DevLong,
	    PyTango.SCALAR,
	    PyTango.READ_WRITE]],
	'ComputingMode':
	    [[PyTango.DevString,
	    PyTango.SCALAR,
	    PyTango.READ_WRITE]],
	}


#------------------------------------------------------------------
#    PeakFinderDeviceServerClass Constructor
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name);



_control_ref = None
def set_control_ref(control_class_ref) :
    global _control_ref
    _control_ref= control_class_ref

def get_tango_specific_class_n_device() :
   return PeakFinderDeviceServerClass,PeakFinderDeviceServer
