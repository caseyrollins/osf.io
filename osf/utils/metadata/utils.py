from website import settings
from website.identifiers.metadata import SUBJECT_SCHEME

def datacite_format_creators_json(contributors):
    creators = []
    for contributor in contributors:
        name_identifiers = [
            {
                'nameIdentifier': contributor.absolute_url,
                'nameIdentifierScheme': 'OSF',
                'schemeURI': settings.DOMAIN
            }
        ]

        if contributor.external_identity.get('ORCID'):
            verified = contributor.external_identity['ORCID'].values()[0] == 'VERIFIED'
            if verified:
                name_identifiers.append({
                    'nameIdentifier': contributor.external_identity['ORCID'].keys()[0],
                    'nameIdentifierScheme': 'ORCID',
                    'schemeURI': 'http://orcid.org/'
                })

        creators.append({
            'creatorName': {
                'creatorName': contributor.fullname,
                'familyName': contributor.family_name,
                'givenName': contributor.given_name
            },
            'nameIdentifiers': name_identifiers
        })

    return creators

def datacite_format_subjects_json(subjects):
    return [
        {
            'subject': subject,
            'subjectScheme': SUBJECT_SCHEME
        }
        for subject in subjects
    ]
