import sys
import os
from ase.io import read
from ase import Atoms

# Get input CIF file and number of frames to save
mofcif = sys.argv[1]
ncifs = int(sys.argv[2])

# Copy the PDB frames file from RASPA output
cmd = 'cp Movies/System_0/Movie_*_allcomponents.pdb ./frames.pdb'
os.system(cmd)

# Read the frames.pdb file
with open('frames.pdb', 'r') as f:
    d = f.readlines()

# Initialize frame counters
nframes = 0
frame_start_idx = []
frame_end_idx = []

# Identify the start and end of each frame in the PDB file
for i, l in enumerate(d):
    ll = l.strip().split()
    if 'MODEL' in ll[0]:
        nframes += 1
        frame_start_idx.append(i)
    elif 'ENDMDL' in ll[0]:
        frame_end_idx.append(i)

# Function to extract cell parameters and atomic positions from a PDB frame
def readpdbpart(dd):
    cryst = []
    atoms = []
    symbols = ''
    for l in dd:
        ll = l.strip().split()
        if ll[0] == 'CRYST1':
            for i in range(6):
                cryst.append(float(ll[i+1]))
        elif ll[0] == 'ATOM':
            atoms.append([float(ll[4]), float(ll[5]), float(ll[6])])
            symbols += ll[2]
    return cryst, atoms, symbols

# Read the MOF CIF file
mof = read(mofcif)

# Extract MOF cell parameters and atom counts
mof_cell = mof.get_cell()
mof_symbols = mof.get_chemical_symbols()
unique_symbols = sorted(set(mof_symbols), key=mof_symbols.index)  # Preserve order of appearance
atom_counts = [mof_symbols.count(sym) for sym in unique_symbols]

# Open XDATCAR file for writing
with open('XDATCAR', 'w') as xdatcar:
    # Write the system information (header)
    xdatcar.write('unknown system\n')
    xdatcar.write('   1.0\n')
    for vec in mof_cell:
        xdatcar.write(f'    {vec[0]:12.6f} {vec[1]:12.6f} {vec[2]:12.6f}\n')

    # Write atom types and counts for the MOF
    xdatcar.write('   ' + '   '.join(unique_symbols) + '\n')
    xdatcar.write('   ' + '   '.join(map(str, atom_counts)) + '\n')

    # Loop over the last ncifs frames and combine them with the MOF
    for i in range(nframes - ncifs, nframes):
        dd = d[frame_start_idx[i]:frame_end_idx[i]]
        cryst, atoms, symbols = readpdbpart(dd)
        
        # Create an Atoms object from the extracted PDB data
        adsorbate = Atoms(symbols, positions=atoms)
        adsorbate.set_pbc((True, True, True))
        adsorbate.set_cell(cryst)
        
        # Combine the MOF structure with the current frame
        combined_atoms = mof + adsorbate
        
        # Update the unique symbols and atom counts with adsorbate data
        combined_symbols = combined_atoms.get_chemical_symbols()
        unique_combined_symbols = sorted(set(combined_symbols), key=combined_symbols.index)  # Preserve order of appearance
        combined_counts = [combined_symbols.count(sym) for sym in unique_combined_symbols]
        
        # Write the combined structure's atomic positions to XDATCAR in direct format
        xdatcar.write(f'Direct configuration=     {i+1}\n')
        for atom_pos in combined_atoms.get_scaled_positions():
            xdatcar.write(f'   {atom_pos[0]:12.8f} {atom_pos[1]:12.8f} {atom_pos[2]:12.8f}\n')
            

    # Update atom types and counts for the combined system
    xdatcar.write('   ' + '   '.join(unique_combined_symbols) + '\n')
    xdatcar.write('   ' + '   '.join(map(str, combined_counts)) + '\n')

print(f"XDATCAR file generated with {ncifs} configurations.")
