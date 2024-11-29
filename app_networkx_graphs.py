
import streamlit as st
import json
import networkx as nx
import matplotlib.pyplot as plt
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
                #st.write("Available keys in JSON:", list(data.keys()))
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

    def visualize_chapter_graph(self, node_id: str) -> plt.Figure:
        """Create a visualization of the graph for a specific node"""
        subgraph = nx.ego_graph(self.G, node_id, radius=1)
        
        pos = nx.spring_layout(subgraph)
        plt.figure(figsize=(12, 8))
        
        # Draw nodes with different colors for different types
        node_colors = []
        for node in subgraph.nodes():
            node_type = self.G.nodes[node]['type']
            if node_type == 'problem':
                node_colors.append('yellow')
            elif node_type == 'chapter':
                node_colors.append('skyblue')
            elif node_type == 'shloka':
                node_colors.append('lightcoral')
            else:
                node_colors.append('lightgreen')
        
        nx.draw(subgraph, pos, with_labels=True, node_color=node_colors,
                node_size=2000, font_size=8)
        plt.title(f"Knowledge Graph for {node_id}")
        return plt
    
    def display_chapter_insights(self):
        """Display chapter insights for the selected chapter, including a focused graph."""
        st.header("Ontology of Characters")

        # Check if chapters exist in the data
        chapters = self.data.get("chapters", [])
        if not chapters:
            st.error("No chapters found in the data.")
            return

        # Sidebar dropdown for chapter selection
        chapter_numbers = [chapter["number"] for chapter in chapters]
        selected_chapter_num = st.sidebar.selectbox(
            "Select a Chapter", chapter_numbers, format_func=lambda num: f"Chapter {num}"
        )

        # Get the selected chapter
        selected_chapter = next(
            (chapter for chapter in chapters if chapter["number"] == selected_chapter_num), None
        )
        if not selected_chapter:
            st.error("Invalid chapter selected.")
            return

        # Display chapter details in an accordion
        with st.expander(f"Chapter {selected_chapter['number']}: {selected_chapter['name']}"):
            # Summary
            st.markdown("### Summary")
            st.write(selected_chapter.get("summary", "No summary available."))

            # Main Themes
            themes = selected_chapter.get("themes", [])
            if themes:
                st.markdown("### Main Themes")
                for theme in themes:
                    st.markdown(f"**{theme['name']}**: {theme['description']}")

            # Key Events
            key_events = selected_chapter.get("key_events", [])
            if key_events:
                st.markdown("### Key Events")
                for event in key_events:
                    st.markdown(f"#### {event['event']}")
                    st.write(f"**Associated Characters:** {', '.join(event['characters'])}")
                    st.write(f"**Associated Shlokas:** {', '.join(map(str, event['shlokas']))}")

                    # Display detailed shloka information
                    for shloka_num in event["shlokas"]:
                        shloka_data = next(
                            (shloka for shloka in selected_chapter.get("shlokas", [])
                                if shloka["shloka_number"] == shloka_num),
                            None,
                        )
                        if shloka_data:
                            st.markdown(f"##### Shloka {shloka_data['shloka_number']}")
                            st.markdown(f"**Sanskrit Text:**")
                            st.text(shloka_data.get("sanskrit_text", ""))
                            st.markdown(f"**Transliteration:**")
                            st.text(shloka_data.get("transliteration", ""))
                            st.markdown(f"**Meaning:**")
                            st.text(shloka_data.get("meaning", ""))
                            st.markdown(f"**Life Application:**")
                            st.text(shloka_data.get("life_application", ""))

        # Display the graph for the selected chapter
        self.visualize_character_graph(selected_chapter)

    def visualize_character_graph(self, chapter):
        """Visualize the character ontology for the selected chapter."""
        st.markdown("### Chapter Ontology Graph")

        # Build the graph for the selected chapter
        G = nx.DiGraph()
        chapter_node = f"Chapter {chapter['number']}: {chapter['name']}"
        G.add_node(chapter_node, type="chapter")

        key_events = chapter.get("key_events", [])
        for event in key_events:
            event_node = f"{chapter['name']} - {event['event']}"
            G.add_node(event_node, type="event")
            G.add_edge(chapter_node, event_node)

            # Add associated characters
            for character in event["characters"]:
                character_node = f"Character: {character}"
                G.add_node(character_node, type="character")
                G.add_edge(event_node, character_node)

        # Draw the graph
        pos = nx.spring_layout(G)
        plt.figure(figsize=(10, 6))

        # Node colors based on type
        node_colors = [
            "lightblue" if G.nodes[node]["type"] == "chapter"
            else "lightgreen" if G.nodes[node]["type"] == "event"
            else "lightcoral"
            for node in G.nodes
        ]

        nx.draw(
            G, pos, with_labels=True, node_size=2000, node_color=node_colors, font_size=8
        )
        st.pyplot(plt)

    
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
            col1, col2 = st.columns([2, 1])

            with col1:
                # Display chapter information
                st.subheader(f"Chapter {selected_chapter_num}: {chapter_data['name']}")

                # Summary
                st.markdown("### Summary")
                st.write(chapter_data['summary'])

                
                # Philosophical Aspects
                st.markdown("#### Philosophical Aspects")
                if 'philosophical_aspects' in chapter_data:
                    with st.expander("Philosophical Aspects"):
                        for aspect in chapter_data['philosophical_aspects']:
                            st.write(f"• {aspect}")

                # Life Problems Addressed
                st.markdown("#### Life Problems Addressed")
                if 'life_problems_addressed' in chapter_data:
                    with st.expander("Life Problems Addressed"):
                        for problem in chapter_data['life_problems_addressed']:
                            st.write(f"• {problem}")

                # Yoga Type
                st.markdown("#### Yoga Type")
                if 'yoga_type' in chapter_data:
                    with st.expander("Yoga Type"):
                        st.write(chapter_data['yoga_type'])

            with col2:
                # Display graph visualization
                st.markdown("####    Chapter Knowledge Graph")
                fig = rag.visualize_chapter_graph(f"Chapter_{selected_chapter_num}")
                st.pyplot(fig)

            # Display shlokas
            st.markdown("### Shlokas")
            if 'shlokas' in chapter_data:
                for shloka in chapter_data['shlokas']:
                    with st.expander(f"Shloka {shloka['shloka_number']}"):
                        if 'sanskrit_text' in shloka:
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

                        if 'keywords' in shloka:
                            st.markdown("**Keywords:**")
                            st.write(", ".join(shloka['keywords']))

    
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
            
            # Create columns for layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Display relevant shlokas
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
            
            with col2:
                # Visualize problem connections
                st.subheader("Problem-Solution Graph")
                problem_id = f"Problem_{selected_problem}"
                fig = rag.visualize_chapter_graph(problem_id)
                st.pyplot(fig)
    
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
            # Find chapters related to the theme
            related_chapters = find_chapters_by_theme(rag.data, selected_theme)
            
            # Display theme information
            st.subheader(f"Exploring: {selected_theme}")
            
            # Create columns for layout
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Display related chapters
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
                            # Create tabs for shlokas instead of nested expanders
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
            
            with col2:
                # Display theme relationships
                st.markdown("### Theme Relationships")
                
                # Create a focused graph for the theme
                theme_graph = nx.Graph()
                theme_id = f"Theme_{selected_theme}"
                theme_graph.add_node(theme_id, type='theme', name=selected_theme)
                
                # Add related chapters
                for chapter in related_chapters:
                    chapter_id = f"Chapter_{chapter['number']}"
                    theme_graph.add_node(chapter_id, 
                                    type='chapter',
                                    name=chapter['name'])
                    theme_graph.add_edge(theme_id, chapter_id)
                
                # Visualize theme relationships
                pos = nx.spring_layout(theme_graph)
                plt.figure(figsize=(8, 8))
                
                # Draw nodes with different colors
                node_colors = ['lightgreen' if node == theme_id else 'skyblue' 
                            for node in theme_graph.nodes()]
                
                nx.draw(theme_graph, pos, with_labels=True, 
                    node_color=node_colors,
                    node_size=2000, font_size=8)
                plt.title(f"Theme Relationships: {selected_theme}")
                st.pyplot(plt)
                
                # Display theme statistics
                st.markdown("### Theme Statistics")
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

    if view_option == "Ontology of Characters":
        
        rag.display_chapter_insights()


if __name__ == "__main__":
    main()
