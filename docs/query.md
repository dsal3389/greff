# query
querying is the most common operation in graphql, `greff` tries to make the querying easy, simullar to
graphql schema and make it programmingly easy to add/remove/modify queries

## TOC
 * [schema](#query-schema)
 * [query operations](#query-operations)
 * [fragments](#fragments)

## query schema
```gql
query {
    books {
        title,
        description
    }
}
```
here is the same query with greff
```py
import greff as ff


class Book(ff.Type): ...


client = ff.Client(...)
books_query = client.query((
    (Book, (
        Book.title,
        Book.description
    ))
))
```
we can see that `client.query` takes a list of lists, each list represent a different type, so here we query `Book` and `People` 

```py
my_query = client.query((
    (Book, (
        Book.tite,
        Book.description
    )),
    (People, (
        People.name,
        People.age
    ))
))
```

#### why is it like this? 
well because it keeps the graphql schema of `type{ ...fields }` and it make it programmically easy to add/remove from query
here is an example
```py
QUERY_BOOKS = False
QUERY_PEOPLE = True


my_query = []


if QUERY_BOOKS:
    books_query = (Book, [
        Book.title,
        Book.description
    ])

    # if we query people we want
    # to query the book author
    if QUERY_PEOPLE:
        books_query[1].append(
            (Book.author, (
                Author.name
            ))
        )
    my_query.append(books_query)
if QUERY_PEOPLE:
    my_query.append(
        (People, (
            People.name,
            People.age
        ))
    )

query = client.query(my_query)
```

## query operations?
`greff` supports the next graphql operations: inline fragments (aka `on`), `fragments` and `arguments` 

the usage is simple, in the case of `arguments` and `on` just wrap your graphql types
with the `argument` or `on` arugment

```py
import greff as ff


class Book(ff.Type): ...
class SmallBook(Book): ...
class BigBook(Book): ...


query = client.query((
    (ff.argument(Book, id=500), (
        Book.title,
        (ff.on(SmallBook), (
            SmallBook.brief
        )),
        (ff.on(BigBook), (
            BigBook.big_description
        ))
    ))
))
```
in this example we added argument `id=500` to the `Book` query, and because `Book` is implementing
both `SmallBook` and `BigBook` we want to get specific types in case we get one of those types

the example query in graphql
```gql
query {
    Book(id: "500") {
        title
        ... on SmallBook {
            brief
        }
        ... on BigBook {
            big_description
        }
    }
}
```

## fragments 
fragments are a way allows us to create a schema once and use it
multiple times in our query, for this, `client.query` takes the `fragments` argument where we define each fragment
and then we reference it in our query with `fragment_ref`

```py
import greff as ff

...

query = client.query((
        (Book, (
            ff.fragment_ref("smlBook"),
            ff.fragment_ref("bigBook")
        ))
    ),
    fragments={
        ff.fragment("smlBook", SmallBook): (
            SmallBook.brief,
        ),
        ff.fragment("bigBook", BigBook): (
            BigBook.big_description
        )
    }
)
```
in this example we defined both `smlBook` on `SmallBook` type and `bigBook` on `BigBook` type, this query in graphql looks like so
```gql
query {
    books {
        ... smlBook
        ... bigBook
    }
}
fragment smlBook on SmallBook {
    brief
}
fragment bigBook on BigBook {
    big_description
}
```

