import asyncio
import numpy as np
from typing import Dict, List, Optional, Any, Set, Tuple
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
import structlog

logger = structlog.get_logger()

@dataclass
class Hyperedge:
    """Hypergraph edge connecting multiple nodes"""
    edge_id: str
    nodes: Set[str]
    weight: float
    edge_type: str
    metadata: Dict[str, Any]
    created_at: datetime

@dataclass 
class HyperNode:
    """Node in hypergraph"""
    node_id: str
    node_type: str
    attributes: Dict[str, Any]
    degree: int = 0  # Number of hyperedges containing this node

class FinancialHypergraphProcessor:
    """Advanced hypergraph processing for multi-entity financial relationships"""
    
    def __init__(self):
        self.nodes: Dict[str, HyperNode] = {}
        self.hyperedges: Dict[str, Hyperedge] = {}
        self.node_to_edges: Dict[str, Set[str]] = defaultdict(set)
        self.edge_to_nodes: Dict[str, Set[str]] = defaultdict(set)
        
    async def initialize(self):
        """Initialize hypergraph processor"""
        logger.info("Initializing Financial Hypergraph Processor")
        logger.info("Financial Hypergraph Processor initialized successfully")
    
    async def add_financial_entities(self, entities: List[Dict]) -> List[str]:
        """Add financial entities as hypergraph nodes"""
        try:
            added_nodes = []
            
            for entity_data in entities:
                node_id = entity_data['entity_id']
                
                node = HyperNode(
                    node_id=node_id,
                    node_type=entity_data['entity_type'],
                    attributes=entity_data.get('attributes', {})
                )
                
                self.nodes[node_id] = node
                added_nodes.append(node_id)
            
            logger.info(f"Added {len(added_nodes)} financial entities to hypergraph")
            return added_nodes
            
        except Exception as e:
            logger.error("Adding financial entities failed", error=str(e))
            raise
    
    async def create_relationship_hyperedge(self, 
                                          relationship_type: str,
                                          entity_ids: List[str],
                                          weight: float = 1.0,
                                          metadata: Dict = None) -> str:
        """Create hyperedge representing multi-entity relationship"""
        try:
            # Validate entities exist
            for entity_id in entity_ids:
                if entity_id not in self.nodes:
                    raise ValueError(f"Entity {entity_id} not found in hypergraph")
            
            edge_id = f"edge_{relationship_type}_{datetime.utcnow().timestamp()}"
            entity_set = set(entity_ids)
            
            # Create hyperedge
            hyperedge = Hyperedge(
                edge_id=edge_id,
                nodes=entity_set,
                weight=weight,
                edge_type=relationship_type,
                metadata=metadata or {},
                created_at=datetime.utcnow()
            )
            
            self.hyperedges[edge_id] = hyperedge
            
            # Update node-edge mappings
            for node_id in entity_set:
                self.node_to_edges[node_id].add(edge_id)
                self.edge_to_nodes[edge_id].add(node_id)
                
                # Update node degree
                self.nodes[node_id].degree += 1
            
            logger.info(f"Created hyperedge {edge_id} connecting {len(entity_ids)} entities")
            return edge_id
            
        except Exception as e:
            logger.error("Hyperedge creation failed", error=str(e))
            raise
    
    async def analyze_systemic_risk(self) -> Dict:
        """Analyze systemic risk using hypergraph structure"""
        try:
            # Calculate centrality measures
            centrality_measures = await self._calculate_hypergraph_centralities()
            
            # Identify critical nodes
            critical_nodes = await self._identify_critical_nodes()
            
            # Analyze clustering
            clustering_analysis = await self._analyze_hypergraph_clustering()
            
            # Calculate connectivity metrics
            connectivity_metrics = await self._calculate_connectivity_metrics()
            
            # Simulate contagion
            contagion_simulation = await self._simulate_financial_contagion()
            
            return {
                'centrality_measures': centrality_measures,
                'critical_nodes': critical_nodes,
                'clustering_analysis': clustering_analysis,
                'connectivity_metrics': connectivity_metrics,
                'contagion_simulation': contagion_simulation,
                'systemic_risk_score': await self._calculate_systemic_risk_score(),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Systemic risk analysis failed", error=str(e))
            raise
    
    async def _calculate_hypergraph_centralities(self) -> Dict:
        """Calculate various centrality measures for hypergraph"""
        centralities = {}
        
        # Hyperdegree centrality (number of hyperedges)
        degree_centrality = {
            node_id: node.degree for node_id, node in self.nodes.items()
        }
        
        # Eigenvector-like centrality for hypergraphs
        eigenvector_centrality = await self._calculate_eigenvector_centrality()
        
        # Betweenness centrality adaptation for hypergraphs
        betweenness_centrality = await self._calculate_hypergraph_betweenness()
        
        return {
            'degree_centrality': degree_centrality,
            'eigenvector_centrality': eigenvector_centrality,
            'betweenness_centrality': betweenness_centrality
        }
    
    async def _calculate_eigenvector_centrality(self) -> Dict[str, float]:
        """Calculate eigenvector centrality for hypergraph"""
        if not self.nodes:
            return {}
        
        # Create adjacency-like matrix for hypergraph
        node_list = list(self.nodes.keys())
        n_nodes = len(node_list)
        node_index = {node: i for i, node in enumerate(node_list)}
        
        # Hypergraph adjacency matrix
        adjacency_matrix = np.zeros((n_nodes, n_nodes))
        
        for edge in self.hyperedges.values():
            edge_nodes = list(edge.nodes)
            edge_size = len(edge_nodes)
            
            # Add connections between all pairs in hyperedge
            for i, node1 in enumerate(edge_nodes):
                for j, node2 in enumerate(edge_nodes):
                    if i != j:
                        idx1 = node_index[node1]
                        idx2 = node_index[node2]
                        # Weight by edge weight and inverse of edge size
                        adjacency_matrix[idx1][idx2] += edge.weight / (edge_size - 1)
        
        # Normalize and calculate eigenvector centrality
        if np.sum(adjacency_matrix) > 0:
            # Power iteration for dominant eigenvector
            centrality_vector = np.ones(n_nodes) / n_nodes
            
            for _ in range(100):  # Max iterations
                new_vector = np.dot(adjacency_matrix, centrality_vector)
                if np.sum(new_vector) > 0:
                    new_vector = new_vector / np.sum(new_vector)
                    if np.allclose(centrality_vector, new_vector, atol=1e-6):
                        break
                    centrality_vector = new_vector
                else:
                    break
            
            return {node_list[i]: float(centrality_vector[i]) for i in range(n_nodes)}
        else:
            return {node: 0.0 for node in node_list}
    
    async def _calculate_hypergraph_betweenness(self) -> Dict[str, float]:
        """Calculate betweenness centrality adaptation for hypergraph"""
        # Simplified hypergraph betweenness
        betweenness = {}
        
        for node_id in self.nodes:
            # Count how many hyperedges this node participates in
            # and how central it is in those hyperedges
            node_edges = self.node_to_edges[node_id]
            betweenness_score = 0.0
            
            for edge_id in node_edges:
                edge = self.hyperedges[edge_id]
                edge_size = len(edge.nodes)
                # Node is more central in smaller hyperedges
                betweenness_score += edge.weight / max(edge_size - 1, 1)
            
            betweenness[node_id] = float(betweenness_score)
        
        # Normalize
        max_betweenness = max(betweenness.values()) if betweenness.values() else 1.0
        if max_betweenness > 0:
            betweenness = {k: v / max_betweenness for k, v in betweenness.items()}
        
        return betweenness
    
    async def _identify_critical_nodes(self) -> Dict:
        """Identify critical nodes in hypergraph"""
        centralities = await self._calculate_hypergraph_centralities()
        
        # Combine centrality measures
        composite_scores = {}
        for node_id in self.nodes:
            score = (
                centralities['degree_centrality'].get(node_id, 0) * 0.4 +
                centralities['eigenvector_centrality'].get(node_id, 0) * 0.4 +
                centralities['betweenness_centrality'].get(node_id, 0) * 0.2
            )
            composite_scores[node_id] = score
        
        # Identify top critical nodes
        sorted_nodes = sorted(composite_scores.items(), key=lambda x: x[1], reverse=True)
        top_critical = sorted_nodes[:min(10, len(sorted_nodes))]
        
        return {
            'top_critical_nodes': [{'node_id': node_id, 'criticality_score': score} 
                                 for node_id, score in top_critical],
            'criticality_threshold': np.percentile(list(composite_scores.values()), 90) if composite_scores else 0.0,
            'highly_critical_count': sum(1 for score in composite_scores.values() if score > 0.8)
        }
    
    async def _analyze_hypergraph_clustering(self) -> Dict:
        """Analyze clustering in hypergraph"""
        if not self.hyperedges:
            return {'clustering_coefficient': 0.0, 'clusters_detected': 0}
        
        # Calculate hypergraph clustering coefficient
        total_clustering = 0.0
        node_count = 0
        
        for node_id in self.nodes:
            node_edges = self.node_to_edges[node_id]
            if len(node_edges) < 2:
                continue
            
            # Count connections between neighbors
            neighbors = set()
            for edge_id in node_edges:
                neighbors.update(self.hyperedges[edge_id].nodes)
            neighbors.discard(node_id)
            
            if len(neighbors) < 2:
                continue
            
            # Count edges between neighbors
            neighbor_connections = 0
            for edge_id in self.hyperedges:
                edge_nodes = self.hyperedges[edge_id].nodes
                if len(edge_nodes & neighbors) >= 2:
                    neighbor_connections += 1
            
            # Calculate local clustering
            max_possible = len(neighbors) * (len(neighbors) - 1) / 2
            local_clustering = neighbor_connections / max_possible if max_possible > 0 else 0.0
            
            total_clustering += local_clustering
            node_count += 1
        
        avg_clustering = total_clustering / node_count if node_count > 0 else 0.0
        
        return {
            'clustering_coefficient': float(avg_clustering),
            'clusters_detected': await self._detect_community_clusters(),
            'modularity_score': await self._calculate_modularity()
        }
    
    async def _detect_community_clusters(self) -> int:
        """Detect community clusters in hypergraph"""
        # Simplified community detection
        # In practice, would use sophisticated algorithms like Louvain method adapted for hypergraphs
        
        if len(self.nodes) < 3:
            return len(self.nodes)
        
        # Estimate number of clusters based on hypergraph structure
        avg_degree = np.mean([node.degree for node in self.nodes.values()])
        estimated_clusters = max(1, int(len(self.nodes) / max(avg_degree, 1)))
        
        return min(estimated_clusters, len(self.nodes))
    
    async def _calculate_modularity(self) -> float:
        """Calculate modularity score for hypergraph"""
        # Simplified modularity calculation
        if not self.hyperedges or not self.nodes:
            return 0.0
        
        # Mock modularity calculation
        total_edges = len(self.hyperedges)
        avg_edge_size = np.mean([len(edge.nodes) for edge in self.hyperedges.values()])
        
        # Higher modularity for smaller, more cohesive communities
        modularity = min(1.0, avg_edge_size / len(self.nodes))
        return float(modularity)
    
    async def _calculate_connectivity_metrics(self) -> Dict:
        """Calculate various connectivity metrics"""
        return {
            'total_nodes': len(self.nodes),
            'total_hyperedges': len(self.hyperedges),
            'average_hyperedge_size': float(np.mean([len(edge.nodes) for edge in self.hyperedges.values()])) if self.hyperedges else 0.0,
            'average_node_degree': float(np.mean([node.degree for node in self.nodes.values()])) if self.nodes else 0.0,
            'hypergraph_density': await self._calculate_hypergraph_density(),
            'connected_components': await self._count_connected_components()
        }
    
    async def _calculate_hypergraph_density(self) -> float:
        """Calculate hypergraph density"""
        if len(self.nodes) < 2:
            return 0.0
        
        # Actual hyperedges vs maximum possible
        max_possible_edges = 2 ** len(self.nodes) - len(self.nodes) - 1  # All possible non-empty, non-singleton subsets
        actual_edges = len(self.hyperedges)
        
        density = actual_edges / max_possible_edges if max_possible_edges > 0 else 0.0
        return float(min(density, 1.0))
    
    async def _count_connected_components(self) -> int:
        """Count connected components in hypergraph"""
        if not self.nodes:
            return 0
        
        visited = set()
        components = 0
        
        for node_id in self.nodes:
            if node_id not in visited:
                # BFS to find connected component
                queue = [node_id]
                visited.add(node_id)
                
                while queue:
                    current_node = queue.pop(0)
                    # Find all nodes connected through hyperedges
                    for edge_id in self.node_to_edges[current_node]:
                        for connected_node in self.hyperedges[edge_id].nodes:
                            if connected_node not in visited:
                                visited.add(connected_node)
                                queue.append(connected_node)
                
                components += 1
        
        return components
    
    async def _simulate_financial_contagion(self) -> Dict:
        """Simulate financial contagion through hypergraph"""
        if not self.nodes:
            return {'contagion_paths': [], 'max_cascade_size': 0}
        
        # Start contagion from most critical nodes
        critical_nodes = await self._identify_critical_nodes()
        
        contagion_results = []
        
        for critical_node_info in critical_nodes['top_critical_nodes'][:3]:  # Top 3 critical nodes
            seed_node = critical_node_info['node_id']
            cascade_size = await self._simulate_cascade_from_node(seed_node)
            
            contagion_results.append({
                'seed_node': seed_node,
                'cascade_size': cascade_size,
                'cascade_percentage': cascade_size / len(self.nodes) * 100
            })
        
        max_cascade_size = max([r['cascade_size'] for r in contagion_results]) if contagion_results else 0
        
        return {
            'contagion_simulations': contagion_results,
            'max_cascade_size': max_cascade_size,
            'max_cascade_percentage': max_cascade_size / len(self.nodes) * 100 if self.nodes else 0,
            'contagion_vulnerability': 'high' if max_cascade_size > len(self.nodes) * 0.3 else 'medium' if max_cascade_size > len(self.nodes) * 0.1 else 'low'
        }
    
    async def _simulate_cascade_from_node(self, seed_node: str) -> int:
        """Simulate cascade starting from specific node"""
        infected = {seed_node}
        queue = [seed_node]
        
        infection_threshold = 0.5  # Threshold for infection spread
        
        while queue:
            current_node = queue.pop(0)
            
            # Find neighbors through hyperedges
            for edge_id in self.node_to_edges[current_node]:
                edge = self.hyperedges[edge_id]
                
                for neighbor in edge.nodes:
                    if neighbor not in infected:
                        # Infection probability based on edge weight and size
                        infection_prob = edge.weight / len(edge.nodes)
                        
                        if infection_prob > infection_threshold:
                            infected.add(neighbor)
                            queue.append(neighbor)
        
        return len(infected)
    
    async def _calculate_systemic_risk_score(self) -> float:
        """Calculate overall systemic risk score"""
        if not self.nodes:
            return 0.0
        
        # Factors contributing to systemic risk
        connectivity_metrics = await self._calculate_connectivity_metrics()
        clustering_analysis = await self._analyze_hypergraph_clustering()
        
        # Risk factors
        density_risk = min(connectivity_metrics['hypergraph_density'] * 2, 1.0)  # Higher density = higher risk
        concentration_risk = 1.0 - clustering_analysis['clustering_coefficient']  # Lower clustering = higher concentration risk
        size_risk = min(len(self.nodes) / 1000, 1.0)  # Larger networks have higher systemic risk potential
        
        # Composite systemic risk score
        systemic_risk = (
            density_risk * 0.4 +
            concentration_risk * 0.4 +
            size_risk * 0.2
        )
        
        return float(min(systemic_risk, 1.0))
