
# functions

## `on(type_: type[Type] | Field)`
used in `QueryRequest` for graphql `on` statement

## `argument(type_: type[Type] | Field, **arguments)`
used in `QueryRequest` for fields that takes argument

## `fragment(name: str, *, on: type[Type] | Field)`
used in `QueryRequest` in the `fragments`

## `fragment_ref(name: str)`
used in `QueryRequest` to reference fragment by name

---

# classes

## `QueryRequest`
the query request object is used by the greff `Client` behind the scenes to
serialize the given query to string

### arguments
 * query - takes a list or query schema
 * fragments - dict of fragments

### `serialize() -> str`
returns the string serialized including fragments

### `serialize_query() -> Iterable[str]`
returns a generator that yields strings

### `serialize_fragments() -> Iterable[str]`
like `serialize_query` but return fragments


## `QueryResponse`
the query response helps creating python objects from graphql response

### arguments
 * response - the graphql dict response

### `@property: response() -> dict[str, Any]`
returns the raw response from graphql with doing anything

### `types() -> tuple[Type, ...]`
returns iterable for each returned type from graphql
```py
response = client.query("""
    query {
        books {
            title
        }
        authors {
            name
        }
    }
""")

books, authors = response.types()
```

### `__iter__() -> Iterable[Type]`
returns an iterable that returns all objects from all types from graphql
