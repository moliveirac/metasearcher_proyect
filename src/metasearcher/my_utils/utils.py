import pandas as pd
import base64, json, requests, time, types
import numpy as np
import traceback
from urllib.parse import quote_plus as url_encode
from pandas import DataFrame

from elsapy.elssearch import ElsSearch
from elsapy.elsclient import ElsClient
from elsapy.elsdoc import AbsDoc
from elsapy.utils import recast_df
from elsapy import log_util


logger = log_util.get_logger(__name__)
DEBUG = True
PROXY = True
SCOPUS_KEY = "insert_SCOPUS_KEY"
WOS_KEY = "insert_WOS_KEY"

class ResultsClass:
    """A class that includes everything about search results"""

    _results_df = None
    _cursor = None
    _query = None

    def __init__(self, results_df, query, total_results=0):
        self._results_df = results_df
        self._query = query
        self._total_results = total_results
        self._cursor = None
        # self._next_elem = None

    @property
    def cursor(self):
        return self._cursor
    @cursor.setter
    def cursor(self, cursor):
        self._cursor = cursor

    @property
    def results_df(self):
        return self._results_df
    
    @property
    def total_pages(self):
        return self._pages
    
    @property
    def total_results(self):
        return self._total_results
    @total_results.setter
    def total_results(self, total_results):
        self._total_results = total_results

    # @property
    # def next_elem(self):
    #     return self._next_elem
    # @next_elem.setter
    # def next_elem(self, next_elem):
    #     self._next_elem = next_elem
    
    @property
    def query(self):
        return self._query

# AUX FUNCTIONS
def empty_results():
    return ResultsClass(DataFrame([]), 0, "")

def init_client():
    return ElsClient("--insertar-API-key")

def formset_required_fields(FormSetClass, request=None):
    
    if request != None:
        formset = FormSetClass(request.POST, request.FILES)
    else: 
        formset = FormSetClass()
    for form in formset:
        form.use_required_attribute = True

    formset.empty_form.use_required_attribute = True

    return formset

def request_to_dict(first_form, formset = None):

    if formset == None:
        return {'keywords': [first_form], 'search_type': ['TITLE-ABS-KEY'], 'bool_op': ['']}

    keywords = [first_form.cleaned_data.get('search_keywords')]
    search_type = [first_form.cleaned_data.get('search_type')]
    bool_op = [first_form.cleaned_data.get('bool_op')]

    for x in formset.cleaned_data:
        bool_op.append(x.get('bool_op_link'))
        search_type.append(x.get('search_type'))
        keywords.append(x.get('search_keywords'))

    return {'keywords': keywords, 'search_type': search_type, 'bool_op': bool_op}

def query_builder(search_dict: dict):
    """Transforms user's search parameters into a search query for Scopus"""

    # Check if both have same length
    if len(search_dict['search_type']) != len(search_dict['keywords']) != len(search_dict['bool_op']):
        raise ValueError("The number of query elements in the dictionary varies")

    scopus_search_string = ""
    clarivate_search_string = ""
    query_results_dict = {}

    clarivate_search_types = wos_search_types(search_dict['search_type'])

    for x in range(len(search_dict['search_type'])):
        op_conn = None
        aux = ''
        match search_dict['bool_op'][x]:
            case "AND": 
                op_conn = ' AND '
            case "AND NOT":
                op_conn = ' AND '
                aux = 'NOT '
            case "OR":
                op_conn = ' OR '
            ### TODO: compatibilidad
            # case "NOT":
            #     search_string = "not"
            case "OR NOT":
                op_conn = ' OR '
                aux = 'NOT '
            case _:
                op_conn = ''
        
        if search_dict['search_type'][x] == "ISBN/ISSN":
            scopus_search_string += op_conn + aux + '( ISBN (' + search_dict['keywords'][x] + ') OR ISSN (' + search_dict['keywords'][x] + ') )'
        else:
            scopus_search_string = scopus_search_string + op_conn + aux + search_dict['search_type'][x] + '(' + search_dict['keywords'][x] + ')'

        if clarivate_search_types[x] == "OG/OO":
            clarivate_search_string += op_conn + '( OG=(' + aux + search_dict['keywords'][x] + ') OR OO=(' + aux + search_dict['keywords'][x] + ') )'
        elif clarivate_search_types[x] == "LANG":
            query_results_dict['LANG'] = search_dict['keywords'][x]
        else:
            clarivate_search_string = clarivate_search_string + op_conn + clarivate_search_types[x] + '=("' + aux + search_dict['keywords'][x] + '")'

    query_results_dict['scopus'] = scopus_search_string
    query_results_dict['clarivate'] = clarivate_search_string
    return query_results_dict

