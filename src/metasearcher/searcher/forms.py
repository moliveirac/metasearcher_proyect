from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper, Layout
from crispy_forms.layout import *
from crispy_forms.bootstrap import *
from crispy_bootstrap5.bootstrap5 import *

# from . import models

class SearchForm(forms.Form):
    search_keys = forms.CharField(label=False, required=True)

    helper = FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.layout = Layout(
        Column(
            Field('search_keys', placeholder='Insert search terms...'), 
            css_class='form-group'
        )
    )
# class AdvancedSearchForm(forms.Form):
#     search_type = forms.ChoiceField(choices=models.SearchField.TYPES, required=True)
#     search_keys = forms.CharField(label='Insert search terms', required=True)

# class FirstAdvancedSearchForm(forms.ModelForm):
#     class Meta:
#         model = models.SearchModel
#         fields = [
#             # 'bool_op',
#             'search_type', 
#             'search_keywords']
#         labels= {
#             # 'bool_op':"Boolean operator",
#             'search_type':"Search type", 
#             'search_keywords':"Keywords"
#         }
        
#     helper = FormHelper()
#     helper.form_tag = False
#     helper.disable_csrf = True
#     helper.layout = Layout(
#         Row(
#             # Column(
#             #     FloatingField('bool_op'), 
#             #     css_class='form-group col-lg-3 col-6'
#             # ),
#             Column(
#                 FloatingField('search_type'), 
#                 css_class='form-group col-xl-5 col'
#             ),
#             Column(
#                 FloatingField('search_keywords'),
#                 css_class="col-xl"
#             ),
#         ),
#     )

class FirstAdvancedSearchForm(forms.Form):
    TYPES = [
        ('TITLE-ABS-KEY', 'Title, Abstracts and Keywords'),
        ('ALL', 'Search on all fields'),
        # ('ABS', 'Abstract'),
        # ('AF-ID', 'Affiliation ID'),
        ('AFFIL', 'Affiliation'),
        ('AFFILCITY','Affiliation City'),
        ('AFFILCOUNTRY','Affiliation Country'),
        # ('AFFILORG','Affiliation Organization'),
        # ('ARTNUM', 'Article Number'),
        ('AU-ID', 'Author Identifier Number'),
        ('AUTHOR-NAME', 'Author Name'),
        ('AUTH', 'Author'),
        # ('AUTHFIRST', 'Author first initial'),
        # ('AUTHLASTNAME', 'Author last name'),
        ('AUTHCOLLAB', 'Collaboration Author'),
        ('CONF', 'Conference'),
        ('DOI', 'Digital Object Identifier (DOI)'),
        ('EDITOR', 'Editor'),
        ('ISBN/ISSN', 'ISBN/ISSN'),
        # ('LANGUAGE', 'Language'),
        ('PMID', 'PubMed ID'),
        ('PUBYEAR', 'Year of Publication'),
        ('SUBJAREA', 'Source Type'),
        ('TITLE', 'Article Title')
    ]

    search_type = forms.ChoiceField(
        choices=TYPES,
        label="Search type",
        required=True,
    )
    search_keywords = forms.CharField(
        label="Keywords",
        required=True,
        max_length=200,
    )

    helper = FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.layout = Layout(
        Row(
            # Column(
            #     FloatingField('bool_op'), 
            #     css_class='form-group col-lg-3 col-6'
            # ),
            Column(
                FloatingField('search_type'), 
                css_class='form-group col-xl-5 col'
            ),
            Column(
                FloatingField('search_keywords'),
                css_class="col-xl"
            ),
        ),
    )

