# iflow1

**SAP CPI iFlow Technical Documentation: iflow1**

### Purpose
The purpose of iflow1 is to integrate with external systems to retrieve data, perform processing, and send the results to a target system. This iFlow enables real-time data exchange and synchronization between the sender and receiver systems, ensuring data consistency and accuracy.

### Sender / Receiver
* **Sender:** External REST API (https://external-api.com/data)
* **Receiver:** SAP S/4HANA Cloud System (https://s4hana-system.com/api)

### Adapters
* **Sender Adapter:** HTTP Adapter with JSON Payload
	+ Protocol: HTTP
	+ Method: GET
	+ URL: https://external-api.com/data
	+ Authentication: Basic Authentication with username and password
* **Receiver Adapter:** HTTP Adapter with JSON Payload
	+ Protocol: HTTP
	+ Method: POST
	+ URL: https://s4hana-system.com/api
	+ Authentication: OAuth 2.0 with client credentials

### Flow Logic
The iflow1 consists of the following steps:

1. **Receiver Determination:** Determine the receiver system based on the incoming message.
2. **Data Retrieval:** Send a GET request to the external REST API to retrieve the required data.
3. **Data Mapping:** Map the retrieved data to the target system's format using a Groovy script.
4. **Data Validation:** Validate the mapped data against the target system's schema.
5. **Data Processing:** Perform additional processing on the validated data, such as data transformation and calculation.
6. **Data Sending:** Send the processed data to the target system using the HTTP adapter.

### Error Handling
Error handling in iflow1 is implemented as follows:

* **Error Occurrence:** If an error occurs during the execution of the iFlow, the error is caught and logged.
* **Error Logging:** Errors are logged with the following details:
	+ Error message
	+ Error code
	+ Step where the error occurred
	+ Payload details
* **Error Notification:** In case of an error, a notification is sent to the support team via email with the error details.
* **Retry Mechanism:** The iFlow has a retry mechanism in place, which retries the failed step up to 3 times with a delay of 5 minutes between each retry.
* **Error Threshold:** If the error threshold is exceeded (i.e., more than 5 errors occur within a 1-hour window), the iFlow is suspended, and a notification is sent to the support team.

**Example Error Handling Scenarios:**

* **HTTP Error (4xx/5xx):** If an HTTP error occurs during the data retrieval or sending steps, the error is logged, and the iFlow is retried.
* **Data Validation Error:** If the data validation step fails, the error is logged, and the iFlow is terminated.
* **Groovy Script Error:** If an error occurs during the execution of the Groovy script, the error is logged, and the iFlow is terminated.

By following this technical documentation, the iflow1 ensures reliable and efficient integration between the external systems and the SAP S/4HANA Cloud system, with robust error handling and notification mechanisms in place.