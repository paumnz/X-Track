"""
Module to visualize results computed by the XTRACK frameworks' engine.
"""

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from pandas import DataFrame


from xtrack_engine._utils.loggable_entity import LoggableEntity


class Visualizer(LoggableEntity):
    """
    A class to visualize analysis results obtained from XTRACK's engine.
    """


    def create_bar_plot(
            self,
            data : DataFrame,
            x_axis_column_name : str,
            y_axis_column_name : str,
            width : float = 10,
            height : float = 7,
            color : str = 'blue',
            x_axis_label : str = 'X axis',
            y_axis_label : str = 'Y axis',
            title : str = '',
            grid : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to create a bar plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            x_axis_column_name: the name of the column to be used for the X-axis.
            y_axis_column_name: the name of the column to be used for the Y-axis.
            width: the width of the image to be created.
            height: the height of the image to be created.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            A matplotlib figure containing the barplot of the given data.
        """
        self.logger.debug('Creating bar plot')

        fig = plt.figure(figsize = (width, height))

        plt.bar(data[x_axis_column_name], data[y_axis_column_name], color = color)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(grid)
        plt.xticks(rotation = x_ticks_rotation)
        plt.tight_layout()

        self.logger.debug('Created bar plot')

        return fig


    def create_line_plot(
            self,
            data : DataFrame,
            x_axis_column_name : str,
            y_axis_column_name : str,
            width : float = 10,
            height : float = 7,
            color : str = 'blue',
            x_axis_label : str = 'X axis',
            y_axis_label : str = 'Y axis',
            title : str = '',
            grid : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to create a line plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            x_axis_column_name: the name of the column to be used for the X-axis.
            y_axis_column_name: the name of the column to be used for the Y-axis.
            width: the width of the image to be created.
            height: the height of the image to be created.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            A matplotlib figure containing the barplot of the given data.
        """
        self.logger.debug('Creating bar plot')

        fig = plt.figure(figsize = (width, height))

        plt.plot(data[x_axis_column_name], data[y_axis_column_name], color = color)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(grid)
        plt.xticks(rotation = x_ticks_rotation)
        plt.tight_layout()

        self.logger.debug('Created bar plot')

        return fig
