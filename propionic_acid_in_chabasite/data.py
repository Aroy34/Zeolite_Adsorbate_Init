import re
import matplotlib.pyplot as plt
import os

def parse_data(filename):
    with open(filename, 'r') as file:
        data = file.read()

    # Find all occurrences of energy values
    energy_pattern = re.compile(r'Current total potential energy:\s+(-?\d+\.\d+)\s+\[K\]')
    energies = [float(match) for match in energy_pattern.findall(data)]
    
    # Find all occurrences of cycle numbers
    cycle_pattern = re.compile(r'Current cycle: (\d+) out of \d+')
    cycles = [int(match) for match in cycle_pattern.findall(data)]

    return cycles, energies

def plot_energy(cycles, energies):
    # Convert energies from K to eV
    # K_to_eV = 8.617333262145e-5
    energies = [e for e in energies]
    
    # Ignore the first 10 cycles
    if len(cycles) > 10:
        cycles = cycles[10:]
        energies = energies[10:]

    # Ensure cycles and energies have the same length
    min_length = min(len(cycles), len(energies))
    cycles = cycles[:min_length]
    energies = energies[:min_length]

    plt.figure(figsize=(10, 6))
    plt.plot(cycles, energies, marker='o', linestyle='-', color='b')
    plt.xlabel('Cycle')
    plt.ylabel('Total Potential Energy [K]')
    plt.title('Fluctuation of Adsorption Energy')

    # Label the lowest energy point
    min_energy = min(energies)
    min_cycle = cycles[energies.index(min_energy)]
    # plt.annotate(f'Lowest Energy: {min_energy:.2f} eV',
    #              xy=(min_cycle, min_energy), 
    #              xytext=(min_cycle + 50, min_energy + 0.1),
    #              arrowprops=dict(facecolor='black', arrowstyle='->'))
    
    plt.grid(True)
    plt.savefig('plot.pdf')
    # plt.show()

if __name__ == '__main__':
    # Set the path to the file in the Output/System_0 directory
    directory = 'Output/System_0'
    filename = os.path.join(directory, 'output_al-cha_2.3.2_350.000000_0.data')
    
    cycles, energies = parse_data(filename)

    # Debugging output
    print(f"Number of cycles: {len(cycles)}")
    print(f"Number of energies: {len(energies)}")

    plot_energy(cycles, energies)
