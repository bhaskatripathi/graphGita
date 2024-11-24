# README.md

## Overview

This project, **graphGita**, is the first modern re-interpretation of the Bhagavad Gita that utilizes **Knowledge Graphs** for accurate query retrieval and qunatify philosphical aspects to serve specific problem-solution needs. **_The ambitious goal is to incorporate over 200 versions of Gita interpretations_** written from time-to-time by different past and present scholars and integrate them in form of a sophisticated Knowledge Graph aided with modern retrieval technologies such as Monte Carlo Tree Search, and KG-RAG to provide a seamless multi-modal experience (text, image and video) to users. My primary goal is to increase readers' comprehension of philosophical ideas while offering pertinent perspectives for modern readers. Based on the literature reviews of each of the 18 chapters and how they relate to one another, the text is formatted into a graph structure. This structure may grow more sophisticated and complex with due course of time as the project progresses.

### Demo app link
https://graphgita.streamlit.app/

### Why Graph the Bhagvad Gita to Re-Understand it in Modern Times ?

There is a significant need to reinterpret ancient texts like the Bhagavad Gita in today's context. The teachings offer valuable perspectives on ethics, human behavior, and spirituality that remain applicable. However, traditional formats often fail to engage modern readers effectively. Advanced technologies, including knowledge graphs and machine learning, can make the wisdom of the Gita more accessible and relevant.

### Key Features

- **Knowledge Graph**: A structured representation of the Gita's text that highlights relationships between chapters, shlokas, characters, and themes.
- **Mathematical Analysis**: Uses mathematical techniques to analyze and interpret the teachings of the Gita.
- **Graph Retrieval-Augmented Generation (KG-RAG with MCTS)**: Knowledge Graph RAG with Monte Carlo Tree Search allows users to retrieve relevant information based on their queries.
- **Monte Carlo Tree Search**: Facilitates interactive exploration of the text, enabling non-linear engagement with the material.

## Problem Statement

### Why is this Project Required?

The Bhagavad Gita presents challenges for modern readers:

- **Complexity of Concepts**: The ideas within the Gita can be difficult to understand without contextual support or visual aids.
- **Linear Structure**: Traditional readings follow a linear narrative that may obscure important relationships between different teachings.
- **Lack of Interactivity**: Static texts do not engage readers in an interactive manner.

## Overview of Bhagavad Gita Chapters

The Bhagavad Gita consists of 18 chapters, each focusing on different aspects of dharma, karma, and spiritual knowledge. Below is a comprehensive breakdown of each chapter:

| Chapter | Name | Sanskrit Name | Total Verses | Focus Area |
|---------|------|---------------|--------------|------------|
| 1 | The Observation of the Armies | Arjuna Visada Yoga | 47 | Introduces the setting and Arjuna's dilemma |
| 2 | The Way of Knowledge | Sankhya Yoga | 72 | Fundamental philosophy and nature of Self |
| 3 | The Way of Action | Karma Yoga | 43 | The importance of righteous action |
| 4 | The Way of Knowledge and Action | Jnana Yoga | 42 | Divine nature of action and wisdom |
| 5 | The Way of Renunciation | Karma Sanyasa Yoga | 29 | Balance between action and renunciation |
| 6 | The Way of Meditation | Dhyana Yoga | 47 | Practice of meditation and mind control |
| 7 | The Way of Knowledge and Realization | Jnana Vijnana Yoga | 30 | Understanding the absolute truth |
| 8 | The Way to the Supreme | Aksara Brahma Yoga | 28 | Process of reaching the ultimate reality |
| 9 | The Way of Royal Knowledge | Raja Vidya Yoga | 34 | Supreme knowledge and devotion |
| 10 | The Divine Manifestations | Vibhuti Yoga | 42 | Divine manifestations in the world |
| 11 | The Vision of the Universal Form | Visvarupa Darsana Yoga | 55 | Revelation of the cosmic form |
| 12 | The Way of Devotion | Bhakti Yoga | 20 | Path of devotional service |
| 13 | The Field and its Knower | Ksetra Ksetrajna Vibhaga Yoga | 35 | Nature, the enjoyer, and consciousness |
| 14 | The Three Modes of Material Nature | Gunatraya Vibhaga Yoga | 27 | Understanding material qualities |
| 15 | The Supreme Person | Purusottama Yoga | 20 | The ultimate truth about God |
| 16 | The Divine and Demoniac Natures | Daivasura Sampad Vibhaga Yoga | 24 | Divine and demoniac qualities |
| 17 | The Three Divisions of Faith | Sraddhatraya Vibhaga Yoga | 28 | Three types of faith |
| 18 | The Way of Liberation | Moksa Sanyasa Yoga | 78 | Conclusion and path to liberation |

