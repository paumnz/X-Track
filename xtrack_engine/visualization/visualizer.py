"""
Module to visualize results computed by the XTRACK frameworks' engine.
"""


from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
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
            A matplotlib figure containing the line plot of the given data.
        """
        self.logger.debug('Creating line plot')

        fig = plt.figure(figsize = (width, height))

        plt.plot(data[x_axis_column_name], data[y_axis_column_name], color = color)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(grid)
        plt.xticks(rotation = x_ticks_rotation)
        plt.tight_layout()

        self.logger.debug('Created line plot')

        return fig


    def create_pie_plot(
            self,
            data : DataFrame,
            category_column_name : str,
            value_column_name : str,
            width : float = 10,
            height : float = 7,
            title : str = '',
            legend : bool = True
        ) -> Figure:
        """
        Method to create a line plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            category_column_name: the name of the column containing the categories of the pie plot.
            value_column_name: the name of the column containing the values of the pie plot.
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.
            legend: a flag that indicates whether a legend should be created on the figure.

        Returns:
            A matplotlib figure containing the pie plot of the given data.
        """
        self.logger.debug('Creating pie plot')

        fig = plt.figure(figsize = (width, height))

        plt.pie(data[value_column_name], labels = data[category_column_name])
        plt.title(title)

        if legend:
            plt.legend()

        plt.tight_layout()

        self.logger.debug('Created pie plot')

        return fig


    def create_comparative_line_plot(
            self,
            data : DataFrame,
            x_axis_column_name : str,
            y_axis_column_name : str,
            category_column_name : str,
            width : float = 10,
            height : float = 7,
            x_axis_label : str = 'X axis',
            y_axis_label : str = 'Y axis',
            title : str = '',
            colors : Tuple[str, ...] = None,
            grid : bool = True,
            legend : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to create a line plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            x_axis_column_name: the name of the column to be used for the X-axis.
            y_axis_column_name: the name of the column to be used for the Y-axis.
            category_column_name : the name of the column containing the categories that lead to different lineplots.
            width: the width of the image to be created.
            height: the height of the image to be created.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            colors: the color to be used for each category.
            grid: a flag that indicates whether the figure should contain a grid or not.
            legend: a flag that indicates whether the figure should include a legend or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            A matplotlib figure containing the line plot of the given data.
        """
        self.logger.debug('Creating line plot')

        fig = plt.figure(figsize = (width, height))

        for idx_category, category in enumerate(data[category_column_name].unique()):
            category_df = data[data[category_column_name] == category]

            plot_params : Dict[str, Any] = {
                'label' : category
            }

            if colors:
                plot_params['color'] = colors[idx_category]

            plt.plot(category_df[x_axis_column_name], category_df[y_axis_column_name], **plot_params)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(grid)
        plt.xticks(rotation = x_ticks_rotation)

        if legend:
            plt.legend()

        plt.tight_layout()

        self.logger.debug('Created line plot')

        return fig


    def create_multi_line_plot(
            self,
            data : DataFrame,
            x_axis_column_name : str,
            y_axis_column_names : Tuple[str, ...],
            width : float = 10,
            height : float = 7,
            x_axis_label : str = 'X axis',
            y_axis_label : str = 'Y axis',
            title : str = '',
            colors : Tuple[str, ...] = None,
            grid : bool = True,
            legend : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to create a multi-line plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            x_axis_column_name: the name of the column to be used for the X-axis.
            y_axis_column_names: the name of the columns to be used for the Y-axis.
            width: the width of the image to be created.
            height: the height of the image to be created.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            colors: the color to be used for each category.
            grid: a flag that indicates whether the figure should contain a grid or not.
            legend: a flag that indicates whether the figure should include a legend or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            A matplotlib figure containing the multi-line plot of the given data.
        """
        self.logger.debug('Creating multi-line plot')

        fig = plt.figure(figsize = (width, height))

        for idx_category, y_axis_col in enumerate(y_axis_column_names):

            plot_params : Dict[str, Any] = {
                'label' : y_axis_col
            }

            if colors:
                plot_params['color'] = colors[idx_category]

            plt.plot(data[x_axis_column_name], data[y_axis_col], **plot_params)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(grid)
        plt.xticks(rotation = x_ticks_rotation)

        if legend:
            plt.legend()

        plt.tight_layout()

        self.logger.debug('Created multi-line plot')

        return fig


    def create_tree_map_plot(
            self,
            data : DataFrame,
            category_column_name : str,
            subcategory_column_name : str,
            value_column_name : str,
            width : float = 10,
            height : float = 7,
            title : str = '',
        ) -> go.Figure:
        """
        Method to create a treemap plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            category_column_name : the name of the column containing the categories to be plotted in the treemap.
            subcategory_column_name : the name of the column containing the subcategories to be plotted in the treemap.
            value_column_name : the name of the column containing the values of each category-subcategory.
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.

        Returns:
            A matplotlib figure containing the treemap plot of the given data.
        """
        self.logger.debug('Creating treemap plot')

        fig = px.treemap(data, path=[px.Constant(""), category_column_name, subcategory_column_name], values = value_column_name, title = title)

        self.logger.debug('Created treemap plot')

        return fig


    def create_word_cloud_plot(
            self,
            word_cloud,
            width : float = 10,
            height : float = 7,
            title : str = '',
        ) -> Figure:
        """
        Method to create a wordcloud plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            category_column_name : the name of the column containing the categories to be plotted in the treemap.
            subcategory_column_name : the name of the column containing the subcategories to be plotted in the treemap.
            value_column_name : the name of the column containing the values of each category-subcategory.
            width: the width of the image to be created.
            height: the height of the image to be created.
            title: the title to be used.

        Returns:
            A matplotlib figure containing the wordcloud plot of the given data.
        """
        self.logger.debug('Creating wordcloud plot')

        fig = plt.figure(figsize = (width, height))

        plt.imshow(word_cloud)
        plt.axis("off")
        plt.title(title)
        plt.tight_layout()

        self.logger.debug('Created wordcloud plot')

        return fig


    def create_scatter_plot(
            self,
            data : DataFrame,
            x_axis_column_name : str,
            y_axis_column_name : str,
            category_column_name : str,
            width : float = 10,
            height : float = 7,
            x_axis_label : str = 'X axis',
            y_axis_label : str = 'Y axis',
            title : str = '',
            grid : bool = True,
            legend : bool = True,
            x_ticks_rotation : float = 0,
        ) -> Figure:
        """
        Method to create a line plot given the data.

        Args:
            data: the Pandas DataFrame containing the information to visualize.
            x_axis_column_name: the name of the column to be used for the X-axis.
            y_axis_column_name: the name of the column to be used for the Y-axis.
            category_column_name: the name of the column to be used for the category separation.
            width: the width of the image to be created.
            height: the height of the image to be created.
            x_axis_label: the label to be used for the X-axis.
            y_axis_label: the label to be used for the Y-axis.
            title: the title to be used.
            grid: a flag that indicates whether the figure should contain a grid or not.
            legend: a flag that indicates whether the figure should contain a legend or not.
            x_ticks_rotation: the rotation degrees of the X-axis ticks.

        Returns:
            A matplotlib figure containing the line plot of the given data.
        """
        self.logger.debug('Creating scatter plot')

        fig = plt.figure(figsize = (width, height))

        for category in data[category_column_name].unique():
            data_subplot = data[data[category_column_name] == category]
            plt.scatter(data_subplot[x_axis_column_name], data_subplot[y_axis_column_name], label = category)

        plt.xlabel(x_axis_label)
        plt.ylabel(y_axis_label)
        plt.title(title)
        plt.grid(grid)
        plt.xticks(rotation = x_ticks_rotation)

        if legend:
            plt.legend()
        plt.tight_layout()

        self.logger.debug('Created scatter plot')

        return fig
