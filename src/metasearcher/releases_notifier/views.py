from django.shortcuts import render, redirect
import traceback
from django.contrib import messages
from .models import QuerySavedModel, UserQueryModel
from my_utils.utils import *
from urllib.parse import unquote
import requests

LOGIN_NEEDED = "User not logged in. Redirected to login page. Please log in first to user the notifier application!"

# Create your views here.
def main_page(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user

            objects_list = QuerySavedModel.objects.filter(users=user)

            return render(request, 'releases_notifier/index.html', 
                        {
                            'objects_list': objects_list,
                            'app': 'rns'
                        })
        else:
            messages.error(request, (LOGIN_NEEDED))
            return redirect('members:login')
    
def save_query(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            query = request.GET.get('query')
            source = request.GET.get('source')
            last_id = request.GET.get('id')
            user = request.user

            if source == None:
                auxquery = request.GET.get('auxquery')
                auxid = request.GET.get('auxid')


            try:
                qs_object = QuerySavedModel.objects.filter(query=query)

                if qs_object.count() == 0:
                    if source == None:
                        qs_object = QuerySavedModel(query=query, source='scopus', last_result=last_id)
                    else:
                        qs_object = QuerySavedModel(query=query, source=source, last_result=last_id)
                    qs_object.save()

                elif qs_object.count() == 1:
                    qs_object = QuerySavedModel.objects.get(query=query)
                    if qs_object.last_result != last_id:
                        qs_object.last_result = last_id
                        qs_object.save()
                else:
                    raise Exception('More than 1 object with the same query is stored on database')

                qs_object.users.add(user)

                # save last result seen for user
                uq_object = UserQueryModel.objects.get(query_id = qs_object.pk, user_id = user.id)
                uq_object.last_result_seen = last_id
                uq_object.save()

                message = "Query saved successfully!"


                if source == None:
                    qs_object = QuerySavedModel.objects.filter(query=auxquery)

                    if qs_object.count() == 0:
                        qs_object = QuerySavedModel(query=auxquery, source='clarivate', last_result=auxid)
                        qs_object.save()

                    elif qs_object.count() == 1:
                        qs_object = QuerySavedModel.objects.get(query=auxquery)
                        if qs_object.last_result != auxid:
                            qs_object.last_result = auxid
                            qs_object.save()
                    else:
                        raise Exception('More than 1 object with the same query is stored on database')

                    qs_object.users.add(user)

                    # save last result seen for user
                    uq_object = UserQueryModel.objects.get(query_id = qs_object.pk, user_id = user.id)
                    uq_object.last_result_seen = auxid
                    uq_object.save()

                    message = "Queries saved successfully!"

                # qs_object.save()
            except:
                traceback.print_exc()
                message = "Query not saved: Something failed, please try again."

            return render(request, 'releases_notifier/save_query.html', 
                {
                    'message': message,
                        'app': 'rns'
                })
            
        else: 
            messages.error(request, (LOGIN_NEEDED))
            return redirect('members:login')
        

def delete_query(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            pk = request.GET.get('query')
            user = request.user

            try:
                qs_object = QuerySavedModel.objects.get(pk=pk)

                if user in qs_object.users.all():
                    qs_object.users.remove(user)
                    # qs_object.save()
                else:
                    print("Error")
                    return

                if not qs_object.users.all():
                    qs_object.delete()

                message="Query deleted succesfuly from your saved queries."

            except:
                message="Error"

        else:
            messages.error(request, (LOGIN_NEEDED))
            return redirect('members:login')

    return render(request, 'releases_notifier/save_query.html', 
               {
                   'message': message,
                    'app': 'rns'
               })

def search_saved_query(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            # Control vars
            fail = False
            error_message = None
            query = unquote(request.GET.get('query'))
            database = request.GET.get('source')

            qs_object = QuerySavedModel.objects.get(query=query)
            
            if qs_object and request.user in qs_object.users.all():
                try:
                    results = search_docs({database: query}, "-orig-load-date", database, cursor="*")

                    if not results.results_df.empty:
                        # result updated and consulted this week
                        qs_object.last_result = results.results_df['ids'][0]
                        qs_object.save()

                        # result consulted by this user
                        qs_user = UserQueryModel.objects.get(query=qs_object, user=request.user)
                        qs_user.last_result_seen = results.results_df['ids'][0]
                        qs_user.save()


                except requests.HTTPError as e:
                    fail = True
                    results = empty_results()
                    error_message = "API " + str(e)[:14] + ". Please check out if your query is correct."
                    
                return render(request, 'searcher/saved_query_results.html', 
                            {
                                'results': results.results_df,
                                'cursor': results.cursor, 
                                'fail': fail,
                                'error_message': error_message,
                                #   'order': order,
                                #   'clarivate': database == 'clarivate',
                                'query': results.query,
                                'app': 'simple_search',
                                'total_results': results.total_results
                            })
            
            else:
                messages.error(request, ("You're not allowed to consult this query. Please save it first!"))
                return redirect('releases_notifier:index')
        else:
            messages.error(request, (LOGIN_NEEDED))
            return redirect('members:login')