def translate_sort(scopus_sort: str):
    if not isinstance(scopus_sort, str):
        raise TypeError

    match scopus_sort[0]:
        case '-':
            order = "+D" 
        case '+':
            order = "+A"
        case _:
            raise KeyError(scopus_sort)

    match scopus_sort[1:]:
        case 'score':
            if order == "+A":
                raise ValueError(scopus_sort)
            sort_type = "RS"
        case 'creator':
            sort_type = "AU"
        case 'pagefirst':
            sort_type = "PG"
        case 'pubyear':
            sort_type = "PY"
        case 'citedby-count':
            sort_type = "LC"
        case 'volume':
            sort_type = "VL"
        case 'orig-load-date':
            sort_type = "LD"
        case _:
            raise KeyError(scopus_sort)
        
    return sort_type + order

# Search docs
def search_docs(search_dict: dict, sort: str, searcher: str, cursor: str = None):
    searcher_values = ['clarivate', 'scopus', 'mix']
    language = None

    if sort == "":
        sort = None
   
    if search_dict != None:

        if searcher not in searcher_values:
            raise KeyError(searcher)
    
        if searcher == 'clarivate':
            page_size = 25
            query = search_dict['clarivate']

            if sort != None:
                sort = translate_sort(sort)

            if 'LANG' in search_dict:
                language = search_dict['LANG']
                if query == '':
                    raise ValueError("You can't search only by language on Web of Science")

            if cursor not in [None, '*']:
                results_dict = wos_search(query, sort, int(cursor), page_size, language=language)
            else:
                results_dict = wos_search(query, sort, 1, page_size, language=language)

        elif searcher == 'scopus':
            query = search_dict['scopus']
            results_dict = scopus_search(query, sort, cursor)

        elif searcher == 'mix':
            results_dict = mix_results(search_dict, sort)
            query = search_dict
    
    elif cursor != None:
        results_dict = scopus_search(None, None, cursor)
        query = None

    results = ResultsClass(results_dict['results_df'], query, results_dict['tot_num_res'])
    
    if 'cursor' in results_dict and results_dict['cursor'] != None:
        results.cursor = base64.b64encode(results_dict['cursor'].encode('ascii')).decode('ascii')

    if 'next' in results_dict and results_dict['next'] != None:
        results.cursor = base64.b64encode(str(results_dict['next']).encode('ascii')).decode('ascii')

    return results

# Scopus
def scopus_search(keywords: str, sort: str, cursor: str = None, page: int = 0):
    """Search documents with scopus"""

    client = init_client()
    page_size = 25
    end = False
    base_url = u'https://api.elsevier.com/content/search/scopus'

    client.exec_request_w_proxy = types.MethodType(exec_request_w_proxy, client)

    if cursor == '*':
        uri = base_url + '?query=' + url_encode(keywords) + '&cursor=' + cursor + '&view=COMPLETE'
        
        if sort != None or sort == "":
            uri += '&sort=' + url_encode(sort)

    elif cursor != None:
        uri = base_url + '?' + cursor

    else:
        uri = base_url + '?query=' + url_encode(keywords) + '&count=' + str(page_size) + '&start=' + str(page*page_size) + '&view=COMPLETE'
        
        if sort != None or sort == "":
            uri += '&sort=' + url_encode(sort)

    if DEBUG:
        print(uri)

    if PROXY:
        response = client.exec_request_w_proxy(URL=uri, proxy_dict=dict(http='socks5h://host.docker.internal:1080', https='socks5h://host.docker.internal:1080'))
    else:
        response = client.exec_request(uri)

    if DEBUG:
        with open('dump.json', 'w') as f:
            f.write(json.dumps(response))
    
    tot_num_res = int(response['search-results']['opensearch:totalResults'])

    # Check if not last page
    if cursor != None and response['search-results']['cursor']['@current'] != response['search-results']['cursor']['@next']:
        
        results = response['search-results']['entry']

    elif cursor == None:

        results = response['search-results']['entry']

    else:
        
        results = []
        end = True
        if DEBUG:
            print("Last page")
    
    results_df = scopus_df(pd.DataFrame(results))

    if cursor != None:

        new_cursor = None

        for link_dict in response['search-results']['link']:
            if 'next' in link_dict.values() and not end:
                new_cursor = link_dict['@href'].split('scopus?')[1]

        return {'results_df': results_df, 
                'tot_num_res': tot_num_res, 
                'cursor': new_cursor
                }
    
    else:

        return {'results_df': results_df, 
                'tot_num_res': 5000 if tot_num_res > 5000 else tot_num_res
                }

