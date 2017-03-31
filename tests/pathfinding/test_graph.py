""" Unit Tests for graph"""

from design.pathfinding.graph import Graph


def test_generate_nodes_of_graph_returns_correct_nodes_for_an_obstacle_facing_north():

    obstacle = ((50, 100), "N")
    graph = Graph([obstacle])
    graph.generate_nodes_of_graph()
    node = (84, 77)
    node2 = (84, 123)
    assert node in graph.graph_dict
    assert node2 in graph.graph_dict
    assert graph.graph_dict.get(node) == [node2]
    assert graph.graph_dict.get(node2) == [node]


def test_generate_nodes_of_graph_returns_correct_nodes_for_an_obstacle_facing_south():

    obstacle = ((50, 100), "S")
    graph = Graph([obstacle])
    graph.generate_nodes_of_graph()

    assert (21.5, 77) in graph.graph_dict
    assert (21.5, 123) in graph.graph_dict
    assert graph.graph_dict.get((21.5, 77)) == [(21.5, 123)]
    assert graph.graph_dict.get((21.5, 123)) == [(21.5, 77)]


def test_generate_nodes_of_graph_returns_correct_nodes_for_an_obstacle_without_orientation():

    obstacle = ((50, 100), "O")
    graph = Graph([obstacle])
    graph.generate_nodes_of_graph()
    node1 = (21.5, 77)
    node2 = (21.5, 123)
    node3 = (84, 77)
    node4 = (84, 123)
    assert len(graph.graph_dict) == 4
    assert graph.graph_dict.get(node2) == [node1]
    assert graph.graph_dict.get(node1) == [node2]
    assert graph.graph_dict.get(node3) == [node4]
    assert graph.graph_dict.get(node4) == [node3]
    assert node2 in graph.graph_dict.keys()
    assert graph.graph_dict.keys() == {node1, node2, node3, node4}


def test_generate_connected_nodes_list_for_node():

    obstacle_list = [((50, 100), "O"), ((75, 140), "S")]
    graph = Graph(obstacle_list)
    graph.generate_nodes_of_graph()
    graph.generate_graph()
    node = (21.5, 77)
    node2 = (21.5, 123)
    assert graph.graph_dict.get(node) == [node2]


def test_generate_the_list_of_nodes_connected_nodes_list_for_node_in_a_graph_with_two_obstacles_facing_south_and_north():

    obstacle_list = [((50, 100), "N"), ((75, 140), "S")]
    graph = Graph(obstacle_list)
    graph.generate_nodes_of_graph()
    graph.generate_graph()
    node_north_1 = (84, 77)
    node_north_2 = (84, 123)
    node_south_1 = (34, 117)
    node_south_2 = (34, 163)

    assert node_north_1 in graph.graph_dict.keys()
    assert node_north_2 in graph.graph_dict.keys()
    assert node_south_1 in graph.graph_dict.keys()
    assert node_south_2 in graph.graph_dict.keys()
    assert node_north_2 in graph.graph_dict.get(node_south_1)
    assert node_south_1 in graph.graph_dict.get(node_north_2)
    assert node_north_1 in graph.graph_dict.get(node_north_2)
    assert node_north_2 in graph.graph_dict.get(node_north_1)
    assert node_south_1 in graph.graph_dict.get(node_south_2)
    assert node_south_2 in graph.graph_dict.get(node_south_1)


def test_generate_the_list_of_nodes_connected_nodes_list_in_a_graph_with_two_obstacles():

    obstacle_list = [((50, 100), "O"), ((75, 160), "S")]
    graph = Graph(obstacle_list)
    graph.generate_nodes_of_graph()
    graph.generate_graph()
    node_1 = (84, 77)
    node_2 = (84, 123)
    node_3 = (21.5, 77)
    node_4 = (21.5, 123)
    node_south_1 = (34, 137)
    node_south_2 = (34, 183)

    assert node_1 in graph.graph_dict.keys()
    assert node_2 in graph.graph_dict.keys()
    assert node_3 in graph.graph_dict.keys()
    assert node_4 in graph.graph_dict.keys()
    assert node_south_1 in graph.graph_dict
    assert node_south_2 in graph.graph_dict
    assert node_2 in graph.graph_dict.get(node_south_1)
    assert node_south_1 in graph.graph_dict.get(node_2)
    assert node_4 in graph.graph_dict.get(node_south_1)
    assert node_south_1 in graph.graph_dict.get(node_4)


def test_generate_the_graph():

    obstacle_list = [((50, 100), "O"), ((75, 160), "S")]
    graph = Graph(obstacle_list)
    graph.generate_nodes_of_graph()
    graph.generate_graph()
    graph_generate = {(84, 77): [(84, 123)],
                      (84, 123): [(84, 77), (34, 137)],
                      (21.5, 77): [(21.5, 123)],
                      (21.5, 123): [(21.5, 77), (34, 137)],
                      (34, 137): [(34, 183), (21.5, 123), (84, 123)],
                      (34, 183): [(34, 137)]}
    assert len(graph.graph_dict.items()) == 6
    assert graph.graph_dict.items() == graph_generate.items()
