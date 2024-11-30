# This is the final version with agraph as d3-graph was not very versatile and had responsive rendering issues on the modbile.
import streamlit as st
import json
import networkx as nx
from streamlit_agraph import agraph, Node, Edge, Config
from typing import Dict, List, Optional, Union, Tuple
import os
from gtts import gTTS
import os
from io import BytesIO

# Function to generate audio from text
def generate_audio(text: str, filename: str = "shloka.mp3", lang: str = 'hi'):
    """
    Generate audio from text with language support and loading spinner
    lang can be 'hi' for Hindi or 'en' for English
    For Indian English accent, we use 'en-IN'
    Returns audio data as bytes
    """
    with st.spinner('Generating audio, please wait...'):
        if lang == 'en':
            lang = 'en-IN'  # Use Indian English accent
        
        # Create a BytesIO object to store audio in memory
        audio_bytes = BytesIO()
        tts = gTTS(text=text, lang=lang)
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)  # Reset pointer to beginning of buffer
        
        return audio_bytes


def create_node(id: str, label: str, node_type: str) -> Node:
    """Helper function to create nodes with consistent styling"""
    type_to_style = {
        'problem': {'color': '#FFD700', 'size': 30, 'shape': 'dot'},    # Yellow
        'chapter': {'color': '#87CEEB', 'size': 25, 'shape': 'dot'},    # Sky blue
        'shloka': {'color': '#F08080', 'size': 20, 'shape': 'dot'},     # Light coral
        'theme': {'color': '#90EE90', 'size': 35, 'shape': 'dot'},      # Light green
        'character': {'color': '#FFD700', 'size': 30, 'shape': 'dot'},  # Changed from 'circularImage' to 'dot'
        'event': {'color': '#87CEEB', 'size': 25, 'shape': 'dot'}       # Sky blue
    }
    
    style = type_to_style.get(node_type, {'color': '#FFFFFF', 'size': 25, 'shape': 'dot'})
    
    return Node(
        id=id,
        label=label,
        size=style['size'],
        shape=style['shape'],
        color=style['color']
    )

def create_edge(source: str, target: str, label: str = "") -> Edge:
    """Helper function to create edges with consistent styling"""
    return Edge(
        source=source,
        target=target,
        label=label,
        color="#666666",
        smooth={'type': 'curvedCW', 'roundness': 0.2}
    )

def create_agraph_config() -> Config:
    """Create consistent agraph configuration for graph visualization"""
    config = Config(
        # Basic display configuration
        width="100%",          # Responsive width that fills container
        height=600,            # Fixed height in pixels
        directed=True,         # Show directed edges with arrows
        
        # Physics simulation settings for node positioning
        physics={
            'enabled': True,   # Enable physics simulation
            'solver': 'forceAtlas2Based',  # Use ForceAtlas2 algorithm for layout
            'forceAtlas2Based': {
                'gravitationalConstant': -2000,  # Strength of node repulsion (-ve for repulsion)
                'centralGravity': 0.5,          # Pull towards center (0=no pull, 1=strong)
                'springLength': 200,            # Desired length of edges
                'springConstant': 0.05,         # Edge elasticity (higher=stiffer)
                'damping': 0.4,                 # Reduces node oscillation (0=no damping, 1=full)
                'avoidOverlap': 0.5             # Node spacing (0=allow overlap, 1=no overlap)
            },
            'stabilization': {
                'enabled': True,          # Stabilize network before displaying
                'iterations': 2000,       # Max iterations for stabilization
                'updateInterval': 25,     # Reduced for smoother initial render
                'onlyDynamicEdges': False,# Stabilize all edges
                'fit': True,             # Scale to fit container
                'initialSteps': 1000     # Minimum steps before first render
            },
            'minVelocity': 0.75,         # Minimum velocity for simulation
            'maxVelocity': 30,           # Maximum velocity for simulation
        },
        
        # Node and edge behavior
        hierarchical=False,              # Don't use hierarchical layout
        nodeHighlightBehavior=True,      # Enable node highlighting on hover
        node={
            'labelProperty': 'label',    # Node property to use as label
            'size': 500,                 # Base node size
            'highlightStrokeColor': 'black',  # Color when node is highlighted
            'scaling': {                 # Node size scaling
                'min': 10,
                'max': 30
            }
        },
        
        # Edge (link) configuration
        link={
            'labelProperty': 'label',    # Edge property to use as label
            'renderLabel': True,         # Show edge labels
            'strokeWidth': 1.5,          # Edge line thickness
            'smooth': {                  # Edge curve settings
                'enabled': True,
                'type': 'curvedCW'
            }
        },
        
        # Visual styling
        highlightColor="#F7A7A6",       # Color used for highlighting
        collapsible=True,               # Allow collapsing of nodes
        
        # Layout configuration
        layout={
            'hierarchical': False,       # Disable hierarchical layout
            'improvedLayout': True,      # Use improved layout algorithm
            'randomSeed': 42,           # Consistent layout between renders
            'clusterThreshold': 150,    # Distance threshold for clustering
        },
        
        # Container styling
        style={                         # CSS styling for graph container
            'border': '2px solid #ddd',
            'border-radius': '8px',
            'background': '#f8f9fa',
            'margin': '10px 0',
            'padding': '10px'
        }
    )
    return config

