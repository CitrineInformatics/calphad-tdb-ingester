from collections import namedtuple
import re
from pypif.obj import *


__author__ = "Saurabh Bajaj <sbajaj@citrine.io>"


def name_and_code(name_str):
    """
    Extract phase name and possible model code from string.

    Args:
        name_str: (str) Raw string of phase name, possibly including a model code.

    Returns:
        ph_name (str) The phase name.
        code (str) The model code, if present. If not present, None.
    """
    try:
        ph_name, code = name_str.split(':')
    except ValueError:
        ph_name = name_str
        code = None

    if code not in ['G', 'A', 'Y', 'L', 'I', 'F', 'B']:
        ph_name = name_str
        code = None

    return ph_name, code


def parse_file(filename):
    """

    Args:
        filename: TDB file

    Returns:
        Dictionaries containing elements, species, and phases

    """
    # Create namedtuple for storing elements and related info
    Element = namedtuple('Element', ['Reference_state', 'mass_g_per_mol', 'H_ref_J_per_mol', 'S_ref_J_per_mol_K'])

    # Initialize metadata dictionaries
    els = {}
    sps = {}
    phs = {}

    # Read in the whole database, the first and only one
    with open(filename, 'r') as f:
        lines = f.readlines()

    # Remove lines starting with comments ($)
    lines = [line for line in lines if line[0][0] != '$']

    # Break lines up into !-delimited commands
    lines = ''.join(lines)
    lines = lines.split('!')

    # Loop over each line in the tdb file and extract the metadata
    for line in lines:
        line = line.split()

        if len(line) == 0:
            continue

        # Add elements sub-systems on the go
        elif line[0] in 'ELEMENTS':
            el_name = line[1]

            # If no character in element name, skip it
            if not re.search('[a-zA-Z]', el_name):
                continue

            ref_name = line[2]
            mass = float(line[3])
            h_ref = float(line[4])
            s_ref = float(line[5])

            # Store in elements dictionary
            els[el_name.title()] = Element(ref_name, mass, h_ref, s_ref)

        # Create species dictionary on the go, add as sub-systems later
        elif line[0] in 'SPECIES':
            sp_name = line[1]
            formula = line[2]
            sps[sp_name] = formula

        # Create phases dictionary on the go, add as sub-systems later
        elif line[0] in 'PHASE':
            ph_name, model_code = name_and_code(line[1])
            typecode = line[2]
            num_sublattices = int(line[3])
            sublattice_sites = [float(i) for i in line[4:]]
            phs[ph_name] = {}
            if model_code is not None:
                phs[ph_name]['model_code'] = model_code
            phs[ph_name]['typecode'] = typecode
            phs[ph_name]['num_sublattices'] = num_sublattices
            phs[ph_name]['subblatice_sites'] = sublattice_sites

        elif line[0] in 'CONSTITUENT':
            ph_c_name, model_code = name_and_code(line[1])
            con_str = ''.join(line[2:])
            con_list = [i.split(',') for i in con_str.strip(':').split(':')]
            # Assumes phase "ph_c_name" is already present in phase dictionary, which is true in TDB files since
            # CONSTITUENTS follow PHASE every time
            phs[ph_c_name]['constituents'] = con_list

    return els, sps, phs


