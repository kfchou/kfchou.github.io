import re

def map_seniority_levels(df):
    """
    Map seniority levels based on job titles in the DataFrame.
    
    Parameters:
    df (DataFrame): DataFrame containing a column 'Role / Title of current position'.
    
    Returns:
    DataFrame: Updated DataFrame with a new column 'Seniority Level'.
    """

    career_levels = [
        'Lead/Principal/Staff/Director', 'Technician', 'Manager', 'Associate',
        'Associate Lead/Principal/Director', 'Sr. Scientist', 'Scientist',
        'Sr. Engineer', 'Engineer', 'Data Scientist or Computational Biologist',
        'Sr. Data Scientist or Computational Biologist', 'VP or higher', 'Others',
        'Senior Associate', 'Intern or student'
    ]

    patterns = [
        ('Associate Lead/Principal/Director', r'\b(associate|assoc|assc)\s*(lead|principal|director|dir)\b'),
        ('Lead/Principal/Staff/Director', r'\b(^lead\b|principal|staff|director|dir|head|advisor|cs[eo]|svp|chief)\b'),
        ('Sr. Data Scientist or Bioinfomatician', r'\b(sr\.?\s*(data sci[a-z]*|data scientist|bioinformatician|computational biologist)|senior\s+(data sci[a-z]*|data scientist|bioinformatician|computational biologist))\b'),
        ('Data Scientist or Bioinfomatician', r'\b(data sci[a-z]*|data scientist|bioinformatician|computational biologist)\b'),
        ('Sr. Scientist', r'\b(sr\.?\s*scientist|senior\s+scientist)\b'),
        ('Scientist', r'\bscientist\b'),
        ('Sr. Manager', r'\b(sr\.?\s+\w+\s+manager|sr\.?\s*manager|senior\s+\w+\s+manager|senior\s+manager|manager\s+(iii|iv))\b'),
        ('Sr. Engineer', r'\b(sr\.?\s*engineer|senior\s+engineer|engineer\s+(iii|iv))\b'),
        ('Engineer', r'\b(engineer|engineering|r&d engineer)\b'),
        ('Technician', r'\b(technician|operator|tech|lab\s+operator|lab\s+supervisor)\b'),
        ('Senior Associate', r'\b(senior\s+associate|sra\s?\d*)\b'),
        ('Associate', r'\b(jr|junior|associate(?!\s+(lead|director|principal))|lab(?:oratory|ratory)?\s+manager|assoc|assc|entry[- ]level|as\d)\b'),
        ('VP or higher', r'\b(vp|vice president|ceo|cso|cto|cmo|general counsel|svp|chief)\b'),
        ('Manager', r'\b(manager|supervisor|project manager|mgr)\b'),
        ('Intern or student', r'\b(intern|student|phd candidate|post\s+doc|co-op)\b'),
    ]


    def categorize(title):
        title_clean = title.lower().strip()
        for category, pattern in patterns:
            if re.search(pattern, title_clean):
                return category
        return 'Others'

    df['Seniority Level'] = df['Role / Title of current position'].apply(categorize)

    # saveoutput for debugging
    df[['Role / Title of current position','Seniority Level']].to_csv('temp.csv',index=False)
    
    return df