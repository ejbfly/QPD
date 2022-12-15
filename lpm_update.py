'''
MOSA FEM to LPM tools     

lpm_update.py 

This module provides low-level functions to read and write LPM input data, and invoke LPM matlab methods.
                                 
(c) E.Breunig, 2021
'''

import os
import shutil
import csv
from rich import print
import subprocess

def update_lpm_inputs(lpm_path, model_designation, new_parameters=None, new_noiseinputs=None):

    # make a new model specific folder wih the csv inputs
    if os.path.exists(lpm_path + '/' + model_designation):
        print("model path exists already....cleaning up")
        shutil.rmtree(lpm_path + '/' + model_designation)

    model_dir = lpm_path + '/' + model_designation
    os.mkdir(lpm_path + '/' + model_designation)
    
    parameter_files =  ['CCPM_constants.csv',
                        'CCPM_noiseInputs.csv',
                        'CCPM_parameters.csv',
                        'CCPM_transferFunctions.csv']

    for each_file in parameter_files:

        shutil.copy( lpm_path + '/CCPM/' + each_file, lpm_path + '/' + model_designation + '/' + each_file)
        #os.rename(lpm_path + '/' + each_file, lpm_path + '/' + each_file + '_original')

    # No we can write the new ttl_coefficients into the csv files. This sould also be outsourced into a dictionary function much like the writing to the Excel_TTL_Tool

    # open the parameter / noise_input csv file and update according to the content of the respective dictionary 

    for target, source in list({0: None, 1: new_noiseinputs, 2: new_parameters, 3: None}.items()):

        csv_filename = model_dir+'/'+parameter_files[target]

        with open(csv_filename) as csv_file:
            print(csv_filename)
            csv_data = csv.DictReader(csv_file)
            if 'varname' in csv_data.fieldnames:
                csv_data_dict = {data['varname']: data for data in csv_data}
            else:
                csv_data_dict = {data['name']: data for data in csv_data}
            fields = list(csv_data.fieldnames)
            
            #print(fields)
        if source is not None:
            for varname,value in source.items():

                print("Updating input for {}".format(varname))

                if varname in csv_data_dict.keys():

                    csv_data_dict[varname]['nominal']=value
                    csv_data_dict[varname]['requirements']=value
                    csv_data_dict[varname]['optimum']=value
                
                else:

                    print(f"{varname} is NOT in the input file")

        with open(model_dir+'/'+f"{model_designation}_"+parameter_files[target].split("_")[-1],'w',newline='') as csv_file:

            csv_writer = csv.DictWriter(csv_file,fields)
            csv_writer.writeheader()
            csv_writer.writerows(csv_data_dict.values())


def run_lpm_update(lpm_path, model_designation):

    # Copy the model specific parameters into the main path

    os.chdir(lpm_path)
    matlab_result = subprocess.Popen(f'matlab -batch "ltpda_startup; modelName={model_designation};modelName; generateNSDF; exit"', shell=True, stdout=subprocess.PIPE).stdout
    return matlab_result