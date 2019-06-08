# The Static Collector
--
The static collector is the simplest of PyPlow collector.It is incredibly scalable by leveraging the cdn of the cloud providers

## How it works, in a nutshell

The PyPlow tracking pixel is served from Cloudfront. The SnowPlow tracker requests the pixel (using a `GET`), and appends the data to be logged in PyPlow in the query string for the `GET` request.

AWS Cloudfront: the request (incl. the query string) gets logged to S3 including some additional data provided by Cloudfront. (E.g. requester IP address and URL.) These can then be parsed by the ETL module.

GCP Cloud CDN: the request (incl. the query string) gets logged to Stackdriver including some additional data provided by Google Cloud Loadbalancer. (E.g. requester IP address and URL.) These can then be parsed by the ETL module.
