import hashlib
import os
import time
import xml.etree.ElementTree as ET
import random
import numpy as np


def read_voxlyze_results(population, print_log, filename="softbotsOutput.xml"):
    i = 0
    max_attempts = 60
    file_size = 0
    this_file = ""

    while (i < max_attempts) and (file_size == 0):
        try:
            file_size = os.stat(filename).st_size
            this_file = open(filename)
            this_file.close()
        except ImportError:  # TODO: is this the correct exception?
            file_size = 0
        i += 1
        time.sleep(1)

    if file_size == 0:
        print_log.message("ERROR: Cannot find a non-empty fitness file in %d attempts: abort" % max_attempts)
        exit(1)

    results = {rank: None for rank in range(len(population.objective_dict))}
    for rank, details in population.objective_dict.items():
        this_file = open(filename)  # TODO: is there a way to just go back to the first line without reopening the file?
        tag = details["tag"]
        if tag is not None:
            for line in this_file:
                if tag in line:
                    results[rank] = float(line[line.find(tag) + len(tag):line.find("</" + tag[1:])])
        this_file.close()

    return results


def read_voxelyze_centroids(population, print_log, filename="softbotsOutput.xml"):
    i = 0
    max_attempts = 60
    file_size = 0
    this_file = ""

    while (i < max_attempts) and (file_size == 0):
        try:
            file_size = os.stat(filename).st_size
            this_file = open(filename)
            this_file.close()
        except ImportError:  # TODO: is this the correct exception?
            file_size = 0
        i += 1
        time.sleep(1)

    if file_size == 0:
        print_log.message("ERROR: Cannot find a non-empty fitness file in %d attempts: abort" % max_attempts)
        exit(1)

    centroids = []
    root = ET.parse(filename).getroot()
    for trace in root.findall('CMTrace/TraceStep'):
        t = float(trace.find('Time').text)
        x = float(trace.find('TraceX').text)
        y = float(trace.find('TraceY').text)
        z = float(trace.find('TraceZ').text)
        centroids.append(np.array([x, y, z, t]))

    return centroids


