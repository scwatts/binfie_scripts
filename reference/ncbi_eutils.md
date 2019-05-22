# eutils reference
## Purpose
This document aims to serve as a basic reference which briefly describes how to use eutils to process and obtain NCBI data
and records on the command line. The principal reason for querying NCBI databases from the command line is that it allows
rapid prototyping and development of workflows. Many of the eutils programs return only xml, for which I use `xmllint` to
process and capture relevant information via xpath expressions. In cases where you prefer to work with json and the query
return type permits, I recommend using `jq` for process. When working with hundreds or thousands of samples/records and need
to make multiple queries for each (e.g. searching, linking, fetch), I have found saving the results of each step to be very
much worthwhile.

## esearch
I primarily use esearch to obtain the uid of a record from a given accession. In this example, I use esearch to get the uid
of a biosample:
```bash
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?&db=biosample&term=SAMN10748607")
echo "cat //IdList//Id/text()" | xmllint --shell <(echo "${xml_result}") | sed '/\//d'
```

## efetch
To download a record from NCBI (e.g. biosample record), efetch is used:
```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id=SAMN10748607" | xmllint --format -
```
You can use either accession or uid to make efetch queries. Note that efetch is not compatible with all entrez databases but
esummary can sometimes be used instead.

## elink
To find databases which contain records associated with a query or to translate an in uid from one database to another, you
can use elink. Typically you'll want to first check what databases contain records for a given query:
```bash
# Get biosample uid from biosample accession
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?&db=biosample&term=SAMN10748607")
biosample_uid=$(echo "cat //IdList//Id/text()" | xmllint --shell <(echo "${xml_result}") | sed '/\//d')
# Get databases with linking records
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=biosample&id=${biosample_uid}&cmd=acheck")
echo 'cat //LinkInfo/*[self::DbTo]/text()' | xmllint --shell <(echo "${xml_result}") | sed -e '/^\//d' -e '/^ --/d'
```

Once you have a target database, you can get the correct uid (and then use efetch to collect the record itself):
```bash
# Get biosample uid from biosample accession
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?&db=biosample&term=SAMN10748607")
biosample_uid=$(echo "cat //IdList//Id/text()" | xmllint --shell <(echo "${xml_result}") | sed '/\//d')
# Get assembly uid from biosample uid
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=biosample&db=assembly&id=${biosample_uid}")
echo "cat //LinkSetDb//Id/text()" | xmllint --shell <(echo "${xml_result}") | sed '/^\//d'
```

## esummary
As efetch does not support all databases, esummary can be used as a substitute in some cases. For example efetch cannot
retrieve assembly database records but esummary can provide a document summary. Here is an example:
```bash
# Get biosample uid from biosample accession
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?&db=biosample&term=SAMN10748607")
biosample_uid=$(echo "cat //IdList//Id/text()" | xmllint --shell <(echo "${xml_result}") | sed '/\//d')
# Get assembly uid from biosample uid
xml_result=$(curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi?dbfrom=biosample&db=assembly&id=${biosample_uid}")
assembly_uid=$(echo "cat //LinkSetDb//Id/text()" | xmllint --shell <(echo "${xml_result}") | sed '/^\//d')
# Get document summary of assembly record
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=assembly&id=${assembly_uid}" | xmllint --format -
```

## XPath - some hints
### Attribute value selection
In some instances, you'll want select a tag on the basis of an attribute value. For example you want to collect the strain
name from the following XML:
```xml
...
    <Attributes>
      <Attribute attribute_name="lat_lon" harmonized_name="lat_lon" display_name="latitude and longitude">41.90 N 12.50 E</Attribute>
      <Attribute attribute_name="strain" harmonized_name="strain" display_name="strain">RMHi93</Attribute>
      <Attribute attribute_name="host" harmonized_name="host" display_name="host">Homo sapiens</Attribute>
      <Attribute attribute_name="collection_date" harmonized_name="collection_date" display_name="collection date">2012-07-20</Attribute>
      <Attribute attribute_name="pathotype" harmonized_name="pathotype" display_name="pathotype">NTHi</Attribute>
      <Attribute attribute_name="geo_loc_name" harmonized_name="geo_loc_name" display_name="geographic location">Italy: Roma</Attribute>
      <Attribute attribute_name="genotype" harmonized_name="genotype" display_name="genotype">ST-105</Attribute>
      <Attribute attribute_name="isolate" harmonized_name="isolate" display_name="isolate">missing</Attribute>
      <Attribute attribute_name="host_sex" harmonized_name="host_sex" display_name="host sex">female</Attribute>
      <Attribute attribute_name="isolation_source" harmonized_name="isolation_source" display_name="isolation source">oropharynx</Attribute>
      <Attribute attribute_name="collected_by" harmonized_name="collected_by" display_name="collected by">Department of Infectious, Parasitic and Immunomediated Diseases, Istituto Superiore di Sanita, Rome, Italy</Attribute>
      <Attribute attribute_name="host_age" harmonized_name="host_age" display_name="host age">9 months</Attribute>
      <Attribute attribute_name="serotype" harmonized_name="serotype" display_name="serotype">NT</Attribute>
      <Attribute attribute_name="host_disease" harmonized_name="host_disease" display_name="host disease">colonization</Attribute>
    </Attributes>
...
```
This can be done by using conditional attribute selection in XPath:
```bash
echo "cat //Attributes//Attribute[@attribute_name='strain']/text()" | xmllint --shell <(echo "${xml_result}") | sed '/^\//d'
```
Where the attribute selection is made within the `[..]`

## Concurrent requests
Many of the commands show here will benefit from using concurrent processing and can be wrapped in a parallel command:
```bash
mkdir 1_biosample_xml
biosample_accession_list="SAMN10748607 SAMN10748605 SAMN10748603 SAMN10748596 SAMN10748593 SAMN10748588 SAMN10748585"
parallel --jobs 3 'if [[ ! -s 1_biosample_xml/{}.xml ]]; then \
                     curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=biosample&id={}" | xmllint --format - > 1_biosample_xml/{}.xml; \
                   fi' :::: ${biosample_accession_list}
```
