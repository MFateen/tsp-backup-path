#!/usr/bin/python
# ####################################################
# Generator of a RIP graph with backup path structures
# ####################################################

# IMPORTANT, DOES NOT DETECT LOOPS

import second_best_cost_backup_path as sbp
import worst_cost_backup_path as wbp
import rip_graph_generator as rip_gen
import networkx as nx
import random
import math
import sys

def reduce_edges(graph, percentage):
    number_of_edges_to_delete = int(math.ceil(graph.number_of_edges()*1.0*percentage/100))
    edges_to_delete = random.sample(graph.edges(), number_of_edges_to_delete)
    graph.remove_edges_from(edges_to_delete)
    # Being awesome
    #edges_to_delete.extend([(y,x) for (x,y) in edges_to_delete])
    return edges_to_delete


def detect_affected_paths(primary_paths, deleted_edges):    
    s1 = set(deleted_edges)
    src_dest = []
    for path in primary_paths:
        chunk = [(path[i],path[i+1]) for i in range(0, len(path)-1)]  # Awesome chunking
        s2 = set(chunk)
        interception = s1&s2
        if len(interception) != 0:
            #print "Detected affected path: %s" % path
            src_dest.append((path[0],path[-1]))
            
    return src_dest
            
            
def check_backup_strategy(original_graph, reduced_graph, source, destination):
    current_node = source
    previous_node = None
    TTL = original_graph.number_of_nodes()
    while (current_node != destination and TTL >= 0):
        nhv = original_graph.node[current_node]['default_next_hop']
        next_hop = nhv[destination]
        #print "I am in node %d and to go to %d I should use %d" % (current_node,destination,next_hop)
        if (next_hop != previous_node and reduced_graph.has_edge(current_node, next_hop)):
            current_node = next_hop
            previous_node = current_node
            TTL = TTL-1
        else:
            bhv = original_graph.node[current_node]['backup_next_hop']            
            next_hop = bhv[destination]
            if (next_hop != None and reduced_graph.has_edge(current_node, next_hop)):
                if (next_hop == previous_node):
                    global fail_count
                    fail_count += 1
                    return
                current_node = next_hop
                previous_node = current_node
                TTL = TTL-1
            else:
                global fail_count
                fail_count += 1
                return
    
    if TTL < 0:
        global fail_count
        fail_count += 1
        
        
def single_experiment(size):
    network_graph = rip_gen.generate_rip_graph(size)
    print "A graph with %d nodes and %d edges was generated." % (network_graph.number_of_nodes(), network_graph.number_of_edges())
    primary_paths = []
    for k,v in nx.shortest_path(network_graph).iteritems():
        for n,m in v.iteritems():
            if len(m) > 1:
                primary_paths.append(m)
    #print primary_paths

    #rip_gen.draw_graph(network_graph)
    
    for tp in [10, 30, 50, 70]:
        print "\n%d of topology change" % tp
        print "====================="
        reduced_graph = network_graph.subgraph(network_graph.nodes())
        deleted_edges = reduce_edges(reduced_graph, tp)
        print "%d edges deleted" % len(deleted_edges)
        #print deleted_edges
        ap = detect_affected_paths(primary_paths, deleted_edges)
        #print ap
        print "Affection rate: %d/%d = %.2f%%" % (len(ap), len(primary_paths), len(ap)*100.0/len(primary_paths))
        string = "Fail rate: %d/%d = %.2f%%\" % (fail_count, len(ap), fail_count*100.0/len(ap))"
        
        sbp.second_best_cost_backup_path(network_graph) 
        
        global fail_count    
        fail_count = 0
        for (s,d) in ap:
            check_backup_strategy(network_graph, reduced_graph, s, d)
        
        print "\nUsing SECOND BEST COST backup strategy...   Fail rate: %d/%d = %.2f%%" % (fail_count, len(ap), fail_count*100.0/len(ap))                
        
        wbp.worst_cost_backup_path(network_graph)
        
        global fail_count    
        fail_count = 0
        for (s,d) in ap:
            check_backup_strategy(network_graph, reduced_graph, s, d)

        print "Using WORST BEST COST backup strategy...   Fail rate: %d/%d = %.2f%%" % (fail_count, len(ap), fail_count*100.0/len(ap))
    
        #print "First graph: %s " % network_graph
        #rip_gen.draw_graph(network_graph)
        #print "Second graph: %s " % reduced_graph
        #rip_gen.draw_graph(reduced_graph)


if __name__ == '__main__':

    print "\n******** STARTING SMALL EXPERIMENT ********"
    single_experiment(10)        
    
    print "\n\n******** STARTING MEDIUM EXPERIMENT ********"
    single_experiment(50)
    
    print "\n\n******** STARTING BIG EXPERIMENT ********"
    single_experiment(100)
    
    #for n, nattr in network_graph.nodes(data=True):  # For each node n and attribute nattr
        #print n
        #print nattr['distance_matrix']
        #print nattr['best_weights_vector']
        #print nattr['default_next_hop']
        #print nattr['backup_next_hop']

        #print "\n"
    #print nx.shortest_path(network_graph)
    #rip_gen.draw_graph(network_graph)