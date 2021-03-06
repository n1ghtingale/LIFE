import sqlparse
import numpy as np
from hmmlearn import hmm
from sklearn.externals import joblib

count =0
observations = []
obsrv_lengths = []
#token_list =  ['Comparison', 'Punctuation', 'Whitespace', 'Keyword', 'IdentifierList', 'DML', 'Multiline', 'Wildcard', 'Parenthesis', 'Identifier', 'Where', 'Function', 'Single', 'Operator', 'Integer']
log_likelihoods = []
token_list = []

f = open("training.log")
for line in f:
    sql = line.split('Query')
    if(len(sql)==1):
        continue
    else:
        sql = sql[1].strip()
    res = sqlparse.parse(sql)
    stmt = res[0]
    print stmt.tokens
    #repr_name = [ [token._get_repr_name()] for token in stmt.tokens]
    #add unseen token to token list.
    token_list += list(set([token._get_repr_name() for token in stmt.tokens if token._get_repr_name() !='Whitespace'])
                       - set(token_list))
    repr_name = [[token_list.index(token._get_repr_name())] for token in stmt.tokens if token._get_repr_name() !='Whitespace']
    observations.append(repr_name)
    obsrv_lengths.append(len(repr_name))
    #print repr_name
    #w.write( ','.join(repr_name) +"\n")
    #count = count+1

print observations
#print obsrv_length

observations = np.concatenate(observations)

model = hmm.MultinomialHMM(n_components=27, n_iter=100, random_state=1)
#import ipdb; ipdb.set_trace()
model.fit(observations, obsrv_lengths)  
f.close()

f2 = open('training.log')
for line in f2:
    sql = line.split('\n')[0].split('Query')
    if(len(sql)==1):
        continue
    else:
        sql = sql[1].strip()
    res = sqlparse.parse(sql)
    stmt = res[0]
    print "sql: %s" % sql
    repr_name = [ [token_list.index(token._get_repr_name())] for token in stmt.tokens if token._get_repr_name() !='Whitespace']
    print repr_name
    log_likelihood = model.score(repr_name)
    print log_likelihood
    log_likelihoods.append(log_likelihood)

threshold = min(log_likelihoods)
model.anomaly_threshold = threshold
#w.close
print threshold
f2.close
exit(0)
#print("training finish")
#print model.transmat_
#exit(0)
#print("---------------")
#print model.emissionprob_
#print("---------------")
#print model.startprob_
#print "-------------------- transmission probability -----------------"
#for idx, matric in enumerate(model.transmat_):
#    print "state %d: " % (idx)
#    for state, prob in enumerate(matric):
#        print "\tto state %d: %E" %(state, prob)

#print("-" * 40)

#print "--------------------- emission probability --------------------"
#for idx, emissionprobs in enumerate(model.emissionprob_):
#    print "state %d: " % (idx)
#    for outsym, prob in enumerate(emissionprobs):
#        print "\t%s: %E" % (token_list[outsym], prob)

#print("-" * 40)

#print "--------------------- start probability --------------------"
#for idx, startprob in enumerate(model.startprob_):
#    print "state %d: %E" % (idx, startprob)
exit(0)

joblib.dump(model, "sqli-hmm.pkl");
