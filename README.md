# phpipam Module

## Description

This python package provides the `PhpIpam` class for use to query the phpipam API. This class largely depends on the `requests` module.


## Prerequisites

   ```
   # yum install gcc python-devel python-pip python-requests libffi-devel
   # pip install urllib3 pyopenssl requests[security] --upgrade
   ```

### Notes

* `get_` methods return json objects in general


### Example

Get a list of all subnets and display in "human-readable" json:

```python
from phpipam import PhpIpam
import json

# Create instance
my_session = PhpIpam(ipam_baseurl, ipam_id, ipam_user, ipam_pw, ca_cert)

# Initiate the phpipam session
my_session.connect()

# Run the query and display result to stdout
subnets = my_session.get_subnets()
if subnets:   # Ensures the data is valid
    print json.dumps(json.loads(subnets), indent=4)
else:
    print "No data received"

# Finish the session
ipam.close()
```
