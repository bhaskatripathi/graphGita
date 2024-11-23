import React from 'react';
import VisGraph, {GraphData, GraphEvents, Options} from 'react-vis-graph-wrapper';
import { Streamlit } from "streamlit-component-lib";
import { useRenderData } from "streamlit-component-lib-react-hooks";

function StreamlitVisGraph() {
  const renderData = useRenderData();

  const graphIn = JSON.parse(renderData.args["data"])

  const options: Options = JSON.parse(renderData.args["config"])

  const lookupNodeId = (lookupNode, myNodes) => myNodes.find(node => node.id === lookupNode);

  const graph: GraphData = {nodes: graphIn.nodes.slice(), edges: graphIn.edges.slice()}

  const events: GraphEvents = {
    selectNode: (event) => {
      Streamlit.setComponentValue(event.nodes[0]);
    }
    ,
    doubleClick: (event) => {
      const lookupNode = lookupNodeId(event.nodes[0], graph.nodes);
      if (lookupNode && lookupNode.link) {
        const link = lookupNode.link;
        if (link) {
          window.open(link);
        }
      }
    }
  };

  return (
    <span>
      <VisGraph
        graph={graph}
        options={options}
        events={events}
        ref = {(network: any) => {
          // console.log(network)
        }}
      />
    </span>
  )
}

export default StreamlitVisGraph;
