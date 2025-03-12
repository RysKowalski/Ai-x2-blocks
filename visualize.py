import warnings
import graphviz

def draw_net(
    config,
    genome,
    view: bool = False,
    filename: str = 'neat_net',
    node_names: dict = None,
    show_disabled: bool = True,
    prune_unused: bool = False,
    node_colors: dict = None,
    fmt: str = 'svg'
):
    """Rysuje sieć neuronową w czytelny sposób, renderując tylko istotne ukryte węzły."""

    if graphviz is None:
        warnings.warn("Graphviz jest wymagany do rysowania sieci")
        return

    if prune_unused:
        genome = genome.get_pruned_copy(config.genome_config)

    if node_names is None:
        node_names = {}
    if node_colors is None:
        node_colors = {}

    node_attrs = {
        'shape': 'circle',
        'fontsize': '9',
        'height': '0.2',
        'width': '0.2'
    }
    dot = graphviz.Digraph(format=fmt, node_attr=node_attrs)
    dot.attr(rankdir='LR', ratio="fill", concentrate="true", nodesep="0.2", ranksep="1")

    # Tworzymy mapę połączeń
    connections = {}
    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            input_node, output_node = cg.key
            if input_node not in connections:
                connections[input_node] = set()
            connections[input_node].add(output_node)

    # Sprawdzamy, które ukryte węzły prowadzą do wyjścia
    def leads_to_output(node, visited=None):
        if visited is None:
            visited = set()
        if node in config.genome_config.output_keys:
            return True
        if node in visited or node not in connections:
            return False
        visited.add(node)
        return any(leads_to_output(next_node, visited) for next_node in connections[node])

    hidden_nodes = {
        n for n in genome.nodes.keys()
        if n not in config.genome_config.input_keys
        and n not in config.genome_config.output_keys
        and leads_to_output(n)
    }

    # Warstwa wejściowa
    with dot.subgraph(name='cluster_input') as s_input:
        s_input.attr(rank='min', style='invis')
        for k in config.genome_config.input_keys:
            name = node_names.get(k, str(k))
            input_attrs = {'style': 'filled', 'shape': 'box', 'fillcolor': node_colors.get(k, 'lightgray')}
            s_input.node(name, _attributes=input_attrs)

    # Warstwa wyjściowa
    with dot.subgraph(name='cluster_output') as s_output:
        s_output.attr(rank='max', style='invis')
        for k in config.genome_config.output_keys:
            name = node_names.get(k, str(k))
            output_attrs = {'style': 'filled', 'fillcolor': node_colors.get(k, 'lightblue')}
            s_output.node(name, _attributes=output_attrs)

    # Warstwa ukryta (tylko istotne węzły)
    with dot.subgraph(name='cluster_hidden') as s_hidden:
        s_hidden.attr(rank='same', style='invis')
        for n in hidden_nodes:
            name = node_names.get(n, str(n))
            hidden_attrs = {'style': 'filled', 'fillcolor': node_colors.get(n, 'white')}
            s_hidden.node(name, _attributes=hidden_attrs)

    # Dodanie połączeń
    for cg in genome.connections.values():
        if cg.enabled or show_disabled:
            input_node, output_node = cg.key
            if input_node in config.genome_config.input_keys or input_node in hidden_nodes:
                if output_node in config.genome_config.output_keys or output_node in hidden_nodes:
                    a = node_names.get(input_node, str(input_node))
                    b = node_names.get(output_node, str(output_node))
                    style = 'solid' if cg.enabled else 'dotted'
                    color = 'green' if cg.weight > 0 else 'red'
                    width = str(0.1 + abs(cg.weight / 5.0))
                    dot.edge(a, b, _attributes={'style': style, 'color': color, 'penwidth': width})

    dot.render(filename, view=view)
    return dot
