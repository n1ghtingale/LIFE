import sqlparse
import numpy as np
#from hmmlearn import hmm
from sklearn.externals import joblib

log_likelihoods = []
es_host = "127.0.0.1"
es_port = "9200"
logs_index = "logs"
attack_query = []
model = joblib.load("sqli-hmm-bee.pkl");
#load token list from model
token_list = model.token_list
f = open("slide-injection-log")
for line in f:
    res = sqlparse.parse(line.strip())
    stmt = res[0]

    #flattening where clause
    where_token = None
    idx = -1
    while True:
        where_token = stmt.token_next_by_instance(idx, sqlparse.sql.Where)
        if not where_token:
            break
        idx = stmt.token_index(where_token)+1
        stmt.tokens += list(where_token.flatten())
        del stmt.tokens[idx]
    #print list(stmt.flatten())
    try:
        repr_name = [[token_list.index(token._get_repr_name())] for token in stmt.tokens if token._get_repr_name() !='Whitespace']
    except ValueError:
        repr_name = [[token_list.index(token._get_repr_name())] for token in stmt.tokens if token._get_repr_name() in token_list
                        and token._get_repr_name() != 'Whitespace']
        print "unseen token found"
            

    print stmt.tokens

#detect sql injection
    if model.score(repr_name) < model.anomaly_threshold:
        print model.score(repr_name)
        for token in stmt.tokens:
            print token._get_repr_name(),
        print "\nabnormal"
    else:
        print model.score(repr_name)
        for token in stmt.tokens:
            print token._get_repr_name(),
        print '\nnormal'
