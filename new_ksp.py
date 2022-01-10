
import networkx as nx
import matplotlib.pyplot as plt
import queue
import csv
import math

from copy import deepcopy


# pos = nx.spring_layout(G_network)
# nx.draw_networkx_nodes(G_network,pos,node_size=700)
# nx.draw_networkx_edges(G_network,pos,width=6)

# nx.draw(G_network,with_labels=True)
# plt.show()

# 计算所选路径路径的weight
def pweight(G,p):
    w = 0
    for i in range(len(p)-1):
        #k = G[p[i]][p[i+1]]
        #print(G[p[i]][p[i+1]]['weight'])
        w += G[p[i]][p[i+1]]['weight']
    return w

# Copy edge (a,z) of G, remove it, and return the copy.
def cprm(G,a,z):
    ec = deepcopy(G[a][z])
    G.remove_edge(a,z)
    return (a,z,ec)

# Copy node n of G, remove it, and return the copy.
def cprmnode(G,n):
    ec = deepcopy(G[n])
    G.remove_node(n)
    return (n,ec)

# K shortest paths in G from 'source' to 'target'
def yen(G,source,target,K):
    # c is the distance(cost) from source, p is the path from the source to that node.
    c,p = nx.single_source_dijkstra(G,source,target)
    A = []
    A.append(p)
    A_cost = []
    A_cost.append(c)
    B = queue.PriorityQueue()

    # iteration K-1
    for k in range(1,K):
        # Spur node ranges over the (k-1)-shortest path minus its last node:
        for i in range(len(A[k-1])-1):
            # Spur node
            sn = A[k-1][i]
            # Root path: from the source to the spur node of the (k-1)-shortest path
            rp = A[k-1][:i]

            removed_edges = []
            removed_root_edges = []
            removed_root_nodes = []

            for j in range(len(rp)-1):

                extra_edges = []
                for e in G.edges():
                    for ee in rp[j]:
                        if e[0] == ee or e[1] == ee:
                            extra_edges.append(e)
                #extra_edges = deepcopy(G.edges(rp[j]))

                for eg in extra_edges:
                    src = eg[0]
                    tgt = eg[1]
                    removed_root_edges.append(cprm(G,src,tgt))
                removed_root_nodes.append(cprmnode(G,rp[j]))

            if len(rp) > 0 and sn != target:
                extra_edges = []
                for e in G.edges():
                    for ee in rp[len(rp)-1]:
                        if e[0] == ee or e[1] == ee:
                            extra_edges.append(e)
                #extra_edges = deepcopy(G.edges(rp[len(rp)-1]))

                for eg in extra_edges:
                    src = eg[0]
                    tgt = eg[1]
                    removed_root_edges.append(cprm(G,src,tgt))
                removed_root_nodes.append(cprmnode(G,rp[len(rp)-1]))

            erp = A[k-1][:i+1]
            for p in A:
                if erp == p[:i+1] and G.has_edge(p[i],p[i+1]):
                    removed_edges.append(cprm(G,p[i],p[i+1]))

            DONE = 0
            try:
                (csp,sp) = nx.single_source_dijkstra(G,sn,target)
            except:
                sp = []
                csp = None
                DONE = 1
            if len(sp) > 0:
                pk = rp + sp
                for nd in removed_root_nodes:
                    # G.add_node(*nd)
                    G.add_node(nd[0])
                for re in removed_root_edges:
                    G.add_edge(re[0], re[1], weight=re[2]['weight'])
                    #G.add_edge(*re)
                cpk = pweight(G,pk)
                B.put((cpk,pk))
            elif len(sp) == 0:
                for nd in removed_root_nodes:
                    # G.add_node(*nd)
                    G.add_node(nd[0])
                for re in removed_root_edges:
                    G.add_edge(re[0], re[1], weight=re[2]['weight'])
                    #G.add_edge(*re)
            for nd in removed_root_nodes:
                # G.add_node(*nd)
                G.add_node(nd[0])
            for re in removed_edges:
                #print(re[2]['weight'])
                G.add_edge(re[0],re[1],weight=re[2]['weight'])
                #G.add_edge(*re)

            #print("k:%d i:%f" %(k,i))
        if B.empty():
            print("There are only %d shortest paths for this pair" %(k))
            break
        while not B.empty():
            cost,path = B.get()
            if path not in A:
                A.append(path)
                A_cost.append(cost)
                break

    return (A,A_cost)


nodes_file = csv.reader(open('newnodes.csv','r'))
links_file = csv.reader(open('newlinks.csv','r'))

## 初始化图
G_network = nx.DiGraph()

## 添加点
tmp = 0
for row in nodes_file:
    if (tmp > 0):
        G_network.add_node(row[0])
    tmp += 1


## 添加边
tmp = 0
for row in links_file:
    if (tmp > 0):
        G_network.add_edge(row[0],row[1])
        G_network[row[0]][row[1]]['weight'] = float(row[2])
    tmp += 1


src = 'C'
tgt = 'H'
k = 10

k_path, path_costs = yen(G_network, src, tgt, k)

k_shortest_paths_file = open('%d_SPs_btw_%s_%s.csv' % (k, src, tgt), 'w')
k_shortest_paths_file.write('Source,Target,kth-path,Distance,,,SHORTEST PATH,,,,,\n')
k_shortest_paths_file.write('%s,%s,\n' % (src, tgt))

for i in enumerate(k_path):
    if (i[0] == 0):
        #print(type(i),i[0],i[1])
        k_shortest_paths_file.write('%d,%f,,,' % (i[0] + 1, path_costs[i[0]]))
    else:
        #print(type(i), i[0], i[1])
        k_shortest_paths_file.write('%d,%f,,,' % (i[0] + 1, path_costs[i[0]]))
    for j in range(len(i[1])):
        k_shortest_paths_file.write('%s,' % (i[1][j]))

    k_shortest_paths_file.write('\n')