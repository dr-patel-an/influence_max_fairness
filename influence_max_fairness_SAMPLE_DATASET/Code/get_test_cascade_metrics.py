import pandas as pd
import numpy as np
import time
import glob

start = time.time()
def DNI(seed_set_cascades):
    """
    Measure the number of distinct nodes in the test cascades started of the seed set
    """
    combined = set()    
    for i in seed_set_cascades.keys():
        for j in seed_set_cascades[i]:    
            combined = combined.union(j)
    return len(combined)

def DNI_fairness(seed_set_cascades, gender_dict):
    """
    Measure the fraction of males in the toal cascades
    """
    combined = set()    
    for i in seed_set_cascades.keys():
        for j in seed_set_cascades[i]:    
            combined = combined.union(j)
    list_DNI = list(combined)
    males = []
    females = []
    for n in list_DNI:
        if gender_dict[n] == '1':
            males.append(n)
        else:
            females.append(n)
#     print("Males in Test Cascade: {} \n Females in Test Cascade: {}".format(str(len(males)), str(len(females))))
    total_males_in_cascade = len(males)
    total_females_in_cascade = len(females)
    males_fraction_in_cascade = len(males)/(len(males) + len(females))
    return total_males_in_cascade, total_females_in_cascade, np.round(males_fraction_in_cascade, 4)

def fairness_score(I_males, I_females, N_males, N_females):
    male_ratio = I_males/N_males
    female_ratio = I_females/N_females
    ratio = [male_ratio, female_ratio]
    prod = 1
    for x in ratio:
        prod *= x
    return prod/(np.max(ratio)**len(ratio))

def get_gender_dict(path):
    with open(path, 'r',  encoding="ISO-8859-1") as f:
        contents = f.read()
    split_content = contents.split('\n')
    split_content = split_content[0:-1]
    split_content_list=[]
    for i in split_content:
        split_content_list.append(i.split(",")[1:])
    split_content_list=split_content_list[1:]
    
    gender_dict = {}
    for split_data in split_content_list:
        gender_dict[split_data[0]] = split_data[1]
    f.close()    
    return gender_dict


seed_file_path = "../Data/Weibo/Seeds/final_seeds.txt"
gender_profile_path = "../Data/Weibo/Init_Data/profile_gender.csv"
test_cascade_path = "../Data/Weibo/Init_Data/test_cascades.txt"

gender_dict = get_gender_dict(gender_profile_path)
print('total nodes in gender_dict: {}'.format(len(gender_dict)))
# print('total nodes in gender_dict: {}\ntime taken: {}'.format(len(gender_dict), time.time()- start))

def get_metrics(seed_file_path):
    f = open(seed_file_path,"r")
    l = f.read().replace("\n"," ")
    seed_set_all = [x for x in l.split(" ") if x!='']#[:1000]
    f.close()
    seed_cascades =  {}
    seed_set = set()
    for s in seed_set_all:
        seed_cascades[str(s)] = []
        
    with open(test_cascade_path) as f:
        for line in f:
            cascade = line.split(";")
            op_id = cascade[1].split(" ")[0]
            cascade = set(map(lambda x: x.split(" ")[0],cascade[2:]))
            if op_id in seed_cascades:
                seed_cascades[op_id].append(cascade)
                seed_set.add(op_id)
                
    seed_set_cascades = { seed: seed_cascades[seed] for seed in seed_set if len(seed_cascades[seed])>0 }
    spreading_DNI = DNI(seed_set_cascades)
    print("Seeds found :",len(seed_set_cascades))
    print("Distinct Nodes Infected: ", spreading_DNI)
    f.close()
    
    total_males_in_cascade, total_females_in_cascade, males_fraction_in_cascade = DNI_fairness(seed_set_cascades, gender_dict)
    fairness_score_value = np.round(fairness_score(total_males_in_cascade , total_females_in_cascade, 775836, 395037), 4)
    
    print('total males in cascade = {}\ntotal females in cascade = {}\nmales_fraction_in_cascade = {}\nfairness score = {}'.format(total_males_in_cascade, total_females_in_cascade, males_fraction_in_cascade, fairness_score_value))
    
    return spreading_DNI, total_males_in_cascade, total_females_in_cascade, males_fraction_in_cascade, np.round(1 - males_fraction_in_cascade, 4),  fairness_score_value


all_seed_files = []
for seed_set_file in glob.glob("../Data/Weibo/Seeds/*"):
    if 'final_seeds_5g_05a' in seed_set_file:
        all_seed_files.append(seed_set_file)

metrics = []
for seed_file in all_seed_files:  
    print('\n\n============================={}============================='.format(seed_file))
    total_infected_in_cascades, total_males_in_casc, total_females_in_cas, males_fraction_in_casc, females_fraction_in_casc, fairness_score_value = get_metrics(seed_file)
    metrics.append([seed_file, total_infected_in_cascades, total_males_in_casc, total_females_in_cas, males_fraction_in_casc, females_fraction_in_casc, fairness_score_value])
    
df = pd.DataFrame(metrics, columns = ['seed_file_name', 'total_distincet_infected_nodes', 'total_males_in_casc', 'total_females_in_cas', 'males_fraction_in_casc', 'females_fraction_in_casc', 'fairness_score_value'])
df.to_csv('./test_cascade_metrics_Approach_B.csv', index=False)
    
    