import pandas as pd
import requests
import json
from tqdm import tqdm
from typing import List, Dict
from stqdm import stqdm

def get_abstract(abstract: Dict) -> str:
    if abstract:
        a ={}
        for key, value in abstract.items():
            for i in value:
                a[i] = key

        a_keys = list(a.keys())
        a_keys.sort()
        sorted_a = {i: a[i] for i in a_keys}
        return ' '.join(list(sorted_a.values()))
    else:
        return ''

def clean_authorships(authorships: List) -> Dict:
    new_authorships = {}
    new_authorships['authors_display_names'] = ';'.join([i['author']['display_name'] for i in authorships])
    new_authorships['authors_display_orcid'] = ';'.join([i['author']['orcid'] for i in authorships if i['author']['orcid']])
    new_authorships['number_of_authors'] = len(new_authorships['authors_display_names'].split(';'))

    all_affiliations = []
    for aff in authorships:
        if len(aff['institutions']) > 0:
            all_affiliations = all_affiliations + [i['display_name'] for i in aff['institutions']]

    new_authorships['clean_institutions'] = all_affiliations

    new_authorships['authors_unique_number_of_affiliations'] = len(set(new_authorships['clean_institutions']))
    new_authorships['authors_unique_affiliations'] = list(set(new_authorships['clean_institutions']))

    return new_authorships

def get_oa_record(doi) -> pd.DataFrame:
    r = requests.get(f'https://api.openalex.org/works/https://doi.org/{doi}')
    response = json.loads(r.text)

    # Fix abstract
    response['abstract'] = get_abstract(response['abstract_inverted_index'])
    response.pop('abstract_inverted_index')

    # Fix author columns
    response.update(clean_authorships(response['authorships']))
    
    # Fix DOI
    response['DOI'] = response['doi'][16:]

    return pd.json_normalize(response)

def getOAdata(init_df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for doi in stqdm(init_df['DOI'].tolist()):
        records.append(
            get_oa_record(doi)
        )

    return pd.concat(records)