**Total Verses**: 701

### Why Graph the Gita?

The Bhagavad Gita, while profound in its teachings, can be challenging to navigate and understand in its traditional linear format. By representing it as a knowledge graph:

1. **Non-Linear Navigation**: Readers can explore connections between concepts across different chapters
2. **Contextual Understanding**: Related verses and themes can be easily discovered regardless of their location in the text
3. **Modern Accessibility**: Complex philosophical concepts become more approachable through visual and interactive representations
4. **Pattern Recognition**: Mathematical analysis reveals structural patterns and thematic relationships that might not be apparent in linear reading
5. **Personalized Learning**: MCTS-powered exploration allows readers to follow paths most relevant to their interests and questions

This graphical representation transforms the ancient text into a dynamic knowledge base that preserves its authenticity while making it more accessible to modern readers.

### Limitations of Existing Texts

Readers today may encounter:

- **Interpretation Variability**: Different translations can lead to confusion regarding core messages.
- **Contextual Relevance**: The teachings may seem disconnected from modern life challenges without clear connections to contemporary issues.

## Life Problems and Their Solutions in the Bhagavad Gita

The Bhagavad Gita offers guidance for various life challenges. Below is a mapping of common problems to relevant verses:

| Problem | Description | Chapter:Verse References |
|---------|-------------|-------------------------|
| Anger | Managing and overcoming anger | 2:56, 2:62, 2:63, 5:26, 16:1-3, 16:21 |
| Depression | Dealing with depression and mental suffering | 2:3, 2:14, 5:21 |
| Confusion | Clearing confusion and gaining clarity | 2:7, 3:2, 18:61 |
| Envy | Dealing with envy and jealousy | 12:13-14, 16:19, 18:71 |
| Death of Loved One | Coping with death of a loved one | 2:13, 2:20, 2:22, 2:25, 2:27 |
| Demotivation | Dealing with lack of motivation | 11:33, 18:48, 18:78 |
| Discrimination | Dealing with discrimination and unfair treatment | 5:18-19, 6:32, 9:29 |
| Fear | Overcoming fear and anxiety | 4:10, 11:50, 18:30 |
| Guilt | Dealing with guilt and feelings of sinfulness | 4:36-37, 5:10, 9:30, 10:3, 14:6, 18:66 |
| Forgetfulness | Dealing with forgetfulness | 15:15, 18:61 |
| Greed | Overcoming greed and attachment | 14:17, 16:21, 17:25 |
| Laziness | Overcoming laziness and procrastination | 3:8, 3:20, 6:16, 18:39 |
| Loneliness | Dealing with feelings of loneliness | 6:30, 9:29, 13:16, 13:18 |
| Hopelessness | Dealing with hopelessness and despair | 4:11, 6:22, 9:34, 18:66, 18:78 |
| Lust | Controlling lust and sensual desires | 3:37, 3:41, 3:43, 5:22, 16:21 |
| Forgiveness | Learning and practicing forgiveness | 11:44, 12:13-14, 16:1-3 |
| Pride | Managing ego and pride | 16:4, 16:13-15, 18:26, 18:58 |
| Inner Peace | Finding inner peace and tranquility | 2:66, 2:71, 4:39, 5:29, 8:28 |
| Temptation | Dealing with temptations | 2:60-61, 2:70, 7:14 |
| Mental Control | Managing an uncontrolled mind | 6:5-6, 6:26, 6:35 |

#Graph Examples
![GraphGita Overview](images/1.png)
*Figure 1: Overview of the GraphGita Knowledge Graph.*
![Chapter Relationships](images/2.png)
*Figure 2: Visualization of relationships between chapters.*
![Philosophical Concepts](images/3.png)
*Figure 3: Mapping of philosophical concepts within the Gita.*
![User Interface](images/4.png)
*Figure 4: Screenshot of the user interface for exploring the Knowledge Graph.*


