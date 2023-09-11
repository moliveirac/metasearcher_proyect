from django.db import models

# Create your models here.
# class SearchModel(models.Model):
#     DEFAULT = 'TITLE-ABS-KEY'
#     TYPES = [
#         ('TITLE-ABS-KEY', 'Title, Abstracts and Keywords'),
#         ('ALL', 'Search on all fields'),
#         # ('ABS', 'Abstract'),
#         # ('AF-ID', 'Affiliation ID'),
#         ('AFFIL', 'Affiliation'),
#         ('AFFILCITY','Affiliation City'),
#         ('AFFILCOUNTRY','Affiliation Country'),
#         # ('AFFILORG','Affiliation Organization'),
#         # ('ARTNUM', 'Article Number'),
#         ('AU-ID', 'Author Identifier Number'),
#         ('AUTHOR-NAME', 'Author Name'),
#         ('AUTH', 'Author'),
#         # ('AUTHFIRST', 'Author first initial'),
#         # ('AUTHLASTNAME', 'Author last name'),
#         ('AUTHCOLLAB', 'Collaboration Author'),
#         ('CONF', 'Conference'),
#         ('DOI', 'Digital Object Identifier (DOI)'),
#         ('EDITOR', 'Editor'),
#         ('ISBN/ISSN', 'ISBN/ISSN'),
#         # ('LANGUAGE', 'Language'),
#         ('PMID', 'PubMed ID'),
#         ('PUBYEAR', 'Year of Publication'),
#         ('SUBJAREA', 'Source Type'),
#         ('TITLE', 'Article Title')
#     ]
#     BOOLOP = [
#         (None, '---'),
#         ('NOT', 'NOT')
#     ]
#     BOOLOPLINK = [
#         ('AND', 'AND'),
#         ('OR', 'OR'),
#         ('AND NOT', 'AND NOT'),
#         # ('OR NOT', 'OR NOT')
#     ]

#     bool_op = models.CharField(
#         max_length=3,
#         choices=BOOLOP,
#         default=None,
#         blank=True)

#     search_type = models.CharField(
#         max_length=13,
#         choices=TYPES,
#         default=DEFAULT)
    
#     search_keywords = models.CharField(
#         max_length=200)
    
#     bool_op_link = models.CharField(
#         max_length=7,
#         choices=BOOLOPLINK,
#         default='AND')