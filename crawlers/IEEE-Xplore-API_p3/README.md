# (Official documentation) IEEE Xplore API

Search Parameters: https://developer.ieee.org/docs/read/Metadata_API_details

Data Fields Returned: https://developer.ieee.org/docs/read/Metadata_API_responses

Python (2.7) SDK: https://developer.ieee.org/Python_Software_Development_Kit

Due to problems giving Error 400 when calling maximumResults and startingResult, these methods have been modified in xploreapi.py

IEEE Xplore API limits to 25 results per query by default, and can be set to 200 maximum.


# Setup

In the root path of this repository:
	
	virtualenv -p python venv
	source venv/bin/activate
	pip install -r requirements.txt

note that:

	source venv/bin/activate

should be executed at first on every usage session, except when using an IDE (such as PyCharm) and environment is pre-configured.


# Usage example

This code (main.py) requires a txt file named "key.txt" containing in the first (and only) line the API Key obtained at https://developer.ieee.org/member/register

Creates (with Pandas) 'queries.csv' containing search history about past queries with , whose identification number (e.g. 0) is related with the corresponding filename containing results from that query for a given year (e.g. Query_0-year.csv).
CSV is separated with commas (",").


ISSN and Author-Terms are not available for every article.

Execute passing two arguments --datafield query_text --year 20xx, such as
**python main.py --year 2017 --publication_title IEEE International Conference on Development and Learning and Epigenetic Robotics**

This would generate files as described above, searching 'IEEE International Conference on Development and Learning and Epigenetic Robotics' for Publication Title and filtering results according to conference on the given year.

**Note**: execution may crush if a given article lacks of parameters values being saved