def write_voxelyze_file(sim, env, individual, run_directory, run_name):
    # TODO: work in base.py to remove redundant static text in this function

    # update any env variables based on outputs instead of writing outputs in
    for name, details in individual.genotype.to_phenotype_mapping.items():
        if details["env_kws"] is not None:
            for env_key, env_func in details["env_kws"].items():
                setattr(env, env_key, env_func(details["state"]))  # currently only used when evolving frequency
                # print env_key, env_func(details["state"])

    new_materials = ""
    if hasattr(individual.genotype, "materials"):
        for mat_idx in individual.genotype.materials.keys():
            curr_ind_material = individual.genotype.materials.get(mat_idx)
            new_material = "        <Material ID=\"{id}\">\n\
            <MatType>0</MatType>\n\
            <Name>{name}</Name>\n\
            <Display>\n\
            <Red>{r}</Red>\n\
            <Green>{g}</Green>\n\
            <Blue>{b}</Blue>\n\
            <Alpha>1</Alpha>\n\
            </Display>\n\
            <Mechanical>\n\
            <MatModel>0</MatModel>\n\
            <Elastic_Mod>{young_modulus}</Elastic_Mod>\n\
            <Plastic_Mod>0</Plastic_Mod>\n\
            <Yield_Stress>0</Yield_Stress>\n\
            <FailModel>0</FailModel>\n\
            <Fail_Stress>0</Fail_Stress>\n\
            <Fail_Strain>0</Fail_Strain>\n\
            <Density>{density}</Density>\n\
            <Poissons_Ratio>0.35</Poissons_Ratio>\n\
            <CTE>{cte}</CTE>\n\
            <uStatic>1</uStatic>\n\
            <uDynamic>0.5</uDynamic>\n\
            </Mechanical>\n\
        </Material>\n".format(id=mat_idx, name=curr_ind_material.name,
                                  r=curr_ind_material.rgb[0], g=curr_ind_material.rgb[1], b=curr_ind_material.rgb[2],
                                  young_modulus=curr_ind_material.young_modulus, density=curr_ind_material.density,
                                  cte=curr_ind_material.cte)
            new_materials += new_material

    voxelyze_file = open(run_directory + "/voxelyzeFiles/" + run_name + "--id_%05i.vxa" % individual.id, "w")

    voxelyze_file.write(
        "<?xml version=\"1.0\" encoding=\"ISO-8859-1\"?>\n\
        <VXA Version=\"1.0\">\n\
        <Simulator>\n")

    # Sim
    for name, tag in sim.new_param_tag_dict.items():
        voxelyze_file.write(tag + str(getattr(sim, name)) + "</" + tag[1:] + "\n")

    voxelyze_file.write(
        "<Integration>\n\
        <Integrator>0</Integrator>\n\
        <DtFrac>" + str(sim.dt_frac) + "</DtFrac>\n\
        </Integration>\n\
        <Damping>\n\
        <BondDampingZ>1</BondDampingZ>\n\
        <ColDampingZ>0.8</ColDampingZ>\n\
        <SlowDampingZ>0.01</SlowDampingZ>\n\
        </Damping>\n\
        <Collisions>\n\
        <SelfColEnabled>" + str(int(sim.self_collisions_enabled)) + "</SelfColEnabled>\n\
        <ColSystem>3</ColSystem>\n\
        <CollisionHorizon>2</CollisionHorizon>\n\
        </Collisions>\n\
        <Features>\n\
        <FluidDampEnabled>0</FluidDampEnabled>\n\
        <PoissonKickBackEnabled>0</PoissonKickBackEnabled>\n\
        <EnforceLatticeEnabled>0</EnforceLatticeEnabled>\n\
        </Features>\n\
        <SurfMesh>\n\
        <CMesh>\n\
        <DrawSmooth>1</DrawSmooth>\n\
        <Vertices/>\n\
        <Facets/>\n\
        <Lines/>\n\
        </CMesh>\n\
        </SurfMesh>\n\
        <StopCondition>\n\
        <StopConditionType>" + str(int(sim.stop_condition)) + "</StopConditionType>\n\
        <StopConditionValue>" + str(sim.simulation_time) + "</StopConditionValue>\n\
        <AfterlifeTime>" + str(sim.afterlife_time) + "</AfterlifeTime>\n\
        <MidLifeFreezeTime>" + str(sim.mid_life_freeze_time) + "</MidLifeFreezeTime>\n\
        <InitCmTime>" + str(sim.fitness_eval_init_time) + "</InitCmTime>\n\
        </StopCondition>\n\
        <EquilibriumMode>\n\
        <EquilibriumModeEnabled>" + str(sim.equilibrium_mode) + "</EquilibriumModeEnabled>\n\
        </EquilibriumMode>\n\
        <GA>\n\
        <WriteFitnessFile>1</WriteFitnessFile>\n\
        <FitnessFileName>" + run_directory + "/fitnessFiles/softbotsOutput--id_%05i.xml" % individual.id +
        "</FitnessFileName>\n\
        <QhullTmpFile>" + run_directory + "/tempFiles/qhullInput--id_%05i.txt" % individual.id + "</QhullTmpFile>\n\
        <CurvaturesTmpFile>" + run_directory + "/tempFiles/curvatures--id_%05i.txt" % individual.id +
        "</CurvaturesTmpFile>\n\
        </GA>\n\
        <MinTempFact>" + str(sim.min_temp_fact) + "</MinTempFact>\n\
        <MaxTempFactChange>" + str(sim.max_temp_fact_change) + "</MaxTempFactChange>\n\
        <MaxStiffnessChange>" + str(sim.max_stiffness_change) + "</MaxStiffnessChange>\n\
        <MinElasticMod>" + str(sim.min_elastic_mod) + "</MinElasticMod>\n\
        <MaxElasticMod>" + str(sim.max_elastic_mod) + "</MaxElasticMod>\n\
        <ErrorThreshold>" + str(0) + "</ErrorThreshold>\n\
        <ThresholdTime>" + str(0) + "</ThresholdTime>\n\
        <MaxKP>" + str(0) + "</MaxKP>\n\
        <MaxKI>" + str(0) + "</MaxKI>\n\
        <MaxANTIWINDUP>" + str(0) + "</MaxANTIWINDUP>\n")

    if hasattr(individual, "parent_lifetime"):
        if individual.parent_lifetime > 0:
            voxelyze_file.write("<ParentLifetime>" + str(individual.parent_lifetime) + "</ParentLifetime>\n")
        elif individual.lifetime > 0:
            voxelyze_file.write("<ParentLifetime>" + str(individual.lifetime) + "</ParentLifetime>\n")

    voxelyze_file.write("</Simulator>\n")

    # Env
    voxelyze_file.write(
        "<Environment>\n")
    for name, tag in env.new_param_tag_dict.items():
        voxelyze_file.write(tag + str(getattr(env, name)) + "</" + tag[1:] + "\n")

    voxelyze_file.write("    <Boundary_Conditions>\n")

    if env.obstacles:
        num_bcs = 0
        for obstacle in env.obst_list:
            num_bcs += len(obstacle.walls)
        voxelyze_file.write("        <NumBCs>" + str(num_bcs) + "</NumBCs>\n")
        for obstacle in env.obst_list:
            for wall in obstacle.walls:
                voxelyze_file.write("        <FRegion>\n\
            <PrimType>" + str(obstacle.prim_type) + "</PrimType>\n\
            <X>" + str(wall["X"]) + "</X>\n\
            <Y>" + str(wall["Y"]) + "</Y>\n\
            <Z>" + str(wall["Z"]) + "</Z>\n\
            <dX>" + str(wall["dX"]) + "</dX>\n\
            <dY>" + str(wall["dY"]) + "</dY>\n\
            <dZ>" + str(wall["dZ"]) + "</dZ>\n\
            <alfa>" + str(obstacle.alfa) + "</alfa>\n\
            <DofFixed>63</DofFixed>\n\
        </FRegion>\n"
                )
    else:
        voxelyze_file.write("       <NumBCs>0</NumBCs>\n")

    voxelyze_file.write("\
        </Boundary_Conditions>\n\
        <Forced_Regions>\n\
        <NumForced>0</NumForced>\n\
        </Forced_Regions>\n\
        <Gravity>\n\
        <GravEnabled>" + str(env.gravity_enabled) + "</GravEnabled>\n\
        <GravAcc>-9.81</GravAcc>\n\
        <FloorEnabled>" + str(env.floor_enabled) + "</FloorEnabled>\n\
        <FloorSlope>" + str(env.floor_slope) + "</FloorSlope>\n\
        </Gravity>\n\
        <Thermal>\n\
        <TempEnabled>" + str(env.temp_enabled) + "</TempEnabled>\n\
        <TempAmp>" + str(env.temp_amp) + "</TempAmp>\n\
        <TempBase>" + str(env.temp_base) + "</TempBase>\n\
        <VaryTempEnabled>1</VaryTempEnabled>\n\
        <TempPeriod>" + str(env.period) + "</TempPeriod>\n\
        </Thermal>\n\
        <TimeBetweenTraces>" + str(env.time_between_traces) + "</TimeBetweenTraces>\n\
        <SaveTraces>" + str(env.save_traces) + "</SaveTraces>\n\
        <StickyFloor>" + str(env.sticky_floor) + "</StickyFloor>\n\
        </Environment>\n")

    voxelyze_file.write(
        "<VXC Version=\"0.93\">\n\
        <Lattice>\n\
        <Lattice_Dim>" + str(env.lattice_dimension) + "</Lattice_Dim>\n\
        <X_Dim_Adj>1</X_Dim_Adj>\n\
        <Y_Dim_Adj>1</Y_Dim_Adj>\n\
        <Z_Dim_Adj>1</Z_Dim_Adj>\n\
        <X_Line_Offset>0</X_Line_Offset>\n\
        <Y_Line_Offset>0</Y_Line_Offset>\n\
        <X_Layer_Offset>0</X_Layer_Offset>\n\
        <Y_Layer_Offset>0</Y_Layer_Offset>\n\
        </Lattice>\n\
        <Voxel>\n\
        <Vox_Name>BOX</Vox_Name>\n\
        <X_Squeeze>1</X_Squeeze>\n\
        <Y_Squeeze>1</Y_Squeeze>\n\
        <Z_Squeeze>1</Z_Squeeze>\n\
        </Voxel>\n\
        <Palette>\n\
        <Material ID=\"1\">\n\
            <MatType>0</MatType>\n\
            <Name>Passive_Soft</Name>\n\
            <Display>\n\
            <Red>0</Red>\n\
            <Green>1</Green>\n\
            <Blue>1</Blue>\n\
            <Alpha>1</Alpha>\n\
            </Display>\n\
            <Mechanical>\n\
            <MatModel>0</MatModel>\n\
            <Elastic_Mod>" + str(env.fat_stiffness) + "</Elastic_Mod>\n\
            <Plastic_Mod>0</Plastic_Mod>\n\
            <Yield_Stress>0</Yield_Stress>\n\
            <FailModel>0</FailModel>\n\
            <Fail_Stress>0</Fail_Stress>\n\
            <Fail_Strain>0</Fail_Strain>\n\
            <Density>1e+006</Density>\n\
            <Poissons_Ratio>0.35</Poissons_Ratio>\n\
            <CTE>0</CTE>\n\
            <uStatic>1</uStatic>\n\
            <uDynamic>0.5</uDynamic>\n\
            </Mechanical>\n\
        </Material>\n\
        <Material ID=\"2\">\n\
            <MatType>0</MatType>\n\
            <Name>Passive_Hard</Name>\n\
            <Display>\n\
            <Red>0</Red>\n\
            <Green>0</Green>\n\
            <Blue>1</Blue>\n\
            <Alpha>1</Alpha>\n\
            </Display>\n\
            <Mechanical>\n\
            <MatModel>0</MatModel>\n\
            <Elastic_Mod>" + str(env.bone_stiffness) + "</Elastic_Mod>\n\
            <Plastic_Mod>0</Plastic_Mod>\n\
            <Yield_Stress>0</Yield_Stress>\n\
            <FailModel>0</FailModel>\n\
            <Fail_Stress>0</Fail_Stress>\n\
            <Fail_Strain>0</Fail_Strain>\n\
            <Density>1e+006</Density>\n\
            <Poissons_Ratio>0.35</Poissons_Ratio>\n\
            <CTE>0</CTE>\n\
            <uStatic>1</uStatic>\n\
            <uDynamic>0.5</uDynamic>\n\
            </Mechanical>\n\
        </Material>\n\
            <Material ID=\"3\">\n\
            <MatType>0</MatType>\n\
            <Name>Active_+</Name>\n\
            <Display>\n\
            <Red>1</Red>\n\
            <Green>0</Green>\n\
            <Blue>0</Blue>\n\
            <Alpha>1</Alpha>\n\
            </Display>\n\
            <Mechanical>\n\
            <MatModel>0</MatModel>\n\
            <Elastic_Mod>" + str(env.muscle_stiffness) + "</Elastic_Mod>\n\
            <Plastic_Mod>0</Plastic_Mod>\n\
            <Yield_Stress>0</Yield_Stress>\n\
            <FailModel>0</FailModel>\n\
            <Fail_Stress>0</Fail_Stress>\n\
            <Fail_Strain>0</Fail_Strain>\n\
            <Density>1e+006</Density>\n\
            <Poissons_Ratio>0.35</Poissons_Ratio>\n\
            <CTE>" + str(env.cte) + "</CTE>\n\
            <uStatic>1</uStatic>\n\
            <uDynamic>0.5</uDynamic>\n\
            </Mechanical>\n\
        </Material>\n\
        <Material ID=\"4\">\n\
            <MatType>0</MatType>\n\
            <Name>Active_-</Name>\n\
            <Display>\n\
            <Red>0</Red>\n\
            <Green>1</Green>\n\
            <Blue>0</Blue>\n\
            <Alpha>1</Alpha>\n\
            </Display>\n\
            <Mechanical>\n\
            <MatModel>0</MatModel>\n\
            <Elastic_Mod>" + str(env.muscle_stiffness) + "</Elastic_Mod>\n\
            <Plastic_Mod>0</Plastic_Mod>\n\
            <Yield_Stress>0</Yield_Stress>\n\
            <FailModel>0</FailModel>\n\
            <Fail_Stress>0</Fail_Stress>\n\
            <Fail_Strain>0</Fail_Strain>\n\
            <Density>1e+006</Density>\n\
            <Poissons_Ratio>0.35</Poissons_Ratio>\n\
            <CTE>" + str(-env.cte) + "</CTE>\n\
            <uStatic>1</uStatic>\n\
            <uDynamic>0.5</uDynamic>\n\
            </Mechanical>\n\
        </Material>\n\
        <Material ID=\"5\">\n\
            <MatType>0</MatType>\n\
            <Name>Obstacle</Name>\n\
            <Display>\n\
            <Red>1</Red>\n\
            <Green>0.784</Green>\n\
            <Blue>0</Blue>\n\
            <Alpha>1</Alpha>\n\
            </Display>\n\
            <Mechanical>\n\
            <MatModel>0</MatModel>\n\
            <Elastic_Mod>5e+009</Elastic_Mod>\n\
            <Plastic_Mod>0</Plastic_Mod>\n\
            <Yield_Stress>0</Yield_Stress>\n\
            <FailModel>0</FailModel>\n\
            <Fail_Stress>0</Fail_Stress>\n\
            <Fail_Strain>0</Fail_Strain>\n\
            <Density>1e+006</Density>\n\
            <Poissons_Ratio>0.35</Poissons_Ratio>\n\
            <CTE>0</CTE>\n\
            <uStatic>1</uStatic>\n\
            <uDynamic>0.5</uDynamic>\n\
            </Mechanical>\n\
        </Material>\n"
        + new_materials +
        "        </Palette>\n\
        <Structure Compression=\"ASCII_READABLE\">\n")

    if env.obstacles:
        voxelyze_file.write("\
            <X_Voxels>" + str(env.env_size[0]) + "</X_Voxels>\n\
            <Y_Voxels>" + str(env.env_size[1]) + "</Y_Voxels>\n\
            <Z_Voxels>" + str(env.env_size[2]) + "</Z_Voxels>\n"
        )
    else:
        voxelyze_file.write("\
            <X_Voxels>" + str(individual.genotype.orig_size_xyz[0]) + "</X_Voxels>\n\
            <Y_Voxels>" + str(individual.genotype.orig_size_xyz[1]) + "</Y_Voxels>\n\
            <Z_Voxels>" + str(individual.genotype.orig_size_xyz[2]) + "</Z_Voxels>\n"
        )

    all_tags = [details["tag"] for name, details in individual.genotype.to_phenotype_mapping.items()]
    if "<Data>" not in all_tags:  # not evolving topology -- fixed presence/absence of voxels
        voxelyze_file.write("<Data>\n")
        for z in range(individual.genotype.orig_size_xyz[2]):
            voxelyze_file.write("<Layer><![CDATA[")
            for y in range(individual.genotype.orig_size_xyz[1]):
                for x in range(individual.genotype.orig_size_xyz[0]):
                    voxelyze_file.write("3")
            voxelyze_file.write("]]></Layer>\n")
        voxelyze_file.write("</Data>\n")

    # Avoid re-evaluation of an individual
    string_for_md5 = ""
    string_for_md5 += str(env.temp_amp)
    string_for_md5 += str(env.period)
    string_for_md5 += str(env.cte)

    if hasattr(individual.genotype, "materials"):
        for mat_idx in individual.genotype.materials.keys():
            curr_ind_material = individual.genotype.materials.get(mat_idx)
            string_for_md5 += str(curr_ind_material.young_modulus)
            string_for_md5 += str(curr_ind_material.density)
            string_for_md5 += str(curr_ind_material.cte)

    for name, details in individual.genotype.to_phenotype_mapping.items():

        # start tag
        if details["env_kws"] is None:
            voxelyze_file.write(details["tag"] + "\n")

        # record any additional params associated with the output
        if details["params"] is not None:
            for param_tag, param in zip(details["param_tags"], details["params"]):
                voxelyze_file.write(param_tag + str(param) + "</" + param_tag[1:] + "\n")

        if details["env_kws"] is None:
            # write the output state matrix to file
            if not env.obstacles:
                for z in range(individual.genotype.orig_size_xyz[2]):
                    voxelyze_file.write("<Layer><![CDATA[")
                    for y in range(individual.genotype.orig_size_xyz[1]):
                        for x in range(individual.genotype.orig_size_xyz[0]):

                            state = details["output_type"](details["state"][x, y, z])
                            # for n, network in enumerate(individual.genotype):
                            #     if name in network.output_node_names:
                            #         state = individual.genotype[n].graph.node[name]["state"][x, y, z]

                            voxelyze_file.write(str(state))
                            if details["tag"] != "<Data>":  # TODO more dynamic
                                voxelyze_file.write(", ")
                            string_for_md5 += str(state)

                    voxelyze_file.write("]]></Layer>\n")
            else:
                for z in range(env.env_size[2]):
                    voxelyze_file.write("<Layer><![CDATA[")
                    for y in range(env.env_size[1]):
                        for x in range(env.env_size[0]):
                            state = env.env_matrix[x][y][z]

                            voxelyze_file.write(str(state))
                            if details["tag"] != "<Data>":  # TODO more dynamic
                                voxelyze_file.write(", ")
                            string_for_md5 += str(state)

                    voxelyze_file.write("]]></Layer>\n")

        # end tag
        if details["env_kws"] is None:
            voxelyze_file.write("</" + details["tag"][1:] + "\n")

    voxelyze_file.write(
        "</Structure>\n\
        </VXC>\n\
        </VXA>")
    voxelyze_file.close()

    m = hashlib.md5()
    m.update(string_for_md5)

    return m.hexdigest()