def convert(files=[], database_name=None):
    """
    Read a CALPHAD thermodynamic database (TDB) file and extract metadata.

    Args:
        files: (list) of string tdb filenames to parse, including the (relative)path to the file.
        database_name: (str) unique name of database

    Returns:
        chem_systems (list) of PIF chemical systems
    """
    # only expecting 1 file
    assert len(files) == 1

    # Initialize list of PIFs
    # chem_systems = []

    # Initialize PIF chemical system
    chem_sys = ChemicalSystem()
    chem_sys.properties = []
    chem_sys.sub_systems = []

    # Add file ID to parent PIF ID
    chem_sys.ids = [Id(name="Database Name", value=database_name)]

    # Attach TDB file to parent PIF
    chem_sys.properties.append(Property(name="Thermodynamic database", files=[FileReference(relative_path=files[0])]))

    # Parse file and store metadata extracted in dictionaries
    elements, species, phases = parse_file(files[0])

    # Create name of chemical system from element names, eg: Al-Co-O, and add as name of parent PIF
    system_name = "".join([el for el in elements if re.search('[a-zA-Z]', el) and "va" not in el.lower()])
    chem_sys.chemical_formula = system_name

    # create a sub-system for each element
    for el_name in elements:

        # Create element sub-system
        el_sys = ChemicalSystem()
        el_sys.properties = []

        # Don't add element name as formula if it's a vacancy, add it as a name instead
        if el_name.lower() != "va":
            el_sys.chemical_formula = el_name.title()
        else:
            el_sys.names = el_name.title()

        # Add element properties
        el_sys.properties.append(Property(name="Element", scalars=[Scalar(value=el_name.title())]))
        el_sys.properties.append(Property(name="Reference state",
                                          scalars=[Scalar(value=elements[el_name].Reference_state)]))
        el_sys.properties.append(Property(name="Mass of reference state",
                                          scalars=[Scalar(value=elements[el_name].mass_g_per_mol)], units='g/mol'))
        el_sys.properties.append(Property(name="Enthalpy of reference state",
                                          scalars=[Scalar(value=elements[el_name].H_ref_J_per_mol)], units='J/mol'))
        el_sys.properties.append(Property(name="Entropy of reference state",
                                          scalars=[Scalar(value=elements[el_name].S_ref_J_per_mol_K)],
                                          units='J/(mol.K)'))

        # Tag it
        el_sys.tags = ["Element"]

        # Add element sub-system to main pif
        chem_sys.sub_systems.append(el_sys)

    # create a sub-system for each specie
    if len(species) > 0:

        for sp in species:

            sp_sys = ChemicalSystem()
            sp_sys.properties = []

            sp_name = sp.title()
            sp_sys.names = [sp.title()]

            # Fix case sensitivity in species names such as "Pbte_L"
            for el in elements:

                # If no character in element name or VA, skip it
                if not re.search('[a-zA-Z]', el) or el == "VA":
                    continue

                if el.lower() in sp_name.lower():
                    sp_name = sp_name.replace(el.lower(), el.title())

            # Add specie formula as formula instead of as a property
            sp_sys.chemical_formula = species[sp].title().replace("1", "")
            # sp_sys.properties.append(Property(name="Formula of species", scalars=[Scalar(value=species[sp].title())]))

            # Tag it
            sp_sys.tags = ["Specie"]

            # Add specie sub-system to main pif
            chem_sys.sub_systems.append(sp_sys)

    # create a sub-system for each phase
    for phase in phases:
        ph_sys = ChemicalSystem()
        ph_sys.composition = []
        ph_sys.properties = []

        # Case sensitivize phase names that have formulae in them
        excluded_names = ["LIQUID", "GAS", "HCP", "FCC", "BCC", "SIGMA", "LAVES", "RHOMBOHEDRAL", "HEXAGONAL",
                          "DIAMOND", "TETRAG", "CUB", "BCT", "ORTHO"]
        for exc_name in excluded_names:
            if exc_name in phase:
                phase_name = phase
                break
            else:
                phase_name = phase.title()

        # Fix case sensitivity in phase names such as "Pbte"
        for el in elements:

            # If no character in element name or VA, skip it
            if not re.search('[a-zA-Z]', el) or el == "VA":
                continue

            if el.lower() in phase_name.lower():
                phase_name = phase_name.replace(el.lower(), el.title())

        # This phase is known phase name for Zn
        if phase_name == "HCP_ZN":
            phase_name = "HCP_Zn"

        ph_sys.names = [phase_name]

        # Add phase properties
        code_state = {"G": "Gas", "A": "Aqueous", "Y": "Ionic liquid", "L": "Liquid", "I": "Ionic solid",
                      "F": "fcc or hcp ordered", "B": "bcc ordered"}
        if "model_code" in phases[phase]:
            if phases[phase]["model_code"] in code_state:
                ph_sys.properties.append(Property(name="State",
                                                  scalars=[Scalar(value=code_state[phases[phase]["model_code"]])]))
            else:
                ph_sys.properties.append(Property(name="State", scalars=[Scalar(value="Solid")]))

        # Add phase composition
        for idx, constituent_lst in enumerate(phases[phase]['constituents']):
            ph_const = Composition()
            ph_const.element = "("
            for constituent in constituent_lst:
                ph_const.element += constituent.title().replace("%", "") + ", "
            ph_const.element = ph_const.element[:-2]
            ph_const.element += ")"
            ph_const.ideal_atomic_percent = \
                round((phases[phase]["subblatice_sites"][idx]/sum(phases[phase]["subblatice_sites"])) * 100.0, 2)

            ph_sys.composition.append(ph_const)

        # Tag it
        ph_sys.tags = ["Phase"]

        # Add specie sub-system to main pif
        chem_sys.sub_systems.append(ph_sys)

    return chem_sys
