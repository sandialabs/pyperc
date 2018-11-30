import plotly
import pandas as pd

def plot_3d_network(G, node_attribute=None, title=None,
               node_size=7, node_range = [None,None], node_cmap='Viridis',
               link_width=1, add_colorbar=True, reverse_colormap=False,
               figsize=[700, 450], node_labels=True, round_ndigits=2, 
               filename=None, auto_open=True):
    """
    Create a 3D pore network graphic using plotly
    """
    # Node attribute
    if isinstance(node_attribute, list):
        node_attribute = dict(zip(node_attribute,[1]*len(node_attribute)))
    if isinstance(node_attribute, pd.Series):
        node_attribute = dict(node_attribute)
        
    # Create edge trace
    edge_trace = plotly.graph_objs.Scatter3d(
        x=[], 
        y=[], 
        z=[],
        text=[],
        hoverinfo='text',
        mode='lines',
        line=dict(
            #colorscale=link_cmap,
            reversescale=reverse_colormap,
            color='#888', #[], 
            width=link_width))
    if node_attribute:
        A = pd.Series(dict([(n1,list(n2.keys())) for n1,n2 in G.adj.items()]))
        for node in node_attribute.keys(): 
            for neigh in A[node]:
                x0, y0, z0 = G.node[node]['pos']
                x1, y1, z1 = G.node[neigh]['pos']
                edge_trace['x'] += tuple([x0, x1, None])
                edge_trace['y'] += tuple([y0, y1, None])
                edge_trace['z'] += tuple([z0, z1, None])
    else:
        for edge in list(G.edges()):
            x0, y0, z0 = G.node[edge[0]]['pos']
            x1, y1, z1 = G.node[edge[1]]['pos']
            edge_trace['x'] += tuple([x0, x1, None])
            edge_trace['y'] += tuple([y0, y1, None])
            edge_trace['z'] += tuple([z0, z1, None])
    
    # Create node trace      
    node_trace = plotly.graph_objs.Scatter3d(
        x=[], 
        y=[], 
        z=[],
        text=[],
        hoverinfo='text',
        mode='markers', 
        marker=dict(
            showscale=add_colorbar,
            colorscale=node_cmap, 
            cmin=node_range[0],
            cmax=node_range[1],
            reversescale=reverse_colormap,
            color=[], 
            size=node_size,
            #opacity=0.75,
            colorbar=dict(
                thickness=15,
                xanchor='left',
                titleside='right'),
            line=dict(width=0)))
    if node_attribute:
        nodes_to_plot = list(node_attribute.keys())
    else:
        nodes_to_plot = G.nodes()
    for node in nodes_to_plot: 
        x, y, z = G.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        node_trace['z'] += tuple([z])

        try:
            # Add node attributes
            node_trace['marker']['color'] += tuple([node_attribute[node]])
            #node_trace['marker']['size'].append(node_size)
            # Add node labels
            if node_labels:
                node_info = 'Node ' + str(node) + ', '+str(round(node_attribute[node],round_ndigits))
                node_trace['text'] += tuple([node_info])
        except:
            pass

    #node_trace['marker']['colorbar']['title'] = 'Node colorbar title'
    
    # Create figure
    data = [edge_trace, node_trace]
    layout = plotly.graph_objs.Layout(
                    title=title,
                    titlefont=dict(size=16),
                    showlegend=False, 
                    #width=figsize[0],
                    #height=figsize[1],
                    hovermode='closest',
                    margin=dict(b=20,l=5,r=5,t=40),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
    
    fig = plotly.graph_objs.Figure(data=data,layout=layout)
    if filename:
        plotly.offline.plot(fig, filename=filename, auto_open=auto_open)  
    else:
        plotly.offline.plot(fig, auto_open=auto_open)  

    
