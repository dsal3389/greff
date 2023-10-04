# greff
I wanted an animal name, but most of them already used in pypi :(

## what is it
a class orianted python library to build graphql python client, just build
you class in python, query them, and the library will create the instances of those classes

## current stage
in the current stage its not ready for release, but you can see the `vision` section

## vision / example
```py
import requests
import greff


class ParentAuthor(greff.Type):
    __queryname__ = "authors"

    name: str
    age: int = 0


class Author(ParentAuthor):
    extra_field: str


class SimpleAuthor(ParentAuthor):
    pass


# we implement the graphql posting function ourself
# since it can very from diffrent implementations
def _request_graphql(query) -> dict:
    response = requests.post("http://localhost:8000/graphql", json={"query": query}, verify=False)
    response.raise_for_status()
    return response.json()

# create our charryplate graphql client
graphql = greff.Client(query_request=_request_graphql)

# graphql equivelent
#  {
#   authors {
#     name,
#     __typename
#   }
# }
authors = graphql.query((
    (ParentAuthor, (
        Author.name,
    )),
))

# graphql response 
# {
#   "data": {
#     "authors": [
#       {
#         "name": "Michael Crichton",
#         "__typename": "Author"
#       }
#     ]
#   }
# }
for author in authors:
    print(type(author), author.name)
```

output
```sh
<class '__main__.Author'> Michael Crichton
```

### why did it return `Author` instance and not `ParentAuthor` instance?

if you look closely at the response
```gql
{
  "data": {
    "authors": [
      {
        "name": "Michael Crichton",
        "__typename": "Author"
      }
    ]
  }
}
```

`ParentAuthor` is implementor for `Author` and `SmallAuthor` and in our query the `__typename` 
returned `Author`, so greff automatically created the correct python instace