> **Note**: The verse numbers are presented in `chapter:verse` format. Ranges (e.g., 16:1-3) indicate consecutive verses addressing the same topic.

## Proposed Solution: RAG-Based Gita Enabled by Knowledge Graph

### Benefits of Knowledge Graphs and MCTS

1. **Enhanced Analysis**: Utilizing GNNs allows for deeper examination of the Gita's teachings and facilitates exploration of relationships between philosophical concepts.
  
2. **Problem-Solving Framework**: The project aims to create mappings of common human problems addressed in the Gita, offering practical solutions based on authentic interpretations.

3. **Interactive Exploration**: MCTS enables users to engage with the material dynamically, simulating various paths through the text.

4. **Scientific Contribution**: This initiative merges ancient philosophy with modern computational techniques, contributing valuable Indic datasets for research in humanities and AI fields.

## Technical Implementation

### Tech Stack

- **Programming Language**: Python
- **Web Framework**: Flask or FastAPI for building APIs
- **Database**: Neo4j or MongoDB for storing Knowledge Graph data
- **Machine Learning Libraries**: TensorFlow or PyTorch for developing Graph Neural Networks
- **Data Processing Libraries**: Pandas for data manipulation; Boto3 for AWS integration
- **Visualization Tools**: D3.js or Plotly for graphical representations of data
- **Cloud Services**: AWS (S3 for storage, Lambda for serverless functions)

### Requirements

- Python 3.x
- Boto3
- Requests
- Pandas
- TQDM
- JSON Schema
- Logging

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/bhaskatripathi/graphGita
   cd graphGita
   ```

2. Install required packages:
   ```bash
   pip install boto3 requests pandas tqdm jsonschema
   ```

3. Set up your AWS credentials for S3 and Textract services.

### Key Functionalities

- **Chapter Information**: Structured data for each chapter derived from authentic sources.
  
- **AWS Client**: Facilitates access to S3 storage and document processing via Textract.

- **Claude API Interaction**: Invokes the Claude model for generating insights based on user prompts.

- **Graph Neural Network Integration**: Enables training and fine-tuning of models on Indic datasets.

## Example Outputs

The generated outputs are structured in JSON format. For example, a chapter summary might look like this:

```json
{
    "summary": "Brief summary of the chapter",
    "main_theme": "The overarching theme of the chapter",
    "philosophical_aspects": ["List of key philosophical concepts addressed"],
    "life_problems_addressed": ["List of life problems or questions this chapter helps address"],
    "yoga_type": "The primary type of yoga discussed in this chapter"
}
```
## Contributing

Contributions are welcome. Please submit a pull request or open an issue for any enhancements or bug fixes.

## How to Cite
If you use **graphGita** in your research or project, please cite it as follows:

### BibTeX Entry
```bibtex
@software{tripathi2024graphgita,
  author       = {Bhaskar Tripathi},
  title        = {graphGita: A Knowledge Graph Approach to Bhagavad Gita Interpretation},
  year         = 2024,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.14211453},
  url          = {https://doi.org/10.5281/zenodo.14211453}
}
```
## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=bhaskatripathi/graphGita&type=Date)](https://star-history.com/#bhaskatripathi/graphGita&Date)

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Future Pipeline
1. Create a Knowledge Graph based RAG on more than 200 Gita versions and find the overlaping philosophie, conflicting, and their relationships to the original Bhagwad Gita.
2. Integrate more sophisticated retrieval technologies for multi-hop query improvements.
3. Integrate below versions of popular Gita books:
- *Bhagavad Gita*: The most famous, part of the Mahabharata, focusing on duty and righteousness.
- *Anugita*: A conversation between Arjuna and Krishna after the war.
- *Avadhuta Gita*: Emphasizes the non-dual nature of reality.
- *Ashtavakra Gita*: A dialogue on renunciation between King Janak and Ashtavakra.
- *Ishvara Gita*: Found in the Kurma Purana.
- *Kapila Gita*: From the Bhagavatam, discussing Sankhya philosophy.
- *Ganesha Gita*: Related to Lord Ganesha, found in the Ganesh Purana.
- *Devi Gita*: Focuses on the divine feminine aspect.
- *Bhagavad-gita As It Is* by A.C. Bhaktivedanta Swami Prabhupada ISKCON
- *Bhagavad-Gita in English* from the International Gita Society
- The *Divine Life Society's version* of the Bhagavad Gita

