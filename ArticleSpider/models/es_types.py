from elasticsearch_dsl import Keyword, Text, Integer, Document, Completion
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["localhost"])


class LkPersonType(Document):
    suggest = Completion(analyzer="ik_smart")
    # id = Keyword()
    # parent_id = Keyword()
    url = Keyword()
    name = Text(analyzer="ik_smart")
    occupation = Text(analyzer="ik_smart")
    location = Text(analyzer="ik_smart")
    photo_url = Keyword()
    photo_path = Keyword()
    gender = Keyword()
    beauty_score = Integer()
    summary = Text(analyzer="ik_smart")
    company_exp = Text(analyzer="ik_smart")
    company_jobexp = Text(analyzer="ik_smart")
    school_exp = Text(analyzer="ik_smart")

    class Index:
        name = "lnkn"
        settings = {
            "number_of_shards": 1,
            "number_of_replicas": 0,
        }



if __name__ == "__main__":
    LkPersonType.init()
