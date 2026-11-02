
from pyvis.network import Network
import streamlit.components.v1 as components


def visualize_graph(graph):
    """
    Display a NetworkX Knowledge Graph
    as an interactive PyVis diagram in Streamlit.
    """

    net = Network(
        height="600px",
        width="100%",
        directed=True,
        bgcolor="#ffffff",
        font_color="#222222",
        cdn_resources="in_line"
    )

    # Add architecture components
    for node in graph.nodes():

        net.add_node(
            str(node),
            label=str(node),
            title=str(node),
            color="#60A5FA",
            size=18
        )

    # Add relationships
    for source, target, data in graph.edges(data=True):

        relationship = data.get(
            "relationship", "connected to"
        )

        page = data.get("page", "Unknown")

        chunk_id = data.get("chunk_id", "Unknown")

        source_text = data.get("source_text", "")

        tooltip = (
            f"Relationship: {relationship}\n"
            f"Source page: {page}\n"
            f"Chunk: {chunk_id}\n"
            f"Evidence: {source_text[:300]}"
        )

        net.add_edge(
            str(source),
            str(target),
            title=tooltip,
            label=relationship,
            arrows="to"
        )

    net.barnes_hut(
        gravity=-3000,
        central_gravity=0.3,
        spring_length=160,
        spring_strength=0.04
    )

    html = net.generate_html()

    components.html(
        html,
        height=620,
        scrolling=True
    )