class AdvancedSearchForm(FirstAdvancedSearchForm):
    BOOLOPLINK = [
        ('AND', 'AND'),
        ('OR', 'OR'),
        ('AND NOT', 'AND NOT'),
        # ('OR NOT', 'OR NOT')
    ]

    bool_op_link = forms.ChoiceField(
        choices=BOOLOPLINK,
        label="Boolean nexus",
        required=True,
    )

    helper = FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.layout = Layout(
        Row(
            Column(
                FloatingField('bool_op_link'), 
                css_class='form-group col-xl-2 col-4'
            ),
            Column(
                FloatingField('search_type'), 
                css_class='form-group col-xl-3 col-8'),
            Column(
                Row(
                    Column(FloatingField('search_keywords'),
                           css_class='col'),
                    Column(Button(
                        'del-btn', 
                        'Delete', 
                        css_class='btn-danger del-btn',
                        onclick="delete_form(this)", 
                        id="del-btn"),
                        css_class='col-auto mb-3 d-grid'
                    )
                )
            )
                 
                ,
            # Column(
            #     Button('del-btn', 'Delete', css_class='btn-danger del-btn', onclick="delete_form(this)", 
            #            id="del-btn"
            #            ),
            #     css_class='col-auto' 
            # ),
        ),
    )

# class AdvancedSearchForm(forms.ModelForm):
#     class Meta:
#         model = models.SearchModel
#         fields = ['bool_op_link', 'search_type', 'search_keywords']
#         labels= {
#             'bool_op_link':"Boolean nexus",
#             'search_type':"Search type", 
#             'search_keywords':"Keywords"
#         }
        
#     helper = FormHelper()
#     helper.form_tag = False
#     helper.disable_csrf = True
#     helper.layout = Layout(
#         Row(
#             Column(
#                 FloatingField('bool_op_link'), 
#                 css_class='form-group col-xl-2 col-4'
#             ),
#             Column(
#                 FloatingField('search_type'), 
#                 css_class='form-group col-xl-3 col-8'),
#             Column(
#                 Row(
#                     Column(FloatingField('search_keywords'),
#                            css_class='col'),
#                     Column(Button(
#                         'del-btn', 
#                         'Delete', 
#                         css_class='btn-danger del-btn',
#                         onclick="delete_form(this)", 
#                         id="del-btn"),
#                         css_class='col-auto mb-3 d-grid'
#                     )
#                 )
#             )
                 
#                 ,
#             # Column(
#             #     Button('del-btn', 'Delete', css_class='btn-danger del-btn', onclick="delete_form(this)", 
#             #            id="del-btn"
#             #            ),
#             #     css_class='col-auto' 
#             # ),
#         ),
#     )

class OrderResultsForm(forms.Form):
    ORDER_OPTIONS = [
        ('-orig-load-date', 'Load Date (Newest)'),
        ('+orig-load-date', 'Load Date (Oldest)'),
        ('-score', 'Relevance (Highest)'),
        ('+score', 'Relevance (Lowest)'),
        # ('-pagecount', 'Number of Pages (Highest)'),
        # ('+pagecount', 'Number of Pages (Lowest)'),
        ('+creator', 'Head author (A-Z)'),
        ('-creator', 'Head author (Z-A)'),
        # ('-pagefirst', 'First page number (Highest)'),
        # ('+pagefirst', 'First page number (Lowest)'),
        ('-pubyear', 'Publication Year (Newest)'),
        ('+pubyear', 'Publication Year (oldest)'),
        ('-citedby-count', 'Times Cited (Highest)'),
        ('+citedby-count', 'Times Cited (Lowest)'),
        # ('-volume', 'Volume Number (Highest)'),
        # ('+volume', 'Volume Number (Lowest)'),
    ]
    order_type = forms.ChoiceField(
        choices=ORDER_OPTIONS,
        label="Order by:",
        required=False,
    )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_tag = False
    helper.disable_csrf = True
    helper.label_class = 'col-auto'
    helper.field_class = 'col'
    helper.layout = Layout(
        Field('order_type', onChange="this.form.submit()"),
    )

class SearcherForm(forms.Form):
    SEARCHER_OPTIONS = [
        ('scopus', 'Scopus'),
        ('clarivate', 'Web of Science'),
        ('mix', 'Mix results')
    ]

    searcher = forms.ChoiceField(
        choices=SEARCHER_OPTIONS,
        label="Search in:",
        required=False,
    )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.form_tag = False
    helper.disable_csrf = True
    helper.label_class = 'col-auto'
    helper.field_class = 'col'
    helper.layout = Layout(
        Field('searcher', onChange="this.form.submit()"),
    )