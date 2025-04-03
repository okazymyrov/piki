# GET a JSON file
```js
fetch('https://[domain]/api/id')
  .then(res => res.json())
  .then(console.log)
```

# POST
```js
fetch('https://[domain]/api/id', {
  method: 'POST',
  body: JSON.stringify({
    title: 'Name',
    body: 'Surname',
    userId: 2
  }),
  headers: {
    'Content-type': 'application/json; charset=UTF-8'
  }
})
.then(res => res.json())
.then(console.log)
```
