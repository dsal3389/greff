# Client
the client allows `greff` to send and recv information from the graphql backend

## implementation
since graphql client can be different from usage to usage, `greff` does not implement a way to send a 
data to the graphql backend, this should be implemented by the programmer.

because of it `greff` provide an easy way to implement those client behaviours

## dependency injection
`greff` provides a default client that takes 2 arguments
 * `query_request` - callable function that takes a graphql query string and returns graphql response as dict
 * `mutate_request` - same as `query_request` but for mutating data

```py
import requests
import greff


def _request_graphql(query: str) -> dict:
    response = requests.post("http://localhost:8000/graphql", json={"query": query}, verify=False)
    response.raise_for_status()
    return response.json()


graphql_client = greff.Client(query_request=_request_graphql)
```

## class
if you need more control or don't want to pass functions you can implement 
your client with `ClientProtocol` 

```py
import requests
import greff


class MyCustomClient(greff.ClientProtocol):
    def query_request(self, query: str) -> dict:
        response = requests.post("http://localhost:8000/graphql", json={"query": query}, verify=False)
        response.raise_for_status()
        return response.json()
    

client = MyCustomClient()
```
