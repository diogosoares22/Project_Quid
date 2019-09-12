import cirq
import random
import math

systemstate = None

measuredstates = []

def generate_reals():
    reals = []
    total = 0
    for i in range(n - 1):
        appended = random.uniform(-2**(k + 1) + 1, 2**(k + 1) - 1)
        reals.append(appended)
        total += appended
    total %= 1
    reals.append(1 - total + random.randint(-2**(k + 1) + 1, 2**(k + 1) - 2))
    return reals
    
def prepare_entangled():
    global systemstate
    circuit = cirq.Circuit()

    for i in range(n - 1):
        for j in range(k):
            circuit.append(cirq.H(cirq.GridQubit(2 * k * i + k + j, 0)))
            circuit.append(cirq.CNOT(cirq.GridQubit(2 * k * i + k + j, 0), cirq.GridQubit(2 * k * i + 2 * k + j, 0)))

    res = cirq.Simulator().simulate(circuit, qubit_order = qubs)
    systemstate = res.final_state

def addnum(player, real):
    global systemstate
    circuit = cirq.Circuit()
    for i in range(k):
        circuit.append(cirq.Y(cirq.GridQubit(2 * k * player + i, 0))**(real / 2**(i)))
    res = cirq.Simulator().simulate(circuit, qubit_order = qubs, initial_state=systemstate)
    systemstate = res.final_state

def sendfrom(player):
    global systemstate
    global measuredstates
    circuit = cirq.Circuit()
    for i in range(k):
        circuit.append(cirq.CNOT(cirq.GridQubit(2 * k * player + k + i, 0), cirq.GridQubit(2 * k * player + i, 0)))
        circuit.append(cirq.H(cirq.GridQubit(2 * k * player + k + i, 0)))
        circuit.append(cirq.measure(cirq.GridQubit(2 * k * player + i, 0), key = '{}-{}-0'.format(player, i)))
        circuit.append(cirq.measure(cirq.GridQubit(2 * k * player + k + i, 0), key = '{}-{}-1'.format(player, i)))
    res = cirq.Simulator().simulate(circuit, qubit_order = qubs, initial_state=systemstate)
    systemstate=res.final_state
    
    doz = []
    dox = []
    for i in range(k):
        doz.append(res.measurements['{}-{}-1'.format(player, i)][0])
        dox.append(res.measurements['{}-{}-0'.format(player, i)][0])
    for i in range(k):
        measuredstates.append(dox[i])
    for i in range(k):
        measuredstates.append(doz[i])
    
    if showcommunication:
        print("P{} -> P{}".format(player, player + 1))
        for i in range(k):
            print("({}, {})".format(int(dox[i]), int(doz[i])), end = '')
        print('\n')

    circuit2 = cirq.Circuit()
    for i in range(k):
        if doz[i]:
            circuit2.append(cirq.Z(cirq.GridQubit(2 * k * player + 2 * k + i, 0)))
        if dox[i]:
            circuit2.append(cirq.X(cirq.GridQubit(2 * k * player + 2 * k + i, 0)))
    nres = cirq.Simulator().simulate(circuit2, qubit_order = qubs, initial_state=systemstate)
    systemstate=nres.final_state

def printcursumqubits(i):
    # factor = math.sqrt(2**(n - 1 - i))
    zeroind = 0
    for j in range(2 * k * i):
        if measuredstates[j]:
            zeroind += 2 ** (2 * k * n - k - 1 - j)

    for l in range(k):
        oneind = zeroind + 2 ** (2 * k * n - k - 1 - 2 * k * i - l)
        # print("zeroind = {}, oneind = {}".format(zeroind, oneind))
        zeronorm = 0 # zerocoef.real ** 2 + zerocoef.imag ** 2
        onenorm = 0 # onecoef.real ** 2 + onecoef.imag ** 2
        # zerocoefsum = 0
        # onecoefsum = 0
        for a in range(2**l):
            for b in range(2**(k - 1 - l)):
                shift = 2 ** (2 * k * n - k - 2 * k * i - l) * a + 2 ** (2 * k * n - k - 2 * k * i - k) * b
                # print("shift {}".format(shift))
                zerocoef = systemstate[zeroind + shift]
                onecoef = systemstate[oneind + shift]
                # print("zero at {} = {}, one at {} = {}".format(zeroind + shift, "{0:b}".format(zeroind + shift), oneind + shift, "{0:b}".format(oneind + shift)))
                zeronorm += zerocoef.real ** 2 + zerocoef.imag ** 2
                onenorm += onecoef.real ** 2 + onecoef.imag ** 2
                # zerocoefsum += zerocoef
                # onecoefsum += onecoef
                # print("adding {} and {}".format(zerocoef, onecoef))
        # zeronorm = zerocoefsum.real ** 2 + zerocoefsum.imag ** 2
        # onenorm = onecoefsum.real ** 2 + onecoefsum.imag ** 2
        norm = zeronorm + onenorm
        # print(norm)
        normrt = math.sqrt(norm)

        print("2^{} sum 0: {}".format(l, zeronorm / norm))
        print("2^{} sum 1: {}".format(l, onenorm / norm))

n = 3
k = 4
showstate = True
showcommunication = True
qubs = [cirq.GridQubit(i, 0) for i in range(2 * k * n - k)]
modulo = 2**k

if __name__ == "__main__":
    if k == 1:
        print("The game for {} players.".format(n))
    else:
        print("The game for {} players telling mod {}.".format(n, modulo))
    reals = generate_reals()
    print("The players will get {}.".format(reals))
    sumreals = int(sum(reals))
    if k == 1:
        print("The sum is {}.".format(sumreals))
    else:
        print("The sum is {} ({} mod {}).".format(sumreals, sumreals % modulo, modulo))
    print("Starting the game...\n")

    prepare_entangled()
    print("Prepared entangled state.")
    if showstate:
        printcursumqubits(0)
    print()
    
    for i in range(n - 1):
        addnum(i, reals[i])
        print("Added {} by player {}.".format(reals[i], i))
        if showstate:
            printcursumqubits(i)
        print()
        sendfrom(i)
        print("Qubit{} teleported to player {}.\n".format("" if k == 1 else "s", i + 1))

    addnum(n - 1, reals[n - 1])
    print("Added {} by player {}.".format(reals[n - 1], n - 1))
    if showstate:
        printcursumqubits(n - 1)
    print()

    mescircuit = cirq.Circuit()
    for i in range(k):
        controlqubit = cirq.GridQubit(2 * k * n - 2 * k + i, 0)
        for j in range(i + 1, k):
            targetqubit = cirq.GridQubit(2 * k * n - 2 * k + j, 0)
            mescircuit.append((cirq.Y(targetqubit)**(-2**(i - j))).controlled_by(controlqubit))
    mescircuit.append(cirq.measure(*[cirq.GridQubit(2 * k * n - 2 * k + i, 0) for i in range(k)], key = 'f'))
    res = cirq.Simulator().simulate(mescircuit, qubit_order=qubs, initial_state=systemstate)
    if k == 1:
        odd = res.measurements['f'][0]
        if odd:
            print("Measured 1. The sum is ODD.")
        else:
            print("Measured 0. The sum is EVEN.")
    else:
        result = 0
        binar = ""
        for i in range(k):
            binar += "1" if res.measurements['f'][k - 1 - i] else "0"
            if res.measurements['f'][i]:
                result += 2**i
        print("Measured {}. The sum is {} mod {}.".format(binar, result, modulo))
        print(binar)