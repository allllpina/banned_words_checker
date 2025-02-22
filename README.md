# Instructions
## DOCKER 

### DOCKER IMAGE CREATION
```
docker build -t bnnd-wrds-chckr .
```

### DOCKER CONTAINER RUN
```
docker run -it --name wrds-chckr -p 8000:8000 bnnd-wrds-chckr
```

### DOCKER IMAGE STARTING
```
docker start -i wrds-chckr
```

## REQUESTS

### /scan (POST)
#### Body
__text__ - text to scan

__language__ - text language

__return_translation__ - whether return a translation of the text in case either "there is no banned words" or "there is no bad context"

__threshold__ - the threshold of triggering in model

__database__ - name of database file

```
{
  "text": "string",
  "language": "string",
  "return_translation": false,
  "threshold": 0.5,
  "database": "string"
}
```
#### Response
```
# In case of bad context
{
  "message": [
    {
      "word": "kill",
      "context": "kill him",
      "reason": [
        "violence"
      ]
    }
  ]
}
# In case of either no bad context or bad words
{
  "message": "There is no banned words"
}
```
### /add_banword (POST)
#### Body
```
{
  "words": [
    "string"
  ],
  "database_name": "string"
}
```
#### Response
```
{
    "added": [
       "word1",
       "word2"
    ],
    "skipped":  [
       "word3",
       "word4"
    ]
}
```

### /remove_banword (POST)
#### Body
```
{
  "words": [
    "string"
  ],
  "database_name": "string"
}
```
#### Response
```
{
  "removed": [
    "good",
    "hello",
  ],
  "not_found": [
    "love"
  ]
}
```
### /get_banwords (GET)
#### Parameters

__database_name__ _string_ (query)

#### Response
```
{
  'length': "string",
  "words": [
    "word1",
	"word2"
  ]
}
```
### /create_database (POST)
#### Body
```
{
  "database_name": "string"
}
```
#### Response
```
{
  "result": "Database 'Lima' successfully created!"
}
```
### /delete_database (POST)
#### Body
```
{
  "database_name": "string"
}
```
#### Response
```
{
  "result": "Database 'Lima' successfully deleted!"
}
```
### /get_databases (GET)
#### Parameters
_None_
#### Response
```
{
  "databases": [
    "database1",
    "database2
  ]
}
```
## ENVIROMENT 
### **.env file setting example is in dockerfile, all you have to do is to create an empty .env file in repository, then build an image**
