from afd import * 

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
