import numpy as np
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.molecule_structure_comparator import CovalentRadius
from chemview import MolecularViewer
from chemview.utils import get_atom_color


def quick_view(structure, bonds=True, conventional=True, transform=[1, 1, 1], show_box=True, bond_tol=0.2):
    """
    :param structure: (pymatgen Structure)
    :param bonds: (bool) visualize bonds
    :param conventional: (bool) use conventional cell
    :param transform: (list) can be used to make supercells with (see pymatgen.Structure.make_supercell method)
    :param show_box: (true) unit cell is shown
    :param bond_tol: (float) used if bonds=True. Sets an extra distance tolerance when finding bonds.
    :return:
        A chemview MolecularViewer widget
    """

    if conventional:
        structure = SpacegroupAnalyzer(structure).get_conventional_standard_structure()
    structure.make_supercell(transform)
    atom_types = [i.symbol for i in structure.species]

    if bonds:
        bonds = []
        for i in range(structure.num_sites - 1):
            sym_i = structure[i].specie.symbol
            for j in range(i + 1, structure.num_sites):
                sym_j = structure[j].specie.symbol
                max_d = CovalentRadius.radius[sym_i] + CovalentRadius.radius[sym_j] + bond_tol
                if structure.get_distance(i, j, 0) < max_d:
                    bonds.append((i, j))
    bonds = bonds if bonds else None

    mv = MolecularViewer(structure.cart_coords, topology={'atom_types': atom_types, 'bonds': bonds})

    if bonds:
        mv.ball_and_sticks(stick_radius=0.2)
    for i in structure.sites:
        el = i.specie.symbol
        coord = i.coords
        r = CovalentRadius.radius[el]
        mv.add_representation('spheres', {'coordinates': coord.astype('float32'),
                                          'colors': [get_atom_color(el)],
                                          'radii': [r * 0.5],
                                          'opacity': 1.0})
    if show_box:
        o = np.array([0, 0, 0])
        a, b, c = structure.lattice.matrix[0], structure.lattice.matrix[1], structure.lattice.matrix[2]
        starts = [o, o, o, a, a, b, b, c, c, a + b, a + c, b + c]
        ends = [a, b, c, a + b, a + c, b + a, b + c, c + a, c + b, a + b + c, a + b + c, a + b + c]
        colors = [0xffffff for i in range(12)]
        mv.add_representation('lines', {'startCoords': np.array(starts),
                                        'endCoords': np.array(ends),
                                        'startColors': colors,
                                        'endColors': colors})
    return mv