class GitaGraphRAG:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_path = os.path.join(self.current_dir, 'data', 'bhagavad_gita_complete.json')
        self.data = self._load_data()
        self.G = nx.Graph()
        self.build_knowledge_graph()
        
    def _load_data(self) -> Optional[Dict]:
        """Load the Bhagavad Gita JSON data"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
            return None
            
    def build_knowledge_graph(self) -> None:
        """Build the knowledge graph from the loaded data"""
        if not self.data:
            return
            
        # Add problem nodes first
        if 'problem_solutions_map' in self.data:
            for problem, details in self.data['problem_solutions_map'].items():
                problem_id = f"Problem_{problem}"
                self.G.add_node(problem_id,
                              type='problem',
                              name=problem,
                              description=details['description'])
                
                # Add references as edges to chapters/shlokas
                for ref in details['references']:
                    shloka_id = f"Shloka_{ref['chapter']}_{ref['shloka']}"
                    chapter_id = f"Chapter_{ref['chapter']}"
                    
                    # Add edges to both chapter and shloka
                    self.G.add_edge(problem_id, chapter_id)
                    self.G.add_edge(problem_id, shloka_id)
        
        # Add chapter nodes
        if 'chapters' in self.data:
            for chapter in self.data['chapters']:
                chapter_id = f"Chapter_{chapter['number']}"
                node_attrs = {
                    'type': 'chapter',
                    'name': chapter.get('name', ''),
                    'number': chapter.get('number', 0),
                    'summary': chapter.get('summary', ''),
                    'main_theme': chapter.get('main_theme', '')
                }
                self.G.add_node(chapter_id, **node_attrs)
                
                # Add shloka nodes
                for shloka in chapter.get('shlokas', []):
                    shloka_id = f"Shloka_{chapter['number']}_{shloka['shloka_number']}"
                    self.G.add_node(shloka_id,
                                  type='shloka',
                                  sanskrit_text=shloka.get('sanskrit_text', ''),
                                  meaning=shloka.get('meaning', ''),
                                  interpretation=shloka.get('interpretation', ''))
                    self.G.add_edge(chapter_id, shloka_id)

    def get_problem_solutions(self, problem: str) -> Optional[Dict]:
        """Get solutions for a specific problem"""
        if 'problem_solutions_map' in self.data:
            return self.data['problem_solutions_map'].get(problem)
        return None

    def get_shloka_by_reference(self, chapter: int, shloka: int) -> Optional[Dict]:
        """Get shloka details by chapter and shloka number"""
        if 'chapters' in self.data:
            chapter_data = next((ch for ch in self.data['chapters'] 
                               if ch['number'] == chapter), None)
            if chapter_data:
                return next((sh for sh in chapter_data.get('shlokas', [])
                           if sh['shloka_number'] == shloka), None)
        return None

    def visualize_chapter_graph(self, node_id: str) -> Tuple[List[Node], List[Edge]]:
        """Create agraph visualization of the graph for a specific node"""
        nodes = []
        edges = []
        seen_nodes = set()  # To prevent duplicate nodes
        
        # Create subgraph for the selected node
        subgraph = nx.ego_graph(self.G, node_id, radius=1)
        
        # Add nodes
        for node in subgraph.nodes():
            if node not in seen_nodes:
                node_data = self.G.nodes[node]
                node_type = node_data['type']
                label = f"{node_data.get('name', '')} {node.split('_')[-1]}"
                
                nodes.append(create_node(node, label, node_type))
                seen_nodes.add(node)
        
        # Add edges
        for source, target in subgraph.edges():
            edges.append(create_edge(source, target))
        
        return nodes, edges

    def visualize_theme_relationships(self, selected_theme: str, related_chapters: list) -> Tuple[List[Node], List[Edge]]:
        """Create agraph visualization showing relationships between theme, chapters, and shlokas"""
        nodes = []
        edges = []
        seen_nodes = set()
        
        # Add theme node
        theme_id = f"Theme_{selected_theme}"
        nodes.append(create_node(theme_id, selected_theme, 'theme'))
        seen_nodes.add(theme_id)
        
        # Add related chapters and shlokas
        for chapter in related_chapters:
            chapter_id = f"Chapter_{chapter['number']}"
            if chapter_id not in seen_nodes:
                nodes.append(create_node(
                    chapter_id,
                    f"Chapter {chapter['number']}: {chapter['name']}",
                    'chapter'
                ))
                seen_nodes.add(chapter_id)
                edges.append(create_edge(theme_id, chapter_id, "contains"))
            
            # Add relevant shlokas
            for shloka in chapter.get('shlokas', []):
                if any(kw.lower() in selected_theme.lower() for kw in shloka.get('keywords', [])):
                    shloka_id = f"Shloka_{chapter['number']}_{shloka['shloka_number']}"
                    if shloka_id not in seen_nodes:
                        nodes.append(create_node(
                            shloka_id,
                            f"Shloka {shloka['shloka_number']}",
                            'shloka'
                        ))
                        seen_nodes.add(shloka_id)
                        edges.append(create_edge(chapter_id, shloka_id, "contains"))
                        edges.append(create_edge(theme_id, shloka_id, "references"))
        
        return nodes, edges

    def display_chapter_insights(self):
        """Display chapter insights with character-centric relationships."""
        st.header("Ontology of Characters")

        # Chapter selection
        chapters = self.data.get("chapters", [])
        if not chapters:
            st.error("No chapters found in the data.")
            return

        selected_chapter_num = st.sidebar.selectbox(
            "Select a Chapter", 
            [chapter["number"] for chapter in chapters],
            format_func=lambda num: f"Chapter {num}"
        )

        selected_chapter = next(
            (chapter for chapter in chapters if chapter["number"] == selected_chapter_num), 
            None
        )
        if not selected_chapter:
            st.error("Invalid chapter selected.")
            return

        # Display chapter information in expander
        with st.expander(f"Chapter {selected_chapter['number']}: {selected_chapter['name']}"):
            st.markdown("### Summary")
            st.write(selected_chapter.get("summary", "No summary available."))

        st.markdown("### Character Relationship Graph")
        
        # Create character relationship graph
        nodes = []
        edges = []
        seen_nodes = set()
        
        key_events = selected_chapter.get("key_events", [])
        for event in key_events:
            event_id = f"Event_{event['event']}"
            if event_id not in seen_nodes:
                nodes.append(create_node(event_id, event['event'], 'event'))
                seen_nodes.add(event_id)
            
            for char in event['characters']:
                char_id = f"Character_{char}"
                if char_id not in seen_nodes:
                    nodes.append(create_node(char_id, char, 'character'))
                    seen_nodes.add(char_id)
                edges.append(create_edge(char_id, event_id))
            
            for shloka_num in event['shlokas']:
                shloka_id = f"Shloka_{selected_chapter_num}_{shloka_num}"
                if shloka_id not in seen_nodes:
                    nodes.append(create_node(shloka_id, f"Shloka {shloka_num}", 'shloka'))
                    seen_nodes.add(shloka_id)
                edges.append(create_edge(event_id, shloka_id))

        # Display Character Details
        st.markdown("### Character Details")
        
        # Get all unique characters from events
        unique_characters = set()
        for event in key_events:
            unique_characters.update(event['characters'])
        
        for char in unique_characters:
            with st.expander(f"{char}", expanded=False):
                # Display character description
                char_info = next((c for c in selected_chapter.get('characters', []) 
                                if c['name'] == char), None)
                if char_info:
                    st.markdown("**Description:**")
                    st.write(char_info['description'])
                
                # Find events involving this character
                char_events = [event for event in key_events if char in event['characters']]
                
                if char_events:
                    st.markdown("**Associated Events and Teachings:**")
                    for event_index, event in enumerate(char_events):
                        st.markdown(f"### {event['event']}")
                        
                        for shloka_index, shloka_num in enumerate(event['shlokas']):
                            shloka = next((s for s in selected_chapter['shlokas'] 
                                        if s['shloka_number'] == shloka_num), None)
                            
                            if shloka:
                                st.markdown(f"#### Shloka {shloka_num}")
                                
                                # Sanskrit Text Section
                                shloka_text = shloka.get('sanskrit_text', '')
                                if shloka_text:
                                    col1, col2 = st.columns([1, 4])
                                    with col1:
                                        if st.button("🔊 Sanskrit", 
                                                   key=f"sanskrit_{selected_chapter_num}_{char}_{event_index}_{shloka_index}"):
                                            audio_file = generate_audio(
                                                shloka_text,
                                                filename=f"sanskrit_{selected_chapter_num}_{shloka_num}.mp3",
                                                lang='hi'
                                            )
                                            st.audio(audio_file, format="audio/mp3")
                                    with col2:
                                        st.markdown("**Sanskrit Text:**")
                                        st.text(shloka_text)
                                
                                # English Sections
                                if 'transliteration' in shloka:
                                    # Create English text without transliteration
                                    english_text = f"Meaning: {shloka.get('meaning', '')}\n\n"
                                    if 'interpretation' in shloka:
                                        english_text += f"Interpretation: {shloka['interpretation']}\n\n"
                                    if 'life_application' in shloka:
                                        english_text += f"Life Application: {shloka['life_application']}"
                                    
                                    col1, col2 = st.columns([1, 4])
                                    with col1:
                                        if st.button("🔊 Explanation", 
                                                   key=f"english_{selected_chapter_num}_{char}_{event_index}_{shloka_index}"):
                                            audio_file = generate_audio(
                                                english_text,
                                                filename=f"english_{selected_chapter_num}_{shloka_num}.mp3",
                                                lang='en'
                                            )
                                            st.audio(audio_file, format="audio/mp3")
                                    
                                    # Display text sections
                                    with col2:
                                        if 'transliteration' in shloka:
                                            st.markdown("**Transliteration:**")
                                            st.write(shloka['transliteration'])
                                        
                                        st.markdown("**Meaning:**")
                                        st.write(shloka['meaning'])
                                        
                                        if 'interpretation' in shloka:
                                            st.markdown("**Interpretation:**")
                                            st.write(shloka['interpretation'])
                                        
                                        if 'life_application' in shloka:
                                            st.markdown("**Life Application:**")
                                            st.write(shloka['life_application'])

                
                # Display character relationships
                char_relationships = [
                    rel for rel in selected_chapter.get('character_relationships', [])
                    if char in rel['from'] or char in rel['to']
                ]
                
                if char_relationships:
                    st.markdown("**Character Relationships:**")
                    for rel in char_relationships:
                        st.markdown(f"- {rel['description']}")

        # Display the graph
        config = create_agraph_config()
        agraph(nodes=nodes, edges=edges, config=config)



def get_themes_from_chapters(data):
    """Extract all unique themes from chapters with their shloka counts"""
    theme_counts = {}
    for chapter in data['chapters']:
        # Get themes from both main_theme and philosophical_aspects
        themes = set()
        if 'main_theme' in chapter:
            themes.add(chapter['main_theme'])
        if 'philosophical_aspects' in chapter:
            themes.update(chapter['philosophical_aspects'])
        
        # Count relevant shlokas for each theme
        for theme in themes:
            if theme not in theme_counts:
                theme_counts[theme] = 0
            
            # Count shlokas that have keywords matching the theme
            theme_counts[theme] += len([
                shloka for shloka in chapter.get('shlokas', [])
                if any(kw.lower() in theme.lower() for kw in shloka.get('keywords', []))
            ])
    
    # Sort themes by shloka count in descending order
    sorted_themes = sorted(
        theme_counts.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Return list of tuples (theme, count)
    return sorted_themes

def find_chapters_by_theme(data, theme):
    """Find all chapters that contain a specific theme"""
    matching_chapters = []
    for chapter in data['chapters']:
        if ('main_theme' in chapter and theme in chapter['main_theme']) or \
        ('philosophical_aspects' in chapter and theme in chapter['philosophical_aspects']):
            matching_chapters.append(chapter)
    return matching_chapters
    

def main():
    st.set_page_config(page_title="Bhagavad Gita Knowledge Graph", layout="wide")
    st.title("Bhagavad Gita Knowledge Graph")
    
    # Initialize the RAG system
    rag = GitaGraphRAG()
    
    if not rag.data:
        st.error("Failed to load Bhagavad Gita data.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    view_option = st.sidebar.selectbox(
        "Select View",
        ["Chapter Topology", "Ontologies of Wisdom ", "Philosophical Themes Triples","Ontology of Characters"]
    )
    
    if view_option == "Chapter Topology":
        st.header("Chapter Topology")
        
        # Select chapter
        chapter_numbers = [ch['number'] for ch in rag.data['chapters']]
        selected_chapter_num = st.sidebar.selectbox(
            "Select Chapter",
            sorted(chapter_numbers),
            key='chapter_topology_select'  # Add a unique key
        )
        
        # Get selected chapter data
        chapter_data = next((ch for ch in rag.data['chapters'] 
                        if ch['number'] == selected_chapter_num), None)
        
        if chapter_data:
            st.subheader(f"Chapter {selected_chapter_num}: {chapter_data['name']}")
            
            # Create two tabs
            content_tab, graph_tab = st.tabs(["Chapter Content", "Knowledge Graph"])
            
            with content_tab:
                # Summary first
                st.markdown("### Summary")
                st.write(chapter_data['summary'])
                
                # Display shlokas
                st.markdown("### Shlokas")
                for shloka in chapter_data.get('shlokas', []):
                    with st.expander(f"Shloka {shloka['shloka_number']}"):
                        # Extract Sanskrit text
                        shloka_text = shloka.get('sanskrit_text', '')
                        
                        # Add Play buttons in columns
                        if shloka_text:
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button("🔊 Sanskrit", 
                                           key=f"sanskrit_ch_{selected_chapter_num}_{shloka['shloka_number']}"):
                                    audio_file = generate_audio(
                                        shloka_text,
                                        filename=f"sanskrit_{selected_chapter_num}_{shloka['shloka_number']}.mp3",
                                        lang='hi'
                                    )
                                    st.audio(audio_file, format="audio/mp3")
                            with col2:
                                st.markdown("**Sanskrit Text:**")
                                st.text(shloka_text)
                        
                        # English sections
                        if 'transliteration' in shloka:
                            # Create English text without transliteration
                            english_text = f"Meaning: {shloka.get('meaning', '')}\n\n"
                            if 'interpretation' in shloka:
                                english_text += f"Interpretation: {shloka['interpretation']}\n\n"
                            if 'life_application' in shloka:
                                english_text += f"Life Application: {shloka['life_application']}"
                            
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button("🔊 Explanation", 
                                           key=f"english_ch_{selected_chapter_num}_{shloka['shloka_number']}"):
                                    audio_file = generate_audio(
                                        english_text,
                                        filename=f"english_{selected_chapter_num}_{shloka['shloka_number']}.mp3",
                                        lang='en'
                                    )
                                    st.audio(audio_file, format="audio/mp3")
                            
                            # Display text sections
                            with col2:
                                if 'transliteration' in shloka:
                                    st.markdown("**Transliteration:**")
                                    st.write(shloka['transliteration'])
                                
                                st.markdown("**Meaning:**")
                                st.write(shloka['meaning'])
                                
                                if 'interpretation' in shloka:
                                    st.markdown("**Interpretation:**")
                                    st.write(shloka['interpretation'])
                                
                                if 'life_application' in shloka:
                                    st.markdown("**Life Application:**")
                                    st.write(shloka['life_application'])
            
            with graph_tab:
                st.markdown("### Chapter Knowledge Graph")
                
                # Force initial render with a state variable
                if 'first_render' not in st.session_state:
                    st.session_state.first_render = True
                    # Force rerun on first render
                    st.rerun()
                
                # Create the graph
                nodes, edges = rag.visualize_chapter_graph(f"Chapter_{selected_chapter_num}")
                config = create_agraph_config()
                agraph(nodes=nodes, edges=edges, config=config)
                
                # Clear the first render flag
                if st.session_state.first_render:
                    st.session_state.first_render = False

    elif view_option == "Ontologies of Wisdom ":
        st.header("Knowledge Pathways from Bhagavad Gita for Wisdom of Life")
        
        # Convert dropdown to horizontal radio buttons
        problems = list(rag.data['problem_solutions_map'].keys())
        selected_problem = st.radio(
            "Select a problem to explore solutions",
            problems,
            format_func=lambda x: x.replace('_', ' ').title(),
            horizontal=True  # This makes the radio buttons appear horizontally
        )
        
        if selected_problem:
            problem_data = rag.data['problem_solutions_map'][selected_problem]
            
            # Display problem description
            st.subheader("Description")
            st.write(problem_data['description'])
            
            # Display relevant shlokas first
            st.subheader("Relevant Shlokas")
            for ref in problem_data['references']:
                shloka = rag.get_shloka_by_reference(ref['chapter'], ref['shloka'])
                if shloka:
                    with st.expander(f"Chapter {ref['chapter']}, Shloka {ref['shloka']}"):
                        shloka_text = shloka.get('sanskrit_text', '')
                        
                        # Add Play buttons in columns for Sanskrit
                        if shloka_text:
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button("🔊 Sanskrit", 
                                           key=f"sanskrit_wisdom_{ref['chapter']}_{ref['shloka']}"):
                                    audio_file = generate_audio(
                                        shloka_text,
                                        filename=f"sanskrit_{ref['chapter']}_{ref['shloka']}.mp3",
                                        lang='hi'
                                    )
                                    st.audio(audio_file, format="audio/mp3")
                            with col2:
                                st.markdown("**Sanskrit Text:**")
                                st.text(shloka_text)
                        
                        # English sections
                        if 'transliteration' in shloka:
                            # Create English text without transliteration
                            english_text = f"Meaning: {shloka.get('meaning', '')}\n\n"
                            if 'interpretation' in shloka:
                                english_text += f"Interpretation: {shloka['interpretation']}\n\n"
                            if 'life_application' in shloka:
                                english_text += f"Life Application: {shloka['life_application']}"
                            
                            col1, col2 = st.columns([1, 4])
                            with col1:
                                if st.button("🔊 Explanation", 
                                           key=f"english_wisdom_{ref['chapter']}_{ref['shloka']}"):
                                    audio_file = generate_audio(
                                        english_text,
                                        filename=f"english_{ref['chapter']}_{ref['shloka']}.mp3",
                                        lang='en'
                                    )
                                    st.audio(audio_file, format="audio/mp3")
                            
                            # Display text sections
                            with col2:
                                if 'transliteration' in shloka:
                                    st.markdown("**Transliteration:**")
                                    st.write(shloka['transliteration'])
                                
                                st.markdown("**Meaning:**")
                                st.write(shloka['meaning'])
                                
                                if 'interpretation' in shloka:
                                    st.markdown("**Interpretation:**")
                                    st.write(shloka['interpretation'])
                                
                                if 'life_application' in shloka:
                                    st.markdown("**Life Application:**")
                                    st.write(shloka['life_application'])

            
            # Add separator before graph
            st.markdown("---")
            
            # Display the problem-solution graph at the bottom
            st.subheader("Problem-Solution Graph")
            problem_id = f"Problem_{selected_problem}"
            nodes, edges = rag.visualize_chapter_graph(problem_id)
            config = create_agraph_config()
            agraph(nodes=nodes, edges=edges, config=config)
    
    elif view_option == "Philosophical Themes Triples":
        st.header("Philosophical Themes Navigator")
        
        # Get sorted themes with counts
        theme_data = get_themes_from_chapters(rag.data)
        
        # Create display format for selectbox
        theme_options = [theme for theme, _ in theme_data]
        theme_format = {theme: f"{theme} ({count} shlokas)" 
                       for theme, count in theme_data}
        
        # Move theme selection to sidebar with count information
        selected_theme = st.sidebar.selectbox(
            "Select a Theme to Explore",
            theme_options,
            format_func=lambda x: theme_format[x]
        )
        
        if selected_theme:
            st.subheader(f"Exploring: {selected_theme}")
            
            # Theme Statistics using metrics
            related_chapters = find_chapters_by_theme(rag.data, selected_theme)
            total_shlokas = sum(len([s for s in ch.get('shlokas', []) 
                                if any(kw.lower() in selected_theme.lower() 
                                      for kw in s.get('keywords', []))]) 
                              for ch in related_chapters)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    label="📚 Related Chapters",
                    value=len(related_chapters)
                )
            with col2:
                st.metric(
                    label="🕉️ Relevant Shlokas",
                    value=total_shlokas
                )
            
            # Display related chapters in tabs
            if related_chapters:
                st.markdown("### Related Chapters")
                chapter_tabs = st.tabs([f"Chapter {ch['number']}: {ch['name']}" 
                                      for ch in related_chapters])
                
                for tab, chapter in zip(chapter_tabs, related_chapters):
                    with tab:
                        # Summary
                        st.markdown("#### Summary")
                        st.write(chapter['summary'])
                        
                        # Main Theme with markdown styling
                        st.markdown("#### Main Theme")
                        st.markdown(f"🎯 ***{chapter['main_theme']}***")
                        
                        # Philosophical aspects with decorative markdown
                        if 'philosophical_aspects' in chapter:
                            st.markdown("#### Philosophical Aspects")
                            for aspect in chapter['philosophical_aspects']:
                                st.markdown(f"✨ :blue[{aspect}]")
                                              
                        # Show relevant shlokas if they contain keywords from the theme
                        if 'shlokas' in chapter:
                            relevant_shlokas = [
                                shloka for shloka in chapter['shlokas']
                                if any(kw.lower() in selected_theme.lower() 
                                    for kw in shloka.get('keywords', []))
                            ]
                            
                            if relevant_shlokas:
                                st.markdown("**Relevant Shlokas:**")
                                # Create tabs for shlokas
                                shloka_tabs = st.tabs([f"Shloka {s['shloka_number']}" for s in relevant_shlokas])
                                
                                for shloka_tab, shloka in zip(shloka_tabs, relevant_shlokas):
                                    with shloka_tab:
                                        # Sanskrit Text Section
                                        shloka_text = shloka.get('sanskrit_text', '')
                                        if shloka_text:
                                            col1, col2 = st.columns([1, 4])
                                            with col1:
                                                if st.button("🔊 Sanskrit", 
                                                           key=f"sanskrit_theme_{chapter['number']}_{shloka['shloka_number']}"):
                                                    audio_file = generate_audio(
                                                        shloka_text,
                                                        filename=f"sanskrit_{chapter['number']}_{shloka['shloka_number']}.mp3",
                                                        lang='hi'
                                                    )
                                                    st.audio(audio_file, format="audio/mp3")
                                            with col2:
                                                st.markdown("**Sanskrit Text:**")
                                                st.text(shloka_text)
                                        
                                        # English sections
                                        if 'transliteration' in shloka:
                                            # Create English text without transliteration
                                            english_text = f"Meaning: {shloka.get('meaning', '')}\n\n"
                                            if 'interpretation' in shloka:
                                                english_text += f"Interpretation: {shloka['interpretation']}\n\n"
                                            if 'life_application' in shloka:
                                                english_text += f"Life Application: {shloka['life_application']}"
                                            
                                            col1, col2 = st.columns([1, 4])
                                            with col1:
                                                if st.button("🔊 Explanation", 
                                                           key=f"english_theme_{chapter['number']}_{shloka['shloka_number']}"):
                                                    audio_file = generate_audio(
                                                        english_text,
                                                        filename=f"english_{chapter['number']}_{shloka['shloka_number']}.mp3",
                                                        lang='en'
                                                    )
                                                    st.audio(audio_file, format="audio/mp3")
                                            
                                            # Display text sections
                                            with col2:
                                                if 'transliteration' in shloka:
                                                    st.markdown("**Transliteration:**")
                                                    st.write(shloka['transliteration'])
                                                
                                                st.markdown("**Meaning:**")
                                                st.write(shloka['meaning'])
                                                
                                                if 'interpretation' in shloka:
                                                    st.markdown("**Interpretation:**")
                                                    st.write(shloka['interpretation'])
                                                
                                                if 'life_application' in shloka:
                                                    st.markdown("**Life Application:**")
                                                    st.write(shloka['life_application'])

                                                                            # Display the graph
                        st.markdown("#### Theme Relationships")
                        nodes, edges = rag.visualize_theme_relationships(selected_theme, [chapter])
                        config = create_agraph_config()
                        agraph(nodes=nodes, edges=edges, config=config)
                        
                        # Add a divider between chapters
                        st.markdown("---")

    if view_option == "Ontology of Characters":
        rag.display_chapter_insights()


if __name__ == "__main__":
    main()
