from calphad_tdb_ingester.converter import convert


def test_pbte():
    """
    Tests that correct number of properties, their names, and values were parsed into the pifs created
    """
    pif = convert(files=["./test_files/test_PbTe.TDB"], database_name="2017Bajaj")

    assert pif.chemical_formula == "PbTe", "Incorrectly parsed formula of parent PIF"
    assert pif.ids[0].value == "2017Bajaj", "Incorrectly parsed argument 'database_name'"
    assert len(pif.sub_systems) > 0, "At least one sub-system must be present in a PIF"
    assert len(pif.properties) > 0, "At least one property must be present in a PIF"

    assert pif.properties[0].name == "Thermodynamic database", "Filename not added as property"

    subsystem_tags = [sub_sys.tags[0] for sub_sys in pif.sub_systems]
    # Check for tags in sub-systems
    assert "Element" in subsystem_tags
    assert "Specie" in subsystem_tags
    assert "Phase" in subsystem_tags

    # extract and test for all elements, species, and phases
    elements = [sub_sys.chemical_formula for sub_sys in pif.sub_systems if sub_sys.tags[0] == "Element"]
    assert elements == ["Pb", None, "Te"]
    species = [sub_sys.names[0] for sub_sys in pif.sub_systems if sub_sys.tags[0] == "Specie"]
    assert species == ["Pbte_L"]
    phases = [sub_sys.names[0] for sub_sys in pif.sub_systems if sub_sys.tags[0] == "Phase"]
    assert phases == ["RHOMBOHEDRAL_A7", "HEXAGONAL_A8", "LIQUID", "PbTe"]

    for sub_sys in pif.sub_systems:

        subsys_prop_names = [subsys_prop.name for subsys_prop in sub_sys.properties]

        if sub_sys.tags[0] == "Element" and sub_sys.chemical_formula == "Pb":

            assert "Enthalpy of reference state" in subsys_prop_names

            for prop in sub_sys.properties:
                if prop.name == "Enthalpy of reference state":
                    assert prop.scalars[0].value == 6870.0, "Incorrectly parsed element enthalpy"

        elif sub_sys.tags[0] == "Specie" and sub_sys.names[0] == "Pbte_L":
            assert sub_sys.chemical_formula == "PbTe", "Incorrectly parse specie property value"

        elif sub_sys.tags[0] == "Phase" and sub_sys.names[0] == "HEXAGONAL_A8":
            assert sub_sys.composition[0].element == "(Te)"
            assert sub_sys.composition[0].ideal_atomic_percent == 100.0


def test_ausi():
    """
    Tests that correct number of properties, their names, and values were parsed into the pifs created
    """
    pif = convert(files=["./test_files/test_AuSi.TDB"], database_name="2018AuSi")

    assert pif.chemical_formula == "SiAu", "Incorrectly parsed formula of parent PIF"
    assert pif.ids[0].value == "2018AuSi", "Incorrectly parsed argument 'database_name'"
    assert len(pif.sub_systems) > 0, "At least one sub-system must be present in a PIF"
    assert len(pif.properties) > 0, "At least one property must be present in a PIF"

    assert pif.properties[0].name == "Thermodynamic database", "Filename not added as property"

    subsystem_tags = [sub_sys.tags[0] for sub_sys in pif.sub_systems]
    # Check for tags in sub-systems
    assert "Element" in subsystem_tags
    assert "Specie" not in subsystem_tags
    assert "Phase" in subsystem_tags

    # extract and test for all elements, species, and phases
    elements = [sub_sys.chemical_formula for sub_sys in pif.sub_systems if sub_sys.tags[0] == "Element"]
    assert elements == [None, "Si", "Au"]
    phases = [sub_sys.names[0] for sub_sys in pif.sub_systems if sub_sys.tags[0] == "Phase"]
    assert phases == ['HCP_Zn', 'BCC_A2', 'LIQUID', 'HCP_A3', 'CUB_A13', 'FCC_A1', 'DIAMOND_A4', 'CBCC_A12']

    for sub_sys in pif.sub_systems:

        subsys_prop_names = [subsys_prop.name for subsys_prop in sub_sys.properties]

        if sub_sys.tags[0] == "Element" and sub_sys.chemical_formula == "Si":

            assert "Enthalpy of reference state" in subsys_prop_names

            for prop in sub_sys.properties:
                if prop.name == "Enthalpy of reference state":
                    assert prop.scalars[0].value == 3217.5, "Incorrectly parsed element enthalpy"

        elif sub_sys.tags[0] == "Phase" and sub_sys.names[0] == "CUB_A13":
            assert sub_sys.composition[0].element == "(Si)"
            assert sub_sys.composition[0].ideal_atomic_percent == 50.0
            assert sub_sys.composition[1].element == "(Va)"
            assert sub_sys.composition[1].ideal_atomic_percent == 50.0


if __name__ == '__main__':
    test_pbte()
    test_ausi()
