import requests
import pandas as pd
import matplotlib.pyplot as plt
import uuid
pd.options.display.float_format = '${:,.2f}'.format

microstrategy_baseurl = "http://localhost:8080/MicroStrategyLibrary/api/"
microstrategy_user = ""
microstrategy_password = ""
microstrategy_projectid = ""
microstrategy_reportid = ""


def login_microstrategy(base_url,api_login,api_password):
    data_get = {'username': api_login,'password': api_password,'loginMode': 1}
    r = requests.post(base_url + 'auth/login', data=data_get)
    if r.ok:
        authToken = r.headers['X-MSTR-AuthToken']
        cookies = dict(r.cookies)
        print("Token: " + authToken)
        return authToken, cookies
    else:
        print("HTTP %i - %s, Message %s" % (r.status_code, r.reason, r.text))

def get_microstrategy_data():
    token_login,cookies = login_microstrategy(base_url = microstrategy_baseurl, api_login = microstrategy_user, api_password = microstrategy_password)
    headers = {'X-MSTR-AuthToken': token_login, 'Accept': 'application/json', 'Content-Type': 'application/json', 'X-MSTR-ProjectID':microstrategy_projectid}
    r = requests.post(microstrategy_baseurl + 'reports/'+microstrategy_reportid+'/instances?limit=1000',headers=headers , cookies=cookies)
    return r

def parse_microstrategy_data (microstrategy_data,table):
    row = []
    def parseo(microstrategy_data,table):
        if 'children' in microstrategy_data.keys():
            for children in microstrategy_data['children']:
                name = children['element']['name']
                iterator = children['element']['attributeIndex']
                if len(row) >= iterator:
                    del row[iterator:len(row)]
                row.insert(iterator,name.lower()) 
                parseo(microstrategy_data = children,table = table)
        else: 
            for metric in microstrategy_data['metrics']:
                row.append(microstrategy_data['metrics'][metric]['rv']) 
            table.append(row[:])
        return table
    return (parseo(microstrategy_data = microstrategy_data,table = table))


def gen_graph ():
    filename=str(uuid.uuid4())+'.png'
    plt.savefig(filename) 
    plt.close()
    return filename

def only_metrics (metric_asked,table,graph):
    graph_filename = ''
    if graph:
        table[metric_asked].sum().plot(kind='bar').figure
        graph_filename = gen_graph()
    return (table[metric_asked].sum().to_string()), graph_filename

def only_attributes (metric_asked,table,attribute_asked,graph):
    graph_filename = ''
    if graph:
        table.groupby(attribute_asked)[metric_asked].sum().plot(kind='barh',stacked=True).figure.tight_layout()
        ax = plt.gca()
        ax.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: '${:,}'.format(int(x))))
        graph_filename = gen_graph()
    print (table.groupby(attribute_asked)[metric_asked].sum().to_string())
    return (table.groupby(attribute_asked)[metric_asked].sum().to_string()), graph_filename

def only_elements (metric_asked,table,element_asked,graph):
    aux = '=='
    query = ''
    graph_filename = ''
    for keys in element_asked:
        if len(query) == 0:
            query = element_asked[keys] + aux + '\'' + keys + '\''
        else: 
            query=query + ' | ' + element_asked[keys] + aux +'\'' + keys + '\'' 
    if graph:
        table.query(query)[metric_asked].sum().plot(kind='bar')
        graph_filename = gen_graph() 
    return(table.query(query)[metric_asked].sum().to_string()), graph_filename

def attributes_elements (metric_asked,table,element_asked,attribute_asked,graph):
    query = ''
    aux = '=='
    graph_filename = ''
    for keys in element_asked:
        if len(query) == 0:
            query = element_asked[keys] + aux + '\'' + keys + '\''
        else: 
            query=query + ' | ' + element_asked[keys] + aux +'\'' + keys + '\''
    if graph:
        table.query(query).groupby(attribute_asked)[metric_asked].sum().plot(kind='bar').figure
        graph_filename = gen_graph()
    return (table.query(query).groupby(attribute_asked)[metric_asked].sum().to_string()), graph_filename

def get_answer_microstrategy (message,metric_list,attribute_list,table):
    attribute_element = {}
    message=message.lower()
    for atributo in attribute_list:
        for word in table[atributo].unique():
            attribute_element[word.lower()] = atributo
    metric_list = [x.lower() for x in metric_list]
    attribute_list = [x.lower() for x in attribute_list]
    metric_bool = False
    attribute_bool = False
    element_bool = False
    graph_bool = False
    metric_asked = []
    attribute_asked = []
    element_asked = {}

    for item in metric_list:
        if message.find(item) != -1 :
            metric_bool = True
            metric_asked.append(item)
            print ('Metrica detectada')
    for item in attribute_list:
        if message.find(item) != -1 :
            attribute_bool = True
            attribute_asked.append(item)
            print ('Atributo detectado')    
    for item in attribute_element:
        if message.find(item) != -1 :
            element_bool = True
            element_asked[item] = attribute_element[item]
            print ('Elemento detectado')
    for item in ['graph','graphic','plot','grafico','grafica','gráfico','gráfica','image']:
        if message.find(item) != -1 :    
            graph_bool = True
            print ('Gráfico detectado')

    if metric_bool == True: 
        if attribute_bool == False and element_bool == False:
            print ('Solo metricas')
            return only_metrics(metric_asked = metric_asked,table = table,graph = graph_bool)
        if attribute_bool == True and element_bool == False:
            print ('Solo atributos')
            return only_attributes(metric_asked = metric_asked,table = table,attribute_asked = attribute_asked, graph = graph_bool)
        if attribute_bool == True and element_bool == True:
            print ('Atributos filtrados')
            return attributes_elements (metric_asked = metric_asked,table = table,element_asked = element_asked,attribute_asked = attribute_asked, graph = graph_bool)
        if attribute_bool == False and element_bool == True:
            print('Solo filtrado')
            return only_elements(metric_asked = metric_asked,table = table,element_asked = element_asked, graph = graph_bool)
    return '',''

def get_data_microstrategy():
    request = get_microstrategy_data()
    list_atributos = []
    list_metrics = []
    for atributo in request.json()['result']['definition']['attributes']:
       list_atributos.append(atributo['name'].lower())
    for metric in request.json()['result']['definition']['metrics']:
        list_metrics.append(metric['name'].lower())
    data_table = []
    data_table = parse_microstrategy_data(microstrategy_data = request.json()['result']['data']['root'],table = data_table)
    df=pd.DataFrame(data_table, columns=list_atributos + list_metrics)
    return list_metrics,list_atributos,df


if __name__ == '__main__':
    list_metrics,list_atributos,table = get_data_microstrategy()
    test='PROFIT AND REVENUE'
    print(get_answer_microstrategy(message=test,metric_list=list_metrics,attribute_list=list_atributos,table=table))