def detail_doc(s_id, origin):
    """Gets document details"""

    if origin == 'Scopus':
        client = init_client()

        if PROXY:
            try:
                client.exec_request_w_proxy = types.MethodType(exec_request_w_proxy, client)
                data = client.exec_request_w_proxy(URL='https://api.elsevier.com/content/abstract/scopus_id/' + s_id + '?view=FULL', proxy_dict=dict(http='socks5h://host.docker.internal:1080', https='socks5h://host.docker.internal:1080'))
                data = data['abstracts-retrieval-response']
            except:
                traceback.print_exc()
                return None
        
        else:
            try:
                data = client.exec_request(URL='https://api.elsevier.com/content/abstract/scopus_id/' + s_id + '?view=FULL')
                data = data['abstracts-retrieval-response']
            except:
                traceback.print_exc()
                return None

            # doc = AbsDoc(uri='https://api.elsevier.com/content/abstract/scopus_id/' + s_id + '?view=FULL')

            # if doc.read(client):
            #     data = doc.data
            #     print(data)
            # else:
            #     return None

    elif origin == 'Clarivate':
        doc = wos_search_request('UT=(' + s_id + ')', None, links=True)

        if doc['QueryResult']['RecordsFound'] != 0:
            data = doc['Data']['Records']['records']['REC'][0]
        else:
            return None
    else:
        raise ValueError(s_id, origin)

    return data

def scopus_df(results_df: DataFrame):

    results_df = recast_df(results_df)

    if 'error' in results_df:
        raise ValueError()
    if results_df.empty:
        return results_df
    # Get titles
    title_series = results_df["dc:title"].rename("title")

    # Get links
    links = results_df["link"].rename("link")

    # Get ID 
    doc_id = results_df["dc:identifier"].rename("ids")

    # Get DOI
    doi_id = results_df["prism:doi"].rename("doi")

    # Get author
    if "dc:creator" in results_df:
        creator = results_df["dc:creator"].rename("author")
    else:
        creator =  pd.Series("", index = np.arange(len(results_df)), name="author")

    # Get Date
    date = results_df["prism:coverDisplayDate"].str[-4:].rename("date")

    # Get load Date
    load_date = results_df["prism:coverDate"].rename("load_date")

    # Get publication-related
    subtype = results_df["subtypeDescription"].rename("type")
    
    pub_name = results_df["prism:publicationName"].rename("publisher")

    cited_by = results_df["citedby-count"].rename("cited_by")

    if "prism:volume" in results_df:
        volume = results_df["prism:volume"].rename("volume")
    else:
        volume =  pd.Series(np.nan, index = np.arange(len(results_df)), name="volume")

    if "prism:pageRange" in results_df:
        page_range = results_df["prism:pageRange"].rename("page_range")
    else:
        page_range = pd.Series(np.nan, index = np.arange(len(results_df)), name="page_range")

    origin = pd.Series('Scopus', index = np.arange(len(results_df)), name='origin')
    
    # Get abstracts
    # client = init_client()
    # abstracts = []
    # for i in range(0, len(results_df.index)):
    #     abstr = AbsDoc(uri=links[i]['self'])
    #     abstr.read(client)
    #     abstracts.append(abstr.data['coredata']['dc:description'])

    res_form = pd.concat(
        [title_series, links, doc_id,
         #pd.Series(abstracts, name='description')
         creator, date, subtype, pub_name,
         cited_by, volume, page_range, origin, doi_id, load_date], axis=1)
        

    return res_form
    
