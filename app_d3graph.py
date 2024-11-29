import streamlit as st
import json
import networkx as nx
from streamlit_d3graph import d3graph
from typing import Dict, List, Optional, Union
import os

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

    def visualize_chapter_graph(self, node_id: str) -> d3graph:
        """Create labeled D3 visualization of the graph for a specific node"""
        # Create subgraph for the selected node
        subgraph = nx.ego_graph(self.G, node_id, radius=1)
        adjmat = nx.adjacency_matrix(subgraph).todense()
        
        # Get node types and create color mapping
        node_types = [self.G.nodes[node]['type'] for node in subgraph.nodes()]
        type_to_color = {
            'problem': '#FFD700',  # Yellow
            'chapter': '#87CEEB',  # Sky blue
            'shloka': '#F08080'    # Light coral
        }
        node_colors = [type_to_color.get(t, '#90EE90') for t in node_types]
        
        # Create labeled visualization
        d3 = d3graph(collision=1, charge=250)
        d3.graph(adjmat)
        d3.set_node_properties(
            label=list(subgraph.nodes()),
            color=node_colors,
            cmap="Set1"
        )
        
        return d3

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
        
        # Initialize graph
        character_graph = nx.Graph()
        
        # Add nodes and edges
        key_events = selected_chapter.get("key_events", [])
        for event in key_events:
            event_id = f"Event_{event['event']}"
            character_graph.add_node(event_id, type='event')
            
            # Add character nodes and connect to event
            for char in event['characters']:
                char_id = f"Character_{char}"
                character_graph.add_node(char_id, type='character')
                character_graph.add_edge(char_id, event_id)
            
            # Add shloka nodes and connect to event
            for shloka_num in event['shlokas']:
                shloka_id = f"Shloka_{selected_chapter_num}_{shloka_num}"
                character_graph.add_node(shloka_id, type='shloka')
                character_graph.add_edge(event_id, shloka_id)

        # Convert to adjacency matrix
        adjmat = nx.adjacency_matrix(character_graph).todense()
        d3 = d3graph(collision=1, charge=250, slider=[0, 7])
        d3.graph(adjmat)

        # Get exact list of nodes that will be used by d3graph
        nodes = list(character_graph.nodes())
        
        # Create colors list matching exactly with nodes
        node_colors = []
        node_labels = []
        node_sizes = []
        
        for node in nodes:
            node_type = character_graph.nodes[node]['type']
            # Assign colors based on type
            if node_type == 'character':
                node_colors.append('#FFD700')  # Gold for characters
                node_sizes.append(30)
            elif node_type == 'event':
                node_colors.append('#87CEEB')  # Sky blue for events
                node_sizes.append(25)
            else:  # shloka
                node_colors.append('#F08080')  # Light coral for shlokas
                node_sizes.append(20)
            
            # Create readable labels
            label = node.replace('_', ' ').replace(f'{selected_chapter_num} ', '')
            node_labels.append(label)

        # Set node properties ensuring all arrays match exactly
        d3.set_node_properties(
            label=node_labels,
            color=node_colors,
            size=node_sizes,
            edge_color="#00FFFF",
            cmap="Set1"
        )
        
        d3.show()

        # Wrap Character Details in an expander
        with st.expander("Character Details", expanded=False):
            unique_characters = set()
            for event in key_events:
                unique_characters.update(event['characters'])
            
            for char in unique_characters:
                # Use a container for each character
                char_container = st.container()
                with char_container:
                    st.markdown(f"## {char}")
                    
                    # Get character description
                    char_info = next((c for c in selected_chapter.get('characters', []) 
                                    if c['name'] == char), None)
                    if char_info:
                        st.markdown("**Description:**")
                        st.write(char_info['description'])
                    
                    # Find events involving this character
                    char_events = [event for event in key_events if char in event['characters']]
                    
                    if char_events:
                        st.markdown("**Associated Events and Teachings:**")
                        for event in char_events:
                            st.markdown(f"### {event['event']}")
                            
                            # Display detailed shloka information
                            for shloka_num in event['shlokas']:
                                shloka = next((s for s in selected_chapter['shlokas'] 
                                            if s['shloka_number'] == shloka_num), None)
                                if shloka:
                                    # Use a separate container for each shloka
                                    shloka_container = st.container()
                                    with shloka_container:
                                        st.markdown(f"#### Shloka {shloka_num}")
                                        
                                        if 'sanskrit_text' in shloka:
                                            st.markdown("**Sanskrit Text:**")
                                            st.text(shloka['sanskrit_text'])
                                        
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
                    
                    # Find character relationships
                    char_relationships = [
                        rel for rel in selected_chapter.get('character_relationships', [])
                        if char in rel['from'] or char in rel['to']
                    ]
                    
                    if char_relationships:
                        st.markdown("**Character Relationships:**")
                        for rel in char_relationships:
                            st.markdown(f"- {rel['description']}")
                    
                    # Add a horizontal line between characters
                    st.markdown("---")

    def visualize_theme_relationships(self, selected_theme: str, related_chapters: list) -> d3graph:
        """Create a D3 visualization showing relationships between theme, chapters, and shlokas"""
        # Create a focused graph for the theme
        theme_graph = nx.Graph()
        theme_id = f"Theme_{selected_theme}"
        theme_graph.add_node(theme_id, type='theme', name=selected_theme)
        
        # Add related chapters and shlokas
        for chapter in related_chapters:
            chapter_id = f"Chapter_{chapter['number']}"
            theme_graph.add_node(chapter_id, 
                                type='chapter',
                                name=chapter['name'])
            theme_graph.add_edge(theme_id, chapter_id)
            
            # Add relevant shlokas from this chapter
            relevant_shlokas = [
                shloka for shloka in chapter.get('shlokas', [])
                if any(kw.lower() in selected_theme.lower() 
                    for kw in shloka.get('keywords', []))
            ]
            
            for shloka in relevant_shlokas:
                shloka_id = f"Shloka_{chapter['number']}_{shloka['shloka_number']}"
                theme_graph.add_node(shloka_id, 
                                    type='shloka',
                                    number=shloka['shloka_number'])
                # Connect shloka to both chapter and theme
                theme_graph.add_edge(chapter_id, shloka_id)
                theme_graph.add_edge(theme_id, shloka_id)

        # Convert to D3 graph
        adjmat = nx.adjacency_matrix(theme_graph).todense()
        d3 = d3graph(collision=1, charge=450)  # Increased charge for better spacing
        d3.graph(adjmat)

        # Get the nodes in the same order as they'll be used by d3graph
        nodes = list(theme_graph.nodes())

        # Create colors and sizes list matching exactly with nodes
        node_colors = []
        node_sizes = []
        node_labels = []

        for node in nodes:
            node_type = theme_graph.nodes[node].get('type')
            # Assign colors and sizes based on node type
            if node_type == 'theme':
                node_colors.append('#90EE90')  # Light green for theme
                node_sizes.append(40)
                node_labels.append(node.replace('Theme_', ''))
            elif node_type == 'chapter':
                node_colors.append('#87CEEB')  # Sky blue for chapters
                node_sizes.append(30)
                node_labels.append(node.replace('_', ' '))
            else:  # shloka
                node_colors.append('#F08080')  # Light coral for shlokas
                node_sizes.append(20)
                # Create a shorter label for shlokas
                chapter_num = node.split('_')[1]
                shloka_num = node.split('_')[2]
                node_labels.append(f"Sh {shloka_num}")

        # Set node properties
        d3.set_node_properties(
            label=node_labels,
            color=node_colors,
            size=node_sizes,
            edge_color="#00FFFF",
            cmap="Set1"
        )
        
        return d3




    
