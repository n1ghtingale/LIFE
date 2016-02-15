import sqlparse
import numpy as np
from hmmlearn import hmm
from sklearn.externals import joblib

count =0
observations = []
obsrv_lengths = []
token_list =  ['Comparison', 'Punctuation', 'Whitespace', 'Keyword', 'IdentifierList', 'DML', 'Multiline', 'Wildcard', 'Parenthesis', 'Identifier', 'Where', 'Function', 'Single', 'Operator', 'Integer']
log_likelihoods = []

f = open("training.log")
for line in f:
    sql = line.split('Query')
    if(len(sql)==1):
        continue
    else:
        sql = sql[1].strip()
    res = sqlparse.parse(sql)
    stmt = res[0]
    #repr_name = [ [token._get_repr_name()] for token in stmt.tokens]
    repr_name = [[token_list.index(token._get_repr_name())] for token in stmt.tokens]
    observations.append(repr_name)
    obsrv_lengths.append(len(repr_name))
    #print repr_name
    #w.write( ','.join(repr_name) +"\n")
    #count = count+1

#print observations
#print obsrv_length

observations = np.concatenate(observations)

model = hmm.MultinomialHMM(n_components=20, n_iter=50)
model.fit(observations, obsrv_lengths)  
print [output for output in map(lambda x: token_list[x], model.sample(8)[0])]

f2 = open('sql.log')
for line in f2:
    sql = line.split('\n')[0]
    res = sqlparse.parse(sql)
    stmt = res[0]
    repr_name = [ [token_list.index(token._get_repr_name())] for token in stmt.tokens]
    print repr_name
    log_likelihood = model.score(repr_name)
    print log_likelihood
    log_likelihoods.append(log_likelihood)

threshold = min(log_likelihoods)
model.anomaly_threshold = threshold
w.close
f.close

joblib.dump(model, "sqli-hmm.pkl");