# WoS
def wos_search(keywords, sort, next_doc: int = 1, page_size: int = 25, language: str = None):
    
    response = wos_search_request(keywords, sort, start_at=next_doc, page_size=page_size, language=language)

    tot_num_res = int(response['QueryResult']['RecordsFound'])

    if tot_num_res != 0:
        results = response['Data']['Records']['records']['REC']
    else:
        results={}

    results_df = wos_df(results)

    return_dict = {'results_df': results_df,
            'tot_num_res': tot_num_res}
    
    if tot_num_res >= next_doc + page_size:
        return_dict['next'] = next_doc + page_size

    return return_dict

def wos_df(results_dict):
    """Returns a df with the data exposed on the web app from a list of wos results"""
    
    if results_dict == {}:
        return DataFrame([])

    df = pd.json_normalize(results_dict)

    # Doc. name + Id
    author_list = []
    title_list = []
    pub_list = []
    doi_list = []
    for x in results_dict:
        if x['static_data']['summary']['names']['count'] > 1:
            row = x['static_data']['summary']['names']['name'][0]
            row['UID'] = x['UID']
            author_list.append(row)
        else:
            if type(x['static_data']['summary']['names']['name']) == list:
                row = x['static_data']['summary']['names']['name'][0]
            else:
                 row = x['static_data']['summary']['names']['name']
            row['UID'] = x['UID']
            author_list.append(row)

        title_row = {}
        pub_row = {}
        if x['static_data']['summary']['titles']['count'] > 1:
            for y in x['static_data']['summary']['titles']['title']:
                if y['type'] == 'item':
                    title_row = y    
                elif y['type'] == 'source':
                    pub_row = y
        else:
            if x['static_data']['summary']['titles']['title']['type'] == 'item':
                title_row = x['static_data']['summary']['titles']['title']
            elif x['static_data']['summary']['titles']['title']['type'] == 'item':
                pub_row = x['static_data']['summary']['titles']['title']

        title_row['UID'] = x['UID']
        pub_row['UID'] = x['UID']
        title_list.append(title_row)
        pub_list.append(pub_row)

        if 'cluster_related' in x['dynamic_data']:
            if type(x['dynamic_data']['cluster_related']['identifiers']['identifier']) == list:
                for identifier_obj in x['dynamic_data']['cluster_related']['identifiers']['identifier']:
                    id_value = np.nan
                    if identifier_obj['type'] == 'doi':
                        id_value = identifier_obj['value']
                        break
                doi_list.append(id_value)
            else:
                if x['dynamic_data']['cluster_related']['identifiers']['identifier']['type'] == 'doi':
                    doi_list.append(x['dynamic_data']['cluster_related']['identifiers']['identifier']['value'])
                else:
                    doi_list.append(np.nan)

    author_df = pd.DataFrame(author_list)
    title_df = pd.DataFrame(title_list)
    pub_name_df = pd.DataFrame(pub_list)


    # translation_df = pd.json_normalize(
    #     results_dict, # dict['Data']['Records']['records']['REC']
    #     record_path=['static_data','summary','titles','title'], 
    #     meta=['UID'])
    
    # title_df = translation_df[translation_df['type'] == 'item'].rename(
    #     columns={'content':'title'}).drop(['type'], axis=1)
    
    # # Publisher name
    # pub_name_df = translation_df[translation_df['type'] == 'source'].rename(
    #     columns={'content':'publisher'}).drop(['type'], axis=1)

    title_df = title_df.rename(
        columns={'content':'title'}).drop(['type'], axis=1)
    
    pub_name_df = pub_name_df.rename(
        columns={'content':'publisher'}).drop(['type'], axis=1)
    
    title_df = pd.merge(title_df, pub_name_df, how='inner', on='UID')
    if 'translated' in title_df.columns:
        title_df.drop(['translated'], inplace=True)

    # Author name (first only)

    # Check if its a list (count > 1)
    # author_df = pd.json_normalize(results_dict,
    #                   record_path=['static_data', 'summary', 'names', 'name'],
    #                   meta=['UID'], errors='ignore')
    author_df = author_df[author_df['seq_no'] == 1].rename(columns={'full_name':'author'})[['UID', 'author']]
        
    results_df = pd.merge(title_df, author_df, how='inner', on='UID')
    results_df['doi'] = doi_list

    df.rename(
        columns={
            'static_data.summary.doctypes.doctype': 'type', 
            'static_data.summary.pub_info.pubyear': 'date', 
            'dynamic_data.citation_related.tc_list.silo_tc.local_count': 'cited_by',
            'static_data.summary.pub_info.vol': 'volume',
            'static_data.summary.pub_info.page.content': 'page_range',
            'dates.date_loaded': 'load_date'
            }, inplace=True)
    
    df['date'] = df['date'].astype(str)
    df['load_date'] = pd.to_datetime(df['load_date'][:9])

    if 'volume' not in df.columns:
        df['volume'] = pd.Series(np.nan, index = np.arange(len(df)), name='volume')

    if 'page_range' not in df.columns:
        df['page_range'] = pd.Series(np.nan, index = np.arange(len(df)), name='page_range')

    df['volume'] = df['volume'].astype('Int64').astype(str)

    df['type'] = df['type'].apply(lambda x : x[0] if type(x) == list else x)
    df['origin'] = pd.Series('Clarivate', index = np.arange(len(df)), name='origin')

    return pd.merge(df[['UID', 'type', 'date', 'cited_by', 'volume', 'page_range', 'origin', 'load_date']], results_df, how='inner', on='UID').rename(columns={'UID':'ids'})