def get_themes_from_chapters(data):
    """Extract all unique themes from chapters"""
    themes = set()
    for chapter in data['chapters']:
        if 'philosophical_aspects' in chapter:
            themes.update(chapter['philosophical_aspects'])
        if 'main_theme' in chapter:
            themes.add(chapter['main_theme'])
    return sorted(list(themes))

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
            sorted(chapter_numbers)
        )
        
        # Get selected chapter data
        chapter_data = next((ch for ch in rag.data['chapters'] 
                        if ch['number'] == selected_chapter_num), None)
        
        if chapter_data:
            # Display chapter information
            st.subheader(f"Chapter {selected_chapter_num}: {chapter_data['name']}")
            
            # Summary first
            st.markdown("### Summary")
            st.write(chapter_data['summary'])
            
            # Display shlokas before the graph
            st.markdown("### Shlokas")
            for shloka in chapter_data.get('shlokas', []):
                with st.expander(f"Shloka {shloka['shloka_number']}"):
                    if 'sanskrit_text' in shloka:
                        st.markdown("**Sanskrit Text:**")
                        st.text(shloka['sanskrit_text'])
                    
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
            
            # Display the graph at the bottom
            st.markdown("---")  # Add a separator
            st.markdown("### Chapter Knowledge Graph")
            d3_graph = rag.visualize_chapter_graph(f"Chapter_{selected_chapter_num}")
            d3_graph.show()

    elif view_option == "Ontologies of Wisdom ":
        st.header("Knowledge Pathways from Bhagavad Gita for Wisdom of Life")
        
        # Group problems by category
        problems = list(rag.data['problem_solutions_map'].keys())
        selected_problem = st.selectbox(
            "Select a problem to explore solutions",
            problems,
            format_func=lambda x: x.replace('_', ' ').title()
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
                        st.markdown("**Sanskrit Text:**")
                        st.text(shloka['sanskrit_text'])
                        
                        if 'transliteration' in shloka:
                            st.markdown("**Transliteration:**")
                            st.write(shloka['transliteration'])
                        
                        st.markdown("**Meaning:**")
                        st.write(shloka['meaning'])
                        
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
            d3 = rag.visualize_chapter_graph(problem_id)
            d3.show()
    
    elif view_option == "Philosophical Themes Triples":
        st.header("Philosophical Themes Navigator")
        
        # Get all themes
        themes = get_themes_from_chapters(rag.data)
        
        # Theme selection
        selected_theme = st.selectbox(
            "Select a theme to explore",
            themes,
            format_func=lambda x: x.strip()
        )
        
        if selected_theme:
            # Display theme information
            st.subheader(f"Exploring: {selected_theme}")
            
            # Display theme statistics first
            st.markdown("### Theme Statistics")
            related_chapters = find_chapters_by_theme(rag.data, selected_theme)
            st.write(f"**Number of related chapters:** {len(related_chapters)}")
            total_shlokas = sum(len([s for s in ch.get('shlokas', []) 
                                if any(kw.lower() in selected_theme.lower() 
                                        for kw in s.get('keywords', []))]) 
                            for ch in related_chapters)
            st.write(f"**Number of relevant shlokas:** {total_shlokas}")
            
            # Display related problems if any
            if 'problem_solutions_map' in rag.data:
                related_problems = [
                    prob for prob, details in rag.data['problem_solutions_map'].items()
                    if selected_theme.lower() in details['description'].lower()
                ]
                if related_problems:
                    st.markdown("### Related Problems")
                    for problem in related_problems:
                        st.write(f"• {problem.replace('_', ' ').title()}")
            
            # Display related chapters and their shlokas
            st.markdown("### Related Chapters")
            for chapter in related_chapters:
                st.markdown(f"#### Chapter {chapter['number']}: {chapter['name']}")
                st.markdown("**Summary:**")
                st.write(chapter['summary'])
                
                if 'main_theme' in chapter:
                    st.markdown("**Main Theme:**")
                    st.write(chapter['main_theme'])
                
                if 'philosophical_aspects' in chapter:
                    st.markdown("**Philosophical Aspects:**")
                    aspects = [asp for asp in chapter['philosophical_aspects'] 
                            if selected_theme in asp]
                    for aspect in aspects:
                        st.write(f"• {aspect}")
                
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
                        
                        for tab, shloka in zip(shloka_tabs, relevant_shlokas):
                            with tab:
                                if 'sanskrit_text' in shloka:
                                    st.markdown("**Sanskrit:**")
                                    st.text(shloka['sanskrit_text'])
                                
                                st.markdown("**Meaning:**")
                                st.write(shloka['meaning'])
                                
                                st.markdown("**Interpretation:**")
                                st.write(shloka['interpretation'])
                
                # Add a divider between chapters
                st.markdown("---")
            
            # Display theme relationships graph at the bottom
            st.markdown("### Theme Relationships")
            d3 = rag.visualize_theme_relationships(selected_theme, related_chapters)
            d3.show()

    if view_option == "Ontology of Characters":
        rag.display_chapter_insights()


if __name__ == "__main__":
    main()
