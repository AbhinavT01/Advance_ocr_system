patterns = {
    'DOB': (
        r'(?i)(?:D\.?O\.?B\.?|D[0O]B|Date\s*of\s*Birth)\s*[:\s]*'
        r'('
        r'\d{2}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2,4}|'
        r'\d{4}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2}|'
        r'\d{2}[-/.\s]{0,3}(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2,4}|'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2}[-/.\s]{0,3},?[-/.\s]{0,3}\d{2,4}'
        r')'
    ),

    'Expiry Date': (
        r'(?i)(?:4b\s)?(?:EXP(?:IR(?:ES|Y DATE)?|IRY DATE|IRE[SD])?)[:\s]*'
        r'('
        r'\d{2}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2,4}|'
        r'\d{4}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2}|'
        r'\d{2}[-/.\s]{0,3}(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2,4}|'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2}[-/.\s]{0,3},?[-/.\s]{0,3}\d{2,4}'
        r')'
    ),

    'Issue Date': (
        r'(?i)(?:ISSU[EA]D|ISS)[:;\s]*'
        r'('
        r'\d{2}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2,4}|'
        r'\d{4}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2}|'
        r'\d{2}[-/.\s]{0,3}(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2,4}|'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2}[-/.\s]{0,3},?[-/.\s]{0,3}\d{2,4}'
        r')'
    ),

    'Street Address': (
        r'(?i)^'
        r'\d+\s+'
        r'(?!safe\s+dr)'
        r'(?:[\w\.\s-]+)\s+'
        r'(?:st\s*|street\s*|ave\s*|avenue\s*|rd\s*|road\s*|blvd\s*|boulevard\s*|dr\s*|drive\s*|ln\s*|lane\s*|ct\s*|court\s*|cir\s*|circle\s*|pkwy\s*|parkway\s*|hwy\s*|highway\s*|pl\s*|place\s*|ter\s*|terrace\s*|plz\s*|plaza\s*|way\s*|route\s*|rte\s*|run\s*|cres\s*|crescent\s*|trl\s*|trail\s*|cswy\s*|causeway\s*|row\s*|alley\s*|mnr\s*|manor\s*|sq\s*|square\s*|pass\s*|crossing\s*|park\s*|garden\s*|grn\s*|green\s*|walk\s*|walkway\s*|wharf\s*|track\s*|turn\s*|tun\s*|viaduct\s*|vista\s*|gln\s*|glen\s*|crk\s*|creek\s*|ridge\s*|mews\s*|jct\s*|junction\s*|fwy\s*|freeway\s*|expwy\s*|expressway\s*|pike\s*|pine\s*|pinelnd\s*|water\s*|wds\s*|wood\s*|woods*)\.?'
    ),

    'Sex': r'(?i)\b(?:SEX)\b\s*[:\s]*(M(?:ALE)?|F(?:EMALE)?)',

    'Height': (
        r'(?i)\b('
        r'\d{1,2}\'\s*-\s*\d{1,2}\"|'
        r'\d+\s*(?:cm)|'
        r'\d+\s*(?:inches?)|'
        r'\d{1,2}\s*in\s*'
        r')'
    ),

    'Weight': r'(?i)(\d{1,3}(?:\.\d{1,2})?\s*(?:kg|lbs?|pounds?))',

    'Class': (
        r'(?i)(?:CLASSIFICATION)\b\s*|(?:CLASS)\s*\s*([A-Z0-9]+|CHILD)'
    ),

    'Rest': (
        r'(?i)(?:REST(?:R(?:ICTIONS)?)?:?)\s*([A-Z0-9]{1,4}|none)'
    ),

    'Replaced': (
        r'(?i)(?:REPLAC[EA]D)[:\s]*'
        r'('
        r'\d{2}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2,4}|'
        r'\d{4}[-/.\s]{0,3}\d{2}[-/.\s]{0,3}\d{2}|'
        r'\d{2}[-/.\s]{0,3}(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2,4}|'
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/.\s]{0,3}\d{2}[-/.\s]{0,3},?[-/.\s]{0,3}\d{2,4}'
        r')'
    ),

    'License Number': (
        r'(?i)('
        r'Lic\s*[#:.\-]?\s*\d{9}\s*|'
        r'(?:DLN|DIN|AIN)?\s*[A-Z]\d{3}[\s.\-]?\d{3}[\s.\-]?\d{2}[\s.\-]?\d{3}[\s.\-]?\d|'
        r'NO[.\s]*\s*?0?\d{7}\s*|'
        r'4[da]\s*0?\d{7}\s*|'
        r'DLN\s*[A-Z0-9]+\s*|'
        r'DL\s*[I1O0]\d{7}\s*|'
        r'LIC\s*[#:;.\-]?\s*0?\d{6,9}\s*|'
        r'DL\s*NO[.\s]*\s*\d{8,12}\s*|'
        r'S\s*?\d{3}[\s.\-]?\d{3}[\s.\-]?\d{2}[\s.\-]?\d{3}[\s.\-]?\d\s*|'
        r'DL\s*NO[.\s]*\s*0?\d{9}\s*|'
        r'LIC\s*NO[.\s]*\s*[A-Z0-9]{3}[\s.\-]?\d{4}[\s.\-]?\d{4}\s*|'
        r'4[da]\s*DLN\s*\d{4}[\s.\-]?\d{2}[\s.\-]?\d{4}\s*|'
        r'DLN\s*\d{4}[\s.\-]?\d{2}[\s.\-]?\d{3}\s*|'
        r'DLN\s*\d{3}XX\d{4}\s*|'
        r'LIC\s*\.?#?\s*NO[.\s]*\s*[A-Z0-9]{3}[\s.\-]?\d{2}[\s.\-]?\d{4}\s*|'
        r'4[da]\s*DLN\s*[A-Z0-9]{3}[\s.\-]?\d{3}[\s.\-]?\d{3}\s*|'
        r'DL\s*NO[.\s]*\s*0?\d{7}\s*|'
        r'S[\s.\-]?\d{3}[\s.\-]?\d{3}[\s.\-]?\d{3}[\s.\-]?\d{3}\s*|'
        r'NUMBER\s*[A-Z0-9]+\s*|'
        r'DL#?\s*[A-Z]\d{3}[\s.\-]?\d{3}[\s.\-]?\d{3}[\s.\-]?\d{3}\s*|'
        r'DL\s*NO[.\s]*\s*\d{12}\s*|'
        r'LICENSE\s*#?[.\s]*\s*\d{9}\s*'
        r')'
    )
}
