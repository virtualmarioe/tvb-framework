# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2013, Baycrest Centre for Geriatric Care ("Baycrest")
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details. You should have received a copy of the GNU General
# Public License along with this program; if not, you can download it here
# http://www.gnu.org/licenses/old-licenses/gpl-2.0
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
#
#

"""
Adapter that uses the traits module to generate interfaces for FCD Analyzer.

.. moduleauthor:: Francesca Melozzi <france.melozzi@gmail.com>
.. moduleauthor:: Marmaduke Woodman <mmwoodman@gmail.com>

"""

import numpy as np
from tvb.analyzers.fcd_matrix import FcdCalculator
from tvb.core.adapters.abcadapter import ABCAsynchronous
from tvb.datatypes.fcd import Fcd
from tvb.basic.traits.util import log_debug_array
from tvb.basic.filters.chain import FilterChain
from tvb.datatypes.time_series import TimeSeries



class FunctionalConnectivityDynamicsAdapter(ABCAsynchronous):
    """ TVB adapter for calling the Pearson CrossCorrelation algorithm. """

    _ui_name = "FCD matrix"
    _ui_description = "Functional Connectivity Dynamics metric"
    _ui_subsection = "fcd_calculator"

    def get_input_tree(self):
        """
        Return a list of lists describing the interface to the analyzer. This
        is used by the GUI to generate the menus and fields necessary for
        defining a simulation.
        """
        algorithm = FcdCalculator()
        algorithm.trait.bound = self.INTERFACE_ATTRIBUTES_ONLY
        tree = algorithm.interface[self.INTERFACE_ATTRIBUTES]
        tree[0]['conditions'] = FilterChain(fields=[FilterChain.datatype + '._nr_dimensions'],
                                            operations=["=="], values=[4])
        return tree


    def get_output(self):
        return [Fcd]


    def configure(self, time_series, sw, sp):
        """
        Store the input shape to be later used to estimate memory usage. Also create the algorithm instance.

        :param time_series: the input time-series for which fcd matrix should be computed
        :param sw: length of the sliding window
        :param sp: spanning time: distance between two consecutive sliding window
        """
        """
        Store the input shape to be later used to estimate memory usage. Also create the algorithm instance.
        """

        self.input_shape = time_series.read_data_shape()
        log_debug_array(self.log, time_series, "time_series")

        ##-------------------- Fill Algorithm for Analysis -------------------##

        self.algorithm = FcdCalculator(time_series=time_series, sw=sw, sp=sp)


    def get_required_memory_size(self, **kwargs):
        """
        Returns the required memory to be able to run this adapter.
        """
        in_memory_input = [self.input_shape[0], 1, self.input_shape[2], 1]
        input_size = np.prod(in_memory_input) * 8.0
        output_size = self.algorithm.result_size(self.input_shape)
        return input_size + output_size


    def get_required_disk_size(self, **kwargs):
        """
        Returns the required disk size to be able to run the adapter (in kB).
        """

        output_size = self.algorithm.result_size(self.input_shape)
        return self.array_size2kb(output_size)


    def launch(self, time_series, sw, sp):
        """
           Launch algorithm and build results.

           :param time_series: the input time-series for which correlation coefficient should be computed
           :param sw: length of the sliding window
           :param sp: spanning time: distance between two consecutive sliding window
           :returns: the fcd matrix for the given time-series, with that sw and that sp
           :rtype: `Fcd`
        """
        # Create a Fcd dataType object.
        result = Fcd(storage_path=self.storage_path, source=time_series, sw=sw, sp=sp)
        fcd = self.algorithm.evaluate()
        result.array_data = fcd
        return result


"""
    def launch(self, time_series, sw, sp):
        # Create a Fcd dataType object.
        not_stored_result = self.algorithm.evaluate()
        result = FcdCalculator(storage_path=self.storage_path, source=self.time_series, sp=self.sp, sw=self.sw)
        result.array_data = not_stored_result.array_data

        return result

"""
