import sys
import os
from ase.io import *
from ase import Atoms

# asdasdasd
# Logical comment
# Get input CIF file and No. of frames to save
mofcif = sys.argv[1]
ncifs = int(sys.argv[2])

# RASPA output copy
cmd = 'cp Movies/System_0/Movie_*_allcomponents.pdb ./frames.pdb'
os.system(cmd)

with open('frames.pdb', 'r') as f:
    d = f.readlines()
nframes = 0
frame_start_idx = []
frame_end_idx = []

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
m = read(mofcif)

# Loop over the last ncifs frames and combine them with the MOF
for i in range(nframes - ncifs, nframes):
    dd = d[frame_start_idx[i]:frame_end_idx[i]]
    cryst, atoms, symbols = readpdbpart(dd)
    
    # Create an Atoms object from the extracted PDB data
    a = Atoms(symbols, positions=atoms)
    a.set_pbc((True, True, True))
    a.set_cell(cryst)
    
    # Combine the zeolite structure with the current frame
    ma = m + a
    
    # Write the combined structure to CIF and POSCAR formats
    ma.write('combined_%d.cif' % (i+1))
    ma.write('combined_%d.POSCAR' % (i+1), format='vasp')

print(f"Combined CIF and POSCAR files saved for the last {ncifs} frames.")
