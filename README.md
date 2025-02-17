# Instructions
## DOCKER 

### DOCKER IMAGE CREATION
```
docker build -t bnnd-wrds-chckr .
```

### DOCKER CONTAINER RUN
```
docker run -it --name wrds-chckr -p 8000:8000 bnnd-wrds-chkr
```

### DOCKER IMAGE STARTING
```
docker start -i wrds-chckr
```

## REQUESTS

### /scan (POST)
#### Body
text - text to scan

return_translation - wether return a tranlsation of the text in case either "there is no banned words" or "there is no bad context"

threshold - the thrashold of triggering in model
```
{
  "text": "string",
  "return_translation": false,
  "threshold": 0.5
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
  ]
}
```
#### Response
```
"'['word1', 'word2']' успішно додано до файлу!"
```

### /remove_banword (POST)
#### Body
```
{
  "words": [
    "string"
  ]
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
## ENVIROMENT 
### **.env file setting example is in dockerfile, all you have to do is to create an empty .env file in repository, then build an image**
