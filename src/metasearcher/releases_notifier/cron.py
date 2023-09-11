from my_utils.utils import *
from my_utils.mail import *
from .models import QuerySavedModel, UserQueryModel
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import time
import pytz


def notify_users():
    all_queries = QuerySavedModel.objects.all()
    updated_queries_pk = []

    if all_queries.count() == 0:

        return
    
    else:
        for query_obj in all_queries:

            # check when was last update
            last_update_was = datetime.now(pytz.utc) - query_obj.updated_on

            # if less than a week check if new results are subbmitted
            if last_update_was > timedelta(days=7):
                results = search_docs({query_obj.source: query_obj.query}, "-orig-load-date", query_obj.source, cursor="*")
                # wait to not pass the limit per second
                time.sleep(5)
                if query_obj.last_result != results.results_df['ids'][0]:
                    query_obj.last_result = results.results_df['ids'][0]
                    query_obj.save()
                    updated_queries_pk.append(query_obj.pk)

            # else, add it too
            else:
                updated_queries_pk.append(query_obj.pk)
        
        # get all users with the queries updated
        users_to_notify = User.objects.filter(userquerymodel__query__in=updated_queries_pk)

        # notify each user with its updated queries
        for actual_user in users_to_notify:
            
            user_queries_to_notify = QuerySavedModel.objects.filter(userquerymodel__user=actual_user).filter(pk__in = updated_queries_pk)
            queries_list = []

            for query_to_notify in user_queries_to_notify:
                uq_object = UserQueryModel.objects.get(query=query_to_notify, user=actual_user)
                
                # check if user got this results
                if query_to_notify.last_result != uq_object.last_result_seen:
                    queries_list.append((query_to_notify.source, query_to_notify.query))
                    uq_object.notified = True
                    uq_object.save()

            if len(queries_list) != 0:
                notify_new_results(actual_user.first_name + " " + actual_user.last_name, queries_list, actual_user.email)

            