def wos_search_request(keywords, sort_field: str = None, links: bool = False, start_at: int=1, page_size: int = 25, language: str = None):
    wos_url = "https://wos-api.clarivate.com/api/wos"
    params = {
        "databaseId": "WOK",
        "usrQuery": keywords,
        "count": page_size,
        "firstRecord": start_at,
    }

    if sort_field != None and sort_field != "":
        params['sortField'] = sort_field

    if links:
        params['links'] = 'true'

    if language != None:
        params['lang'] = language

    headers = {
        "X-ApiKey": WOS_KEY 
    }

    if PROXY:
        response = requests.get(wos_url,
                            params=params,
                            headers=headers,
                            proxies=dict(http='socks5h://host.docker.internal:1080', 
                                         https='socks5h://host.docker.internal:1080')
                            )
    else:
        response = requests.get(wos_url,
                            params=params,
                            headers=headers)
    
    if DEBUG:
        print(response.url)
    
    # return response.json()['Data']['Records']['records']['rec']
    if response.ok:
        return response.json()

    else:
        raise requests.HTTPError("HTTP " + str(response.status_code) + " Error from " + wos_url + "\nand using headers " + str(headers) + ":\n" + response.text)

def wos_search_types(search_type_list):
    op_list = []

    for search_type in search_type_list:
        match search_type:
            case "ALL" | "TITLE-ABS-KEY":
                op_list.append('TS')
            case "AFFIL":
                op_list.append('OG/OO')
            case "AFFILCITY":
                op_list.append('CI')
            case "AFFILCOUNTRY":
                op_list.append('CU')
            case "AU-ID":
                op_list.append('AI')
            case "AUTHOR-NAME":
                op_list.append('AU')
            case "AUTH":
                op_list.append('AU')
            case "AUTHCOLLAB":
                op_list.append('GP')
            case "DOI":
                op_list.append('DO')
            case "EDITOR":
                op_list.append('ED')
            case "LANGUAGE":
                op_list.append('LANG')
                # TODO
            case "PUBYEAR":
                op_list.append('PY')
            case "SUBJAREA":
                op_list.append('WC/SU')
            case "TITLE":
                op_list.append('TI')
        
    return op_list

def get_all_scopus_results(keywords: str, sort: str, max_results: int = 250):
    results_dict = scopus_search(keywords, sort, page = 0)
    
    df = results_dict['results_df']

    results_limit = min(results_dict['tot_num_res'],max_results)
    actual_page = 1

    while len(df) < results_limit:
        results_dict = scopus_search(keywords, sort, page = actual_page)

        new_df = results_dict['results_df']
        df = pd.concat([df, new_df], ignore_index=True)
        actual_page += 1

    return df

def get_all_clarivate_results(keywords: str, sort: str, max_results: int = 250):
    results_dict = wos_search(keywords, sort, page_size=100)
    
    df = results_dict['results_df']

    results_limit = min(results_dict['tot_num_res'],max_results)

    while len(df) < results_limit:
        results_dict = wos_search(keywords, sort, next_doc=results_dict['next'], page_size=100)

        new_df = results_dict['results_df']

        if 'results_df' in results_dict:
            df = pd.concat([df, new_df], ignore_index=True)

    return df

def exec_request_w_proxy(self, URL, proxy_dict):
    """Sends the actual request; returns response. 
    This is a copy of the original exec_request from Elsapy adapted for the use of proxys."""
    
    ## Construct and execute request
    headers = {
        "X-ELS-APIKey"  : self.api_key,
        # "User-Agent"    : self.__user_agent,
        "Accept"        : 'application/json'
        }
    if self.inst_token:
        headers["X-ELS-Insttoken"] = self.inst_token
    logger.info('Sending GET request to ' + URL)
    r = requests.get(
        URL,
        headers = headers,
        proxies=proxy_dict
        )
    
    if r.status_code == 200:
        self._status_msg='data retrieved'
        return json.loads(r.text)
    else:
        self._status_msg="HTTP " + str(r.status_code) + " Error from " + URL + " and using headers " + str(headers) + ": " + r.text
        raise requests.HTTPError("HTTP " + str(r.status_code) + " Error from " + URL + "\nand using headers " + str(headers) + ":\n" + r.text)

# mix results
def mix_results(queries: list, sort: str):
    sort_prefix = sort[0]
    sort_suffix = sort[1:]

    scopus_search_df = get_all_scopus_results(queries['scopus'], sort, max_results=100)
    
    sort = translate_sort(sort)
    clarivate_search_df = get_all_clarivate_results(queries['clarivate'], sort, max_results=100)

    scopus_search_df.dropna(subset=['doi'], ignore_index=True, inplace=True)
    clarivate_search_df.dropna(subset=['doi'], ignore_index=True, inplace=True)

    scopus_search_df['score_scopus'] = scopus_search_df.index
    clarivate_search_df['score_clarivate'] = clarivate_search_df.index
    search_df = pd.merge(scopus_search_df, clarivate_search_df, left_on=[scopus_search_df['doi']], right_on=[clarivate_search_df['doi']], how='outer', suffixes=['_scopus', '_clarivate'])

    match sort_suffix:
        case "score":
            search_df['score'] = search_df.apply(lambda row: 
                                row['score_scopus'] if (row['score_scopus'] is not pd.NaT or row['score_scopus'] < row['score_clarivate']) else row['score_clarivate'], axis=1)
            
            search_df.sort_values('score', ascending=(sort_prefix == '+'), inplace=True, ignore_index=True)

        case "citedby-count":
            search_df['cited_by'] = search_df.apply(lambda row: 
                                row['cited_by_scopus'] if (row['cited_by_scopus'] is not pd.NaT or row['cited_by_scopus'] < row['cited_by_clarivate']) else row['cited_by_clarivate'], axis=1)
            
            search_df.sort_values('cited_by', ascending=(sort_prefix == '+'), inplace=True, ignore_index=True)

        case "pubyear":
            search_df['date'] = search_df.apply(lambda row: 
                                row['date_scopus'] if (row['date_scopus'] is not pd.NaT or row['date_scopus'] < row['date_clarivate']) else row['date_clarivate'], axis=1)
            
            search_df.sort_values('date', ascending=(sort_prefix == '+'), inplace=True, ignore_index=True)

        case "creator":
            search_df['author'] = search_df.apply(lambda row: 
                                row['author_scopus'] if (row['author_scopus'] is not pd.NaT or row['author_scopus'] > row['author_clarivate']) else row['author_clarivate'], axis=1)
            
            search_df.sort_values('author', ascending=(sort_prefix == '+'), inplace=True, ignore_index=True)

        case "orig-load-date":
            search_df['load_date'] = search_df.apply(lambda row: 
                                row['load_date_scopus'] if (row['load_date_scopus'] is not pd.NaT or row['load_date_scopus'] < row['load_date_clarivate']) else row['load_date_clarivate'], axis=1)
            
            search_df.sort_values('load_date', ascending=(sort_prefix == '+'), inplace=True, ignore_index=True)

    return {'results_df': search_df, 'tot_num_res': len(search_df)}