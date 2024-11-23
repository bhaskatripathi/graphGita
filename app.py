import streamlit as st
from streamlit_agraph import agraph, Node, Edge, Config

# Define nodes and edges
nodes = []
edges = []

# Add some nodes
nodes.append(Node(id="Spiderman", 
                  label="Peter Parker", 
                  size=25, 
                  shape="circularImage",
                  image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_spiderman.png"))

nodes.append(Node(id="Captain_Marvel", 
                  size=25, 
                  shape="circularImage",
                  image="http://marvel-force-chart.surge.sh/marvel_force_chart_img/top_captainmarvel.png"))

# Add an edge
edges.append(Edge(source="Captain_Marvel", 
                  label="friend_of", 
                  target="Spiderman"))

# Define the graph configuration
config = Config(
    width=750,
    height=950,
    directed=True,
    physics=True,
    hierarchical=False,
)

# Render the graph
st.title("Streamlit Agraph Example")
agraph(nodes=nodes, edges=edges, config=config)
