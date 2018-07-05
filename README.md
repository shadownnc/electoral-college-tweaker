# electoral-college-tweaker
Explore different scenarios of allocating electoral votes with historical data.

* **elect_tweaker/data:** JSON data files of each election year with popular vote tallies and percentages by state.
* **elect_tweaker/elect_data.py:** methods to parse HTML from Wikipedia and turn into JSON data.
* **elect_tweaker/elect_tweaker.py:** methods to run heuristics on the data.
* **data_output.py:** methods to print data in a spreadsheet format.
* **tweaker.py:** main script to bring it all together.

You can also view the [Google Sheet](https://docs.google.com/spreadsheets/d/1zsSVJHqwbWQbSdmC7vHewGqJtYN6k2-8SGmk42r8M6s/edit?usp=sharing) where the results for proportional allocation were first tested and analyzed.

## Winner Take All Discrepancies

There are several instances where the actual results had a discrepancy with winner take all, generally on the margin. These are not represented in the data files, but are notated below:

* 1880:
  * CA: 1 electoral vote went to James Garfield.
* 1892:
  * CA: 1 electoral vote went to Benjamin Harrison.
  * MI: 5 electoral votes went to Grover Cleveland.
  * ND: 3 electoral votes were split between Grover Cleveland, Benjamin Harrison, and James Weaver.
  * OH: 1 electoral vote went to Grover Cleveland.
  * OR: 1 electoral vote went to James Weaver.
* 1896:
  * CA: 1 electoral vote went to William Jennings Bryan.
  * KY: 1 electoral vote went to William Jennings Bryan.
* 1904:
  * MD: 1 electoral vote went to Theodore Roosevelt.
* 1908:
  * MD: 2 electoral votes went to William Howard Taft.
* 1912:
  * CA: 2 electoral votes went to Woodrow Wilson.
* 1916:
  * WV: 1 electoral vote went to Woodrow Wilson.
* 1948:
  * TN: 1 electoral vote went to J. Strom Thurmond.
* 1960:
  * AL: 6 unpledged electors
  * MS: 8 unpledged electors
  * OK: 1 unpledged elector
* 1972:
  * VA: 1 faithless electoral vote went to John Hospers.
* 2012:
  * ME: Congressional district electoral votes (2) all went to Barack Obama.
  * NE: Congressional district electoral votes (3) all went to Mitt Romney.
* 2016:
  * ME: Congressional district electoral votes (2) split between Hillary Clinton and Donald Trump.
  * NE: Congressional district electoral votes (3) all went to Donald Trump

## Python Libraries

* lxml
* requests