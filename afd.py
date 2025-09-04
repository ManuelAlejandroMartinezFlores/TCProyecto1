from afn import *
from afn import _epsilon_closure


def gen_label(states):
    labels = [state.label for state in states]
    labels.sort()
    return '='.join(labels) 

class AFDState:
    def __init__(self, afn_states, accept_state):
        self.afn_states = _epsilon_closure(afn_states) 
        self.label = gen_label(self.afn_states)
        self.transitions = {}
        self.new = True
        self.accept = accept_state in self.afn_states if accept_state else False

    def _get_transitions(self, existing, accept_state):
        for state in self.afn_states:
            for char in state.transitions:
                if char in self.transitions:
                    self.transitions[char].update(_epsilon_closure(state.transitions[char]))
                else:
                    self.transitions[char] = _epsilon_closure(state.transitions[char])

        for char in self.transitions:
            label = gen_label(_epsilon_closure(self.transitions[char]))
            if label in existing:
                self.transitions[char] = existing[label]
            else:
                state = AFDState(self.transitions[char], accept_state)
                existing[label] = state 
                self.transitions[char] = state
                
        self.new = False 
        for char in self.transitions:
            if self.transitions[char].new:
                existing = self.transitions[char]._get_transitions(existing, accept_state)

        return existing 

    def __repr__(self):
        return f'{self.afn_states}'
    
class AFD:
    def __init__(self, afn):
        self.start = AFDState(_epsilon_closure({afn.start}), afn.accept)
        self.nodes = self.start._get_transitions({self.start.label: self.start}, afn.accept)
        self.min = False

    def simulate(self, text):
        current = self.start 
        for char in text:
            if char not in current.transitions:
                return False 
            current = current.transitions[char]
        return current.accept
    
    def minimizing(self):
        table = {}
        alphabet = set()
        for labelp, p in self.nodes.items():
            table[labelp] = {}
            alphabet.update(p.transitions.keys())
            for labelq, q in self.nodes.items():
                if labelq <= labelp:
                    continue
                table[labelp][labelq] = (p.accept != q.accept)

        new_added = True 
        while new_added:
            new_added = False
            for labelp in table:
                for labelq in table[labelp]:
                    if table[labelp][labelq]:
                        continue
                    for char in alphabet:
                        ptransition = char in self.nodes[labelp].transitions
                        qtransition = char in self.nodes[labelq].transitions
                        if ptransition != qtransition:
                            new_added = True 
                            table[labelp][labelq] = True
                            break
                        if ptransition:
                            labelpp = self.nodes[labelp].transitions[char].label
                            labelqp = self.nodes[labelq].transitions[char].label
                            min_label = min(labelpp, labelqp)
                            max_label = max(labelpp, labelqp)
                            if labelpp == labelqp:
                                continue
                            if table[min_label][max_label]:
                                new_added = True
                                table[labelp][labelq] = True 
                                break 
                            
        parent = {label: label for label in self.nodes}
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        for labelp in table:
            for labelq, dist in table[labelp].items():
                if not dist:
                    rootp = find(labelp)
                    rootq = find(labelq)
                    if rootp != rootq:
                        parent[rootq] = rootp

        representative = {label: find(label) for label in self.nodes}

        new_nodes = {}
        for repr in set(representative.values()):
            node = AFDState({}, None)
            node.label = repr 
            new_nodes[repr] = node
            
        for label, repr in representative.items():
            node = self.nodes[label]
            representant = new_nodes[repr]
            representant.accept = (node.accept or representant.accept)
            for char, state in node.transitions.items():
                representant.transitions[char] = new_nodes[representative[state.label]] 

        self.start = new_nodes[representative[self.start.label]]
        self.nodes = new_nodes
        self.min = True
                
    
    def to_graph(self):
        G = nx.MultiDiGraph()
        stack = [self.start]
        visited = set()

        while stack:
            current = stack.pop()
            G.add_node(current.label, label='', terminal=current.accept)
            
            for char, state in current.transitions.items():
                G.add_edge(current.label, state.label, label=char)
                if state.label not in visited:
                    if state.label != current.label:
                        stack.append(state)
                    visited.add(state.label)
        return G
    
    def plot(self):
        G = self.to_graph()
        pos = nx.spring_layout(G)
        
        node_colors = []
        for node in G.nodes():
            if G.nodes[node]['terminal'] and node == self.start.label:
                node_colors.append('yellow')  # Terminal
            elif G.nodes[node]['terminal']:
                node_colors.append('lightcoral')  # Terminal
            elif node == self.start.label:
                node_colors.append('lightgreen')  # Inicio
            else:
                node_colors.append('skyblue')  # Estado
        
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=300)
        
        
        nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=20, connectionstyle='arc3,rad=0.2')
        label_pos = [0.3, 0.15, 0.25, 0.1, 0.2] 
        edge_labels = {(u, v, k): d['label'] for u, v, k, d in G.edges(keys=True, data=True)}
        for i, ((u, v, k), label) in enumerate(edge_labels.items()):
            nx.draw_networkx_edge_labels(G, pos, {(u, v, k): label}, 
                                label_pos=label_pos[i % len(label_pos)])

        
        plt.axis('off')
        plt.title("Visualización AFD")
        plt.show()





if __name__ == "__main__":
    filename = input("Nombre del archivo: ")
    try:
        with open(filename, 'r') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if line:  
                    try:
                        validate_regex(line)
                        postfix = shunting_yard(line)
                        print(f"Original: {line}")
                        print(f"Postfix: {postfix}")
                        nfa = regex_to_nfa(postfix)
                        nfa.plot()
                        afd = AFD(nfa)
                        afd.plot()
                        afd.minimizing()
                        afd.plot()
                        while True:
                            try:
                                ex = input("Expresión: ")
                                print(f'AFN: {nfa.simulate(ex)}')
                                print(f'AFD: {afd.simulate(ex)}')
                            except KeyboardInterrupt as e:
                                break
                    except ValueError as e:
                        print(f"Expresión regular inválida: {e}")
                    print('\n'+"="*50)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")





