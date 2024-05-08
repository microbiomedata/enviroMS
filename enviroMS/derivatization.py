import nmdc_schema.nmdc as nmdc
from linkml_runtime.dumpers import yaml_dumper, json_dumper
from uuid import uuid4


b1 = nmdc.Biosample(
    id="nmdc:biosample:SAMN0626712",
    description='Groundwater microbial communities from the Columbia River',
    env_broad_scale=nmdc.ControlledTermValue(term=nmdc.OntologyClass(id='ENVO:01000253', name='freshwater river biome')),
    env_local_scale=nmdc.ControlledTermValue(term=nmdc.OntologyClass(id='ENVO:00000384', name='river bed')),
    env_medium=nmdc.ControlledTermValue(term=nmdc.OntologyClass(id='ENVO:00002007', name='sediment')),
    sample_link="gold:Gb0126441"
)

d = nmdc.DataObject()
d.was_generated_by
samp_proc_db = nmdc.Database()

samp_proc_db.biosample_set.append(b1)

weighing = nmdc.MaterialSamplingActivity(
    biosample_input="EMSL:2f7107d6-5dd1-11ec-bf63-0242ac130002",
    amount_collected=nmdc.QuantityValue(has_unit='grams', has_numeric_value=6.0),
    sampling_method="weighing",
    collected_into=nmdc.MaterialContainer(
        container_size=nmdc.QuantityValue(has_unit='mL', has_numeric_value=50.0),
        container_type="screw_top_conical"),
    material_output="nmdc:{}".format(uuid4()),
)

samp_proc_db.material_sampling_activity_set.append(weighing)

se6 = nmdc.MaterialSample(id=weighing.material_output, description="a 6 gram aliquot of EMSL:2f7107d6-5dd1-11ec-bf63-0242ac130002")

samp_proc_db.material_sample_set.append(se6)

dissolving = nmdc.DissolvingActivity(
    material_input=se6.id,
    dissolution_aided_by=nmdc.LabDevice(
        device_type="orbital_shaker",
        activity_speed=nmdc.QuantityValue(
            has_unit='rpm',
            has_numeric_value=800.0),
        activity_time=nmdc.QuantityValue(
            has_unit='hours',
            has_numeric_value=2.0)),
    dissolution_reagent='deionized_water',
    dissolution_volume=nmdc.QuantityValue(
        has_unit='mL',
        has_numeric_value=30.0,
    ),
    dissolved_in=nmdc.MaterialContainer(
        container_size=nmdc.QuantityValue(
            has_unit='mL',
            has_numeric_value=50.0
        ),
        container_type="screw_top_conical"
    ),
    material_output="nmdc:{}".format(uuid4()),
)
samp_proc_db.dissolving_activity_set.append(dissolving)

se7 = nmdc.MaterialSample(dissolving.material_output,
                          description="monet_data:somextract_6 dissolved in 30 mL of water")
'''                          
[solubilization-activity1]
id = 'derive:8'
source_material = 'derive:7'
solvent = {type = 'MSTFA', concentration= '1%', reagent = 'TMCS'}
syringe = {type = 'Hamilton'}
volume = { numeric_value = '80', unit = 'µL' }
shaker = {type = 'vortex', numeric_value = '20', unit = 'seconds'}

[reaction-activity1]
id = 'derive:9'
source_material = 'derive:8'
shaker = {type = 'thermomixer', numeric_value = '1000', unit = 'rpm'}
temperature = { numeric_value = '37', unit = 'C' }
time = { numeric_value = '30', unit = 'minutes'}

'''
samp_proc_db.material_sample_set.append(se7)

reaction = nmdc.ReactionActivity(
    material_input=se7.id,
    reaction_aided_by=nmdc.LabDevice(
        device_type="thermomixer",
        activity_temperature=nmdc.QuantityValue(
            has_unit='degrees Celsius',
            has_numeric_value=37.0),
        activity_time=nmdc.QuantityValue(
            has_unit='hours',
            has_numeric_value=1.5)),
    material_output="nmdc:{}".format(uuid4()),
)

samp_proc_db.reaction_activity_set.append(reaction)

d5 = nmdc.MaterialSample(id=reaction.material_output,
    description="something at the end of a reaction")

samp_proc_db.material_sample_set.append(d5)

print(yaml_dumper.dump(samp_proc_db, "samp_proc_instantiation.yaml"))
print(json_dumper.dump(samp_proc_db, "sample_process_gcms.json"))
