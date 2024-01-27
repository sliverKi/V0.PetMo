from elasticsearch import Elasticsearch
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl import analyzer
from django_elasticsearch_dsl import Document as dslDocument, fields
from django_elasticsearch_dsl.registries import registry
from posts.models import Post

nori_analyzer = analyzer(
    'nori_tokenizer',
    tokenizer = 'nori_tokenizer',
)
@registry.register_document
class PostDocument(dslDocument):
    author=fields.ObjectField(
        properties={
            'username':fields.TextField(),
            'profile':fields.TextField(),
            'regionDepth2':fields.TextField(),
            'regionDepth3':fields.TextField(),
        }
    )
    boardAnimalTypes=fields.ObjectField(
        properties={
            "animalTypes": fields.TextField()
        }
    )    
    categoryType=fields.ObjectField(
        properties={
            "categoryType": fields.TextField()
        }
    )
    Image=fields.ObjectField(
        properties={
            "img_path":fields.TextField()
        }
    )
    
    createdDate=fields.DateField()
    updatedDate=fields.DateField()
    viewCount=fields.IntegerField()
    likeCount=fields.IntegerField()
    commentCount=fields.IntegerField()
    bookmarkCount=fields.IntegerField()
    class Index:
        name="search_post_logs"
    class Django:
        model=Post
        fields=["id", "content"]



