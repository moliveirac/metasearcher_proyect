import pandas as pd
import traceback
import base64
import requests
from django.shortcuts import render, redirect
from django.forms import formset_factory, modelformset_factory
from .forms import SearchForm, AdvancedSearchForm, FirstAdvancedSearchForm, OrderResultsForm, SearcherForm
# from .models import SearchModel
from my_utils.utils import *
from urllib.parse import unquote


# Views

def index(request):
    """Principal view for simple keyword search"""

    form = SearchForm()

    return render(request, 'searcher/search.html', 
                  {
                      'form': form,
                      'app': 'simple_search'
                   })


def search_view(request):
    """Results for simple search"""

    if request.GET.get('search_keys') != None:
        # Control vars
        fail = False
        error_message = None
        keywords = request.GET.get('search_keys')
        order_type = request.GET.get('order_type')
        database = request.GET.get('searcher')

        if order_type == '+score' and database == 'clarivate':
            order_type = '-score'

        # Forms
        form = SearchForm({'search_keys': keywords})
        order = OrderResultsForm({'order_type':order_type})
        searcher = SearcherForm({'searcher':database})

        # Validation
        if not order.is_valid():
            order_type = '-orig-load-date'
            order = OrderResultsForm({'order_type':order_type})

        if not searcher.is_valid() or database == None:
            database = 'scopus'
            searcher = SearcherForm({'searcher':database})

        try:
            search_dict = request_to_dict(keywords)
            search_dict = query_builder(search_dict)
            results = search_docs(search_dict, order_type, database, cursor="*")

        except ValueError as e:
            fail = True
            results = empty_results()
            error_message = str(e) + "."

        except requests.HTTPError as e:
            fail = True
            results = empty_results()
            error_message = "API " + str(e)[:14] + ". Please check out if your query is correct."

        if database == 'mix':
            return render(request, 'searcher/search_mix_results.html', 
                      {
                          'keywords': keywords, 
                          'form': form, 
                          'results': results.results_df,
                          'cursor': results.cursor, 
                          'fail': fail,
                          'error_message': error_message,
                          'order': order,
                          'searcher': searcher,
                          'clarivate': True,
                          'query': results.query,
                          'app': 'simple_search',
                          'total_results': results.total_results
                      })
            
        return render(request, 'searcher/search_results.html', 
                      {
                          'keywords': keywords, 
                          'form': form, 
                          'results': results.results_df,
                          'cursor': results.cursor, 
                          'fail': fail,
                          'error_message': error_message,
                          'order': order,
                          'searcher': searcher,
                          'clarivate': database == 'clarivate',
                          'query': results.query,
                          'app': 'simple_search',
                          'total_results': results.total_results
                      })

    else:
        return redirect('searcher:index')


def advanced_search_index(request):
    """Principal view for advanced search"""
    
    # AdvancedSearchFormSet = modelformset_factory(SearchModel, form=AdvancedSearchForm, extra=1)
    AdvancedSearchFormSet = formset_factory(AdvancedSearchForm, extra=1)

    first_form = FirstAdvancedSearchForm()
    formset = formset_required_fields(AdvancedSearchFormSet)
    
    return render(request, 'searcher/adv_search.html',
                      {
                          'formset': formset, 
                          'first_form': first_form,
                          'app': 'advanced_search'
                       })


def advanced_search_view(request):
    """Results advanced search view"""

    if request.method == 'POST':
        fail = False
        error_message = None
        order_type = request.POST.get('order_type')
        database = request.POST.get('searcher')

        if order_type == '+score' and database == 'clarivate':
            order_type = '-score'

        # AdvancedSearchFormSet = modelformset_factory(SearchModel, form=AdvancedSearchForm, extra=1)
        AdvancedSearchFormSet = formset_factory(AdvancedSearchForm, extra=1)
        first_form = FirstAdvancedSearchForm(request.POST)
        formset = formset_required_fields(AdvancedSearchFormSet, request)
        order = OrderResultsForm({'order_type':order_type})
        searcher = SearcherForm({'searcher':database})

        if not searcher.is_valid() or database == None:
            database = 'scopus'
            searcher = SearcherForm({'searcher':database})

        if not all([first_form.is_valid(), formset.is_valid(), order.is_valid()]):
            fail = True
            results = empty_results()
            error_message = "Query parameters not allowed. Check if your query is correct."

        else:
            search_dict = request_to_dict(first_form, formset)
            search_dict = query_builder(search_dict)

            try:
                results = search_docs(search_dict, order_type, database, cursor="*")

            except ValueError as e:
                fail = True
                results = empty_results()
                if DEBUG:
                    print(str(e))
                error_message = str(e) + "."

            except requests.HTTPError as e:
                fail = True
                results = empty_results()
                if DEBUG:
                    print(str(e))
                error_message = "API " + str(e)[:14] + ". Please check out if your query is correct."

        if database == 'mix':
            return render(request, 'searcher/adv_search_mix_results.html', 
                      {
                          'first_form': first_form,
                          'keywords': results.query, 
                          'formset': formset,
                          'results': results.results_df,
                          'cursor': results.cursor, 
                          'fail': fail,
                          'error_message': error_message,
                          'order': order,
                          'searcher': searcher,
                          'clarivate': True,
                          'query': results.query['scopus'],
                          'auxquery': results.query['clarivate'],
                          'app': 'advanced_search',
                          'total_results': results.total_results
                      })

        return render(request, 'searcher/adv_search_results.html', 
                        {
                            'first_form': first_form,
                            'keywords': results.query, 
                            'formset': formset, 
                            'results': results.results_df,
                            'cursor': results.cursor,
                            'fail': fail,
                            'error_message': error_message,
                            'order': order,
                            'searcher': searcher,
                            'clarivate': database == 'clarivate',
                            'query': results.query,
                            'app': 'advanced_search',
                            'total_results': results.total_results
                        })
        
        # elif (form := SearchForm(request.POST)).is_valid():
        #     keywords = form.cleaned_data.get('search_keys')
            
        #     return render(request, 'searcher/search_results.html', 
        #                   {'keywords': keywords, 'form': form, 
        #                    'results': search_docs(keywords)})
            
            
    else:
        return redirect('searcher:adv_index')


def detail_view(request):
    """Detailed view for documents"""

    if request.method == 'GET':
        doc_id = request.GET.get('id')
        origin = request.GET.get('origin')
        form = SearchForm(request.GET)
        try:
            data = detail_doc(doc_id, origin)
            # print(data)
        except:
            traceback.print_exc()
            return render(request, 'searcher/404.html')
        
        if origin == 'Clarivate':
            return render(request, 'searcher/clarivate_detail_result.html',
                  {
                      'doc': data,
                      'app': None
                   })
        elif origin == 'Scopus':
            return render(request, 'searcher/scopus_detail_result.html',
                  {
                      'doc': data,
                      'app': None
                   })


def next_cursor_page(request):
    
    if request.method == 'GET':
        query = unquote(request.GET.get('query'))
        sort_type = unquote(request.GET.get('order_type'))
        database = unquote(request.GET.get('searcher'))
        cursor = base64.b64decode(
            unquote(request.GET.get('cursor')).encode('ascii')
            ).decode('ascii')
        try:
            next_value = int(request.GET.get('next'))
        except:
            next_value = 0

        query_dict = {database: query}
        results = search_docs(query_dict, sort_type, database, cursor=cursor)

        return render(request, 'searcher/cursor_results.html', 
                      {
                          'results': results.results_df,
                          'cursor': results.cursor,
                          'query': query,
                          'sort_type': sort_type,
                          'searcher': database,
                          'next_value': next_value
                      })


def send_query(request):
    if request.method == 'GET':
        query = unquote(request.GET.get('query'))
        database = request.GET.get('source')

        if database == "mix":
            # aux query
            auxquery = unquote(request.GET.get('auxquery'))

            scopus_result = get_recent_result({'scopus': query}, 'scopus')
            wos_result = get_recent_result({'clarivate': auxquery}, 'clarivate')

            return render(request, 'searcher/last_published_result_mix.html',
                  {
                      'query': query, 
                      'auxquery': auxquery,
                      'database': database,
                      'scopus_result_name': scopus_result[0],
                      'scopus_id': scopus_result[1],
                      'wos_result_name': wos_result[0],
                      'wos_id': wos_result[1],
                  })

        else:
            result = get_recent_result({database: query}, database)

            return render(request, 'searcher/last_published_result.html',
                  {
                      'query': query, 
                      'database': database,
                      'result_name': result[0],
                      'id': result[1]
                  })
        


def get_recent_result(query_dict, database):
    try: 
        results = search_docs(query_dict, "-orig-load-date", database)

        if results.total_results == 0:
            result_name = "There are no results nowadays... Are you sure you want to save this query?"
            result_id = None
        else:
            result_name = results.results_df['title'][0] + " (" + results.results_df['ids'][0] + ")"
            result_id = results.results_df['ids'][0]
    except Exception as e:
        traceback.print_exc()
        result_name = "There was an error with your request, please reload the page."
        result_id = None


    return (result_name, result_id)

    