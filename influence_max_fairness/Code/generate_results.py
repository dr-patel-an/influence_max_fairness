import time
import re
import os
import sys
import numpy as np
import extract_feats_and_trainset_v2
import preprocess_for_imm
import rank_nodes
import infector
import iminfector_v2
# import evaluation2

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(os.path.join(dname,"..","Data"))
print('Current working directory for the code', os.getcwd()) # CHANDU: Updated


beta_values = [7] #[0.1, 0.5, 1, 3, 5, 7]
alpha = 0.5
all_seeds = [1250] #[250, 500, 750, 1000, 1250] 
learning_rate = 0.1
n_epochs = 5
embedding_size = 50
num_neg_samples = 10
log = open("time_log2.txt","a")
fn = 'weibo'
sampling_perc = 120


times = []
for beta_value in beta_values:
    for seed_size in all_seeds:
        start = time.time()
#         time.sleep(beta_value)
        final_seeds_filename = "Weibo/Seeds/final_seeds_5g_05a_{}s_{}b".format(seed_size, beta_value)
        final_seeds_filename = re.sub('[.]', '_', final_seeds_filename) + ".txt" 
        
        extract_feats_and_trainset_v2.run(fn,sampling_perc,log, beta_value)
        preprocess_for_imm.run(fn,log)
        rank_nodes.run(fn) 
        infector.run(fn,learning_rate,n_epochs,embedding_size,num_neg_samples,log)
        iminfector_v2.run(fn, embedding_size, log, seed_size, final_seeds_filename)    
        print("Time taken for the execution and writing "+ final_seeds_filename + ": " + str(np.round(float(time.time()-start), 3)))
        times.append([final_seeds_filename, np.round(float(time.time()-start), 3)])
        
log.close()  