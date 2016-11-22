# p3s examples

The files name "job_template*" are meant to be used with the script
like "job" in the p3pilot directory, which interact with the server.
They allow the user to inject the database with multiple job
definitions at once, from a single file. The syntax is currently:
`
python3 job.py -j mytemplates.json
`

The template file is supposed to represent a JSON list.
