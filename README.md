# meetperry - Andrew McCarthy takehome

### Running the service
* This is a FastAPI python service.
* You will need a local instance of postgres running.
  * Run the sql queries contained in the `changeset.sql` file to generated the table needed for the service
* I've provided a Docker file to allow you to easily run the service.Run `docker build -t meet-perry .`
to build the image, then run `docker run -p 8000:8000 --env REPORT_INTERVAL_SECONDS=60 meet-perry` to start the service.
  * `REPORT_INTERVAL_SECONDS` is a suggestion.  It should be set to however often you want the report to be generated.
* If Docker fails, you can run `python app.py` to attempt to start the service locally:
  * You will need the libraries contained in `requirements.txt` installed for the app to work.  Also make sure the `DB_HOST` env var is set to `localhost` 

### Env vars
* `HTTP_PORT`: default 8000
* `REPORT_INTERVAL_SECONDS` Refresh interval for the report generation.  Defaulted to 15 seconds
* `DB_HOST` set to `host.docker.internal` to allow the docker contained to connect
* `DB_PORT` default 5432
* `DB_USER` default postgres
* `DB_NAME` default meetperry 

### Structure
* There is a single POST endpoint that accepts the webhook requests:
  * The request body is structured like so, with `WebhookPayload` being the top level request body:
    * ```
        class WebhookMetadata():
            userId: string
            id: string
            content: string
            isCompleted: boolean
        
        class WebhookPayload():
            event: string
            timestamp: string
            metadata: WebhookMetadata
        ```     
* The report generation is run in a background thread and puts the results into a json file.  Each file is structured like so:
  * `task_report_{user_id}_{start_time}_{end_time}.json`
* There is a single db table used for this service, structured like so:
```
CREATE TABLE meetperry.task (
    id BIGSERIAL PRIMARY KEY,
    external_id text NOT NULL UNIQUE,
    user_id text NOT NULL,
    content text NOT NULL,
    completed_date timestamp with time zone NULL,
    deleted_date timestamp with time zone NULL,
    created_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_date timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
```
* The code is divided into the following directories:
  * domain: class definitions for the domain objects
  * exceptions: class definitions for custom exceptions
  * managers: manager classes for handling webhook processing and report generation
  * resources: a customer resource class for managing the Postgres connection
  * routes: the single POST route definition
  * schemas: class definition for the request body
* The top level app.py file contains the app definition as well as the task function for report generation

### Design Discussion
* I assumed the `updated` event is only sent to "complete" a task.  I do not check for updates to the userId or content.
  * Similarly, all the `delete` operation does is add a `deleted_date` field to the db entry.  All records, whether in progress or completed, can be deleted
* I also use the timestamp provided in the webhook when recording created_date, completed_date, and deleted_date.  It may be better to use the time the request is received by the service instead. 
* The reports are inserted into json files automatically.  It would probably make more sense to have a separate endpoint to generate reports based on a user provided date range.
* The "Scheduled job" for this service is a background thread running with a delay.  In a proper production environment, we would want to use something like AWS lambda or Kubernetes cron jobs to ensure more reliability and flexibility.
* The POST webhook endpoint would be best deployed on a cloud hosted kubernetes cluster (or similar)
* I believe most obvious edge cases are handled here.  I created custom exceptions which are caught in the route logic.
  * These include duplicate `create` events for tasks, sending an `update` or `deletion` event before a task is created, and sending an invalid event type
  * Some issues would probably pop up regarding the request structure.  FastAPI does some heavy lifting and enforces the request structure with 422's returned if any parameter types are invalid.  Regardless, I'm sure some 500's could be produced with malformed request bodies.
* In a more built out implementation, we would want GET endpoint(s) to retrieve task information.
* We would also probably want to include more logging and to store each webhook that is sent for auditing purposes.
* It would also be useful to implement materialized views to facilitate data processing and report generation
* Adding additional domain objects would also be very useful
  * Adding a db table for "users", and connecting them to the associated tasks.
* This service would also benefit from some changes to the "TODO" service that sends webhooks:  
  * Having more event types, like `completed`, `content_update`, etc... instead of just `updated`
  * Sending more webhooks for other related objects like the aforementioned "users"
  * Having information be stored in explicit fields instead of all crammed into metadata.
  * Have external endpoints to allow our service to retrieve information about tasks independent of the webhooks

### Testing

* I unfortunately did not have enough time to implement a unit test suite, but I did extensively test the service on my local machine:
  * Send a `created` event and ensure the task is inserted into the db.
    * Send a second `created` event with the same id and ensure a 409 is received
  * Send a `updated` event (with isCompleted set to true) and ensure the task is marked as completed in the db (completed_date set and non-null)
    * Send an `updated` event with a task id that doesn't exist and confirm we receive a 404
  * Send a `deleted` event and ensure the task is marked as deleted (deleted_date set and non-null)
    * Send a `deleted` event with a task id that doesn't exist and confirm we receive a 404
  * Send a nonsense event type and ensure we receive a 400
  * Check to make sure reports are generated for each user on the correct cadence.
    * Make sure each category has the correct number of tasks
    * We create and complete tasks with custom timestamps and ensure they are included in the correct list in each report.