"""
Module to implement the network metric calculation functionality of the XTRACK framework's engine.
"""


import community
import networkx as nx
import numpy as np

from xtrack_engine._utils.loggable_entity import LoggableEntity


class NetworkMetricCalculator(LoggableEntity):
    """
    A class to implement the network metric calculation functionality of XTrack's engine.
    """

    DENSITY_METRIC : str = 'density'
    IN_DEGREE_METRIC : str = 'in_degree'
    OUT_DEGREE_METRIC : str = 'out_degree'
    EFFICIENCY_METRIC : str = 'efficiency'
    EIGENVECTOR_CENTRALITY_METRIC : str = 'eigenvector_centrality'
    MODULARITY_METRIC : str = 'modularity'
    DIAMETER_METRIC : str = 'diameter'
    CLUSTERING_COEFFICIENT_METRIC : str = 'clustering_coefficient'
    NODE_NUMBER_METRIC : str = 'node_number'
    EDGE_NUMBER_METRIC : str = 'edge_number'

    def calculate_network_density(self, network : nx.DiGraph) -> float:
        """
        Method to calculate the density of a network.

        Args:
            network: the network whose density will be computed.

        Returns:
            The density of the given network.
        """
        self.logger.debug('Calculating network density')

        try:
            network_density = len(network.edges) / (len(network.nodes) * (len(network.nodes) - 1))
        except ZeroDivisionError:
            network_density = 0.0

        self.logger.debug('Calculated network density')

        return network_density


    def calculate_average_in_degree(self, network : nx.DiGraph) -> float:
        """
        Method to calculate the average in-degree of a network.

        Args:
            network: the network whose average in-degree will be computed.

        Returns:
            The average in-degree of the given network.
        """
        self.logger.debug('Calculating average in-degree')

        avg_in_degree = 0.0
        in_degrees = dict(network.in_degree(weight = 'weight'))

        for _, in_degree in in_degrees.items():
            avg_in_degree += in_degree

        try:
            avg_in_degree /= len(in_degrees.keys())
        except ZeroDivisionError as exc:
            self.logger.debug(f'An error occurred when computing the average in-degree (Zero division found: {exc})')

        self.logger.debug('Calculated average in-degree')

        return avg_in_degree


    def calculate_average_out_degree(self, network : nx.DiGraph) -> float:
        """
        Method to calculate the average out-degree of a network.

        Args:
            network: the network whose average out-degree will be computed.

        Returns:
            The average out-degree of the given network.
        """
        self.logger.debug('Calculating average in-degree')

        avg_out_degree = 0.0
        out_degrees = dict(network.out_degree(weight = 'weight'))

        for _, out_degree in out_degrees.items():
            avg_out_degree += out_degree

        try:
            avg_out_degree /= len(out_degrees.keys())
        except ZeroDivisionError as exc:
            self.logger.debug(f'An error occurred when computing the average out-degree (Zero division found: {exc})')

        self.logger.debug('Calculated average out-degree')

        return avg_out_degree


    def calculate_network_efficiency(self, network : nx.DiGraph, invert_weight : bool = True) -> float:
        """
        Method to calculate the efficiency of a network.

        Args:
            network: the network whose efficiency will be computed.
            invert_weight: a boolean parameter that indicates if the weight should be inverted (1 / weight) or not.

        Returns:
            The average efficiency of the given network.
        """
        self.logger.debug('Calculating network efficiency')

        network_efficiency = 0.0

        network_clone = network.copy()

        if invert_weight:
            for _, _, attrs in network_clone.edges(data = True):
                attrs['weight'] =  1 / attrs['weight']

        path_lengths = dict(nx.all_pairs_dijkstra_path_length(network_clone))

        for node, node_path_lengths in path_lengths.items():
            for target_node, distance in node_path_lengths.items():
                if node == target_node:
                    continue

                network_efficiency += 1 / distance

        try:
            network_efficiency = network_efficiency / (len(network_clone.nodes) * (len(network_clone.nodes) - 1))
        except ZeroDivisionError as exc:
            network_efficiency = 0.0
            self.logger.debug(f'An error occurred when computing network efficiency (Zero division found: {exc})')

        self.logger.debug('Calculated network efficiency')

        return network_efficiency


    def calculate_average_eigenvector_centrality(self, network : nx.DiGraph) -> float:
        """
        Method to calculate the average eigenvector centrality of a network.

        Args:
            network: the network whose average eigenvector centrality will be computed.

        Returns:
            The average average eigenvector centrality of the given network.
        """
        self.logger.debug('Calculating average eigenvector centrality')

        avg_network_evc = 0.0

        try:
            evc_per_node = dict(nx.eigenvector_centrality_numpy(network, weight = 'weight'))
        except TypeError:
            self.logger.error('Error when calculating average network EVC due to empty network. Defaulting to 0.')
            return avg_network_evc

        for _, evc_value in evc_per_node.items():
            avg_network_evc += evc_value

        try:
            avg_network_evc /= len(network.nodes)
        except ZeroDivisionError as exc:
            self.logger.debug(f'An error occurred when computing average eigenvector centrality (Zero division found: {exc})')

        self.logger.debug('Calculated average eigenvector centrality')

        return avg_network_evc


    def calculate_network_modularity(self, network : nx.DiGraph) -> float:
        """
        Method to calculate the network modularity.

        Args:
            network: the network whose modularity will be computed.

        Returns:
            The modularity of the given network.
        """
        self.logger.debug('Calculating network modularity')

        modularity = 0.0
        network = network.to_undirected()

        partitions = community.best_partition(network)

        try:
            modularity = community.modularity(partitions, network)
        except Exception as exc:
            self.logger.error('Error when calculating network modularity. Defaulting to 0.')

        self.logger.debug('Calculated network modularity')

        return modularity


    def calculate_network_diameter(self, network : nx.DiGraph) -> int:
        """
        Method to calculate the network diameter.

        Args:
            network: the network whose diameter will be computed.

        Returns:
            The diameter of the given network.
        """
        self.logger.debug('Calculating network diameter')

        diameter = np.inf

        try:
            network = network.subgraph(
                max(nx.strongly_connected_components(network), key = len)
            )
            diameter = nx.diameter(network)
        except Exception as exc:
            self.logger.error('Error when calculating network diameter. Defaulting to 0.')

        self.logger.debug('Calculated network diameter')

        return diameter


    def calculate_average_clustering_coefficient(self, network : nx.DiGraph) -> float:
        """
        Method to calculate the average clustering coefficient of the given network.

        Args:
            network: the network whose diameter will be computed.

        Returns:
            The average clustering coefficient of the given network.
        """
        self.logger.debug('Calculating network average clustering coefficient')

        avg_network_clustering_coefficient = 0.0

        try:
            avg_network_clustering_coefficient = nx.average_clustering(network, weight = 'weight')
        except Exception as exc:
            self.logger.error('Error when calculating network average clustering coefficient. Defaulting to 0.')

        self.logger.debug('Calculated network average clustering coefficient')

        return avg_network_clustering_coefficient


    def calculate_network_node_number(self, network : nx.DiGraph) -> int:
        """
        Method to calculate the number of nodes of the given network.

        Args:
            network: the network whose diameter will be computed.

        Returns:
            The average number of nodes of the given network.
        """
        self.logger.debug('Calculating network node number')

        node_number = len(network.nodes)

        self.logger.debug('Calculated network node number')

        return node_number


    def calculate_network_edge_number(self, network : nx.DiGraph) -> int:
        """
        Method to calculate the number of edges of the given network.

        Args:
            network: the network whose diameter will be computed.

        Returns:
            The average number of edges of the given network.
        """
        self.logger.debug('Calculating network edge number')

        edge_number = len(network.edges)

        self.logger.debug('Calculated network edge number')

        return edge_number
