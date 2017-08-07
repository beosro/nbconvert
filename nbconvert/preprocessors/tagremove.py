"""
Module containing a preprocessor that removes cells if they match
one or more regular expression.
"""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

import re
from traitlets import List, Unicode
from . import ClearOutputPreprocessor


class TagRemovePreprocessor(ClearOutputPreprocessor):
    """
    Removes cells from a notebook that have tags that designate they are to be
    removed prior to exporting the notebook.
    
    Traitlets:
    ----------
    remove_cell_tags: removes cells tagged with these values
    remove_all_output_tags: removes entire output areas on cells 
                            tagged with these values
    remove_single_output_tags: removes individual output objects on
                               outputs tagged with these values

    """

    remove_cell_tags = List(Unicode, default_value=[]).tag(config=True)
    remove_all_output_tags = List(Unicode, default_value=[]).tag(config=True)
    remove_single_output_tags = List(Unicode, default_value=[]).tag(config=True)

    def check_cell_conditions(self, cell, resources, index):
        """
        Checks that a cell has a tag that is to be removed

        Returns: Boolean.
        True means cell should *not* be removed.
        """

        # Return true if any of the tags in the cell are removable.
        return not any([tag in cell.get('tags', [])
                        for tag in self.cell_remove_tags])

    def preprocess(self, nb, resources):
        """
        Preprocessing to apply to each notebook. See base.py for details.
        """
        # Skip preprocessing if the list of patterns is empty
        if not (self.cell_remove_tags or self.output_remove_tags):
            return nb, resources

        # Filter out cells that meet the conditions
        nb.cells = [self.preprocess_cell(cell, resources, index)[0]
                    for index, cell in enumerate(nb.cells)
                    if self.check_cell_conditions(cell, resources, index)]

        return nb, resources

    def preprocess_cell(self, cell, resources, cell_index):
        """
        Apply a transformation on each cell. See base.py for details.
        """

        if any([tag in cell.get('tags', [])
                for tag in self.output_remove_tags]):
            cell.outputs = []
            cell.execution_count = None
            # Remove metadata associated with output
            if 'metadata' in cell:
                for field in self.remove_metadata_fields:
                    cell.metadata.pop(field, None)
        if cell.outputs:
            cell.outputs = [self.preprocess_output(output,
                                                   resources,
                                                   cell_index,
                                                   output_index)[0]
                            for output_index, output in enumerate(cell.outputs)
                            if self.check_output_conditions(output,
                                                            resources,
                                                            cell_index,
                                                            output_index)
                            ]
        return cell, resources

    def check_output_conditions(self, output, resources, 
                                cell_index, output_index):
        """
        Checks that an output has a tag that indicates removal.

        Returns: Boolean.
        True means output should *not* be removed.
        """
        return not any([tag in output.metadata.get('tags', [])
                        for tag in self.remove_single_output_tags])


    def preprocess_output(self, output, resources,
                          cell_index, output_index):
        return output, resources
