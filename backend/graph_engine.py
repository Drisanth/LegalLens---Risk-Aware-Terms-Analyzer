import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class GraphEngine:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, clauses, embeddings, similarities=None, threshold=0.7):
        """
        Builds a dependency graph where nodes are clauses and edges represent semantic similarity.
        """
        self.graph.clear()
        
        # Add nodes
        for idx, clause_data in enumerate(clauses):
            # clause_data is expected to be a dict with 'id', 'text', 'base_risk', etc.
            self.graph.add_node(idx, **clause_data)
        
        # Calculate similarities if not provided
        if similarities is None and len(embeddings) > 0:
            similarities = cosine_similarity(embeddings)
            
        # Add edges based on similarity threshold
        # We only look at upper triangle to avoid duplicates, but graph is directed if we want flow.
        # For risk propagation, usually undirected or mutual dependency. Let's make it symmetric for now.
        num_nodes = len(clauses)
        for i in range(num_nodes):
            for j in range(i + 1, num_nodes):
                sim = similarities[i][j]
                if sim > threshold:
                    # Semantic link
                    self.graph.add_edge(i, j, weight=sim, type="semantic")
                    self.graph.add_edge(j, i, weight=sim, type="semantic")

    def propagate_risk(self, alpha=0.3, max_iter=10):
        """
        Implements the patent core propagation formula:
        R_propagated = R_base + alpha * Σ (W_ij * R_j)
        
        Iterative approach to allow risk to flow through the network.
        """
        nodes = self.graph.nodes(data=True)
        
        # Initialize current risk with base risk
        current_risks = {n: data.get('base_risk', 0.0) for n, data in nodes}
        
        for _ in range(max_iter):
            new_risks = current_risks.copy()
            
            for node_id in self.graph.nodes():
                # Calculate aggregated neighbor risk
                neighbor_risk_sum = 0.0
                neighbors = list(self.graph.neighbors(node_id))
                
                if not neighbors:
                    continue
                    
                for neighbor_id in neighbors:
                    weight = self.graph[node_id][neighbor_id].get('weight', 0.0)
                    neighbor_risk_sum += weight * current_risks[neighbor_id]
                
                # Apply formula
                # R_new = R_base + alpha * neighbor_sum
                # We can also normalize neighbor_sum or just let it accumulate (damped by alpha)
                base_risk = self.graph.nodes[node_id].get('base_risk', 0.0)
                propagated_val = base_risk + (alpha * neighbor_risk_sum)
                
                # Normalize/Clamp to 0-1
                new_risks[node_id] = min(max(propagated_val, 0.0), 1.0)
            
            # Check convergence (optional, simple check)
            if all(abs(new_risks[n] - current_risks[n]) < 0.01 for n in current_risks):
                break
                
            current_risks = new_risks

        # Update graph with final scores
        for node_id, risk in current_risks.items():
            self.graph.nodes[node_id]['propagated_risk'] = risk
            
        return current_risks

    def get_graph_metadata(self):
        return nx.node_link_data(self.graph)
