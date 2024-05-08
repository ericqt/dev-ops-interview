import express from 'express'
import pgp from 'pg-promise'
import cors from 'cors'
import QueryBuilder from './utils/queryBuilder.js'
import fetch from 'node-fetch'

var app = express()
const port = 3000
const db = pgp()("postgres://postgres:postgres@" + process.env.DB_HOST + "/" + process.env.DB_NAME) // TODO: Ideally user, pw, and port are passed from env as well

app.use(express.json())
app.use(cors())

const RANDOM_USER_URL = 'https://randomuser.me/api/'
const FETCH_LIMIT = 5000 

app.get('/test', (req, res) => {
    const { limit, starting_after, ending_before, email } = req.query
    const emailFmt = email?.trim().toLowerCase().replace(/'/g, "''")

    // Request query validation
    if (parseInt(isNaN(limit)) || parseInt(limit) > 100 || parseInt(limit) < 0 || parseInt(isNaN(starting_after)) || parseInt(isNaN(ending_before)) ) {
        res.sendStatus(400)
        return
    }

    const queryStr = QueryBuilder.getClerksQuery({ limit, starting_after, ending_before, email: emailFmt })

    db.query(queryStr)
        .then(out => res.send(out))
        .catch(err => {
            console.log(err)
            res.sendStatus(500)
        })
})

// For each user, store their name, email, phone number, picture, and registration date.
// TODO: Run batches async maybe, probably not since that would assume truely random results per batch.
// TODO: Maybe use paging? Probably not since the current batch size is so low. 
app.post('/populate', (req, res) => {
    fetch(RANDOM_USER_URL + "?results=" + FETCH_LIMIT, { method: 'GET' })
        .then(res => res.json())
        .then(jsonData => {
            const queryStr = QueryBuilder.populateClerksQuery(jsonData.results)

            db.query(queryStr)
                .then(() => res.sendStatus(200))
                .catch(e => {
                    console.log(e)
                    res.sendStatus(500)
                })
        })
        .catch(err => console.error('error:' + err))
})

app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
})
