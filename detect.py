import sqlparse
from elasticsearch import Elasticsearch
import numpy as np
#from hmmlearn import hmm
from sklearn.externals import joblib

token_list =  ['Comparison', 'Punctuation', 'Whitespace', 'Keyword', 'IdentifierList', 'DML', 'Multiline', 'Wildcard', 'Parenthesis', 'Identifier', 'Where', 'Function', 'Single', 'Operator', 'Integer']
log_likelihoods = []
es_host = "127.0.0.1"
es_port = "9200"
logs_index = "logs"
attack_query = []
model = joblib.load("sqli-hmm.pkl");

es = Elasticsearch([{'host': es_host, 'port':es_port}])

sql_log_query = {
  "query":{
    "bool":{
      "must":[
        {
          "match_all":{}
          },
        {
          "range":{
            "@timestamp":{
              "lte":"now",
              "gte":"now-1m"
              }
            }
          }
        ]
      }
    }
  }

logs_count = es.count(index=logs_index, doc_type=['mysql-general'],
    body=sql_log_query)['count']
print(logs_count)

results = es.search(index=logs_index, doc_type=['mysql-general'],
    size=logs_count ,body=sql_log_query)['hits']['hits']

results = [result['_source'] for result in results]

#detect sql injection
i = 0
for result in results:
    if 'stmt' in result and result['command'] == "Query":
      res = sqlparse.parse(result['stmt'])
    stmt = res[0]
    #repr_name = [ [token._get_repr_name()] for token in stmt.tokens]
    repr_name = [[token_list.index(token._get_repr_name())] for token in stmt.tokens]
    if model.score(repr_name) < model.anomaly_threshold:
      sql_find_attack_query = {
          "query":{
            "bool":{
              "must":[
                {
                  "term":{ "cid" : result['cid'] }
                },
                {
                  "match":{ "command" : "Connect" }
                },
                {
                  "range":{
                    "@timestamp":{
                      "lte" : result['@timestamp']
                     }
                   }
                }
                ]
              }
            }
          }
      attacked_host = es.search(index=logs_index, doc_type=['mysql-general'],
          body=sql_find_attack_query)['hits']['hits'][0]
      print(attacked_host)
      print(attacked_host['_source']['stmt'])
      attack_query.append({'dst_host': attacked_host['_source']['stmt'], 'injection_statement' : result['stmt'],
          "@timestamp":result['@timestamp']})
      print(attack_query)
      
for attack in attack_query:
  es.index(index="attack", doc_type="sqli", body=attack)
