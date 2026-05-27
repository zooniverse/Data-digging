import requests

def main():
    WORKFLOW_ID = 19276  # Replace with actual workflow ID
    START_DATE = "2026-05-20"  # Replace with start date
    END_DATE = "2026-05-26"  # Replace with end date

    # List of all possible parameters: (found in https://zooniverse.github.io/eras/querying-classification-counts-unauth.html#querying-classification-counts-unauthenticated)
    # workflow_id (or project_id, but not both), period, start_date, end_date
    url = f"https://eras.zooniverse.org/classifications/?workflow_id={WORKFLOW_ID}&period=day"

    if START_DATE:
        url += f"&start_date={START_DATE}"

    if END_DATE:
        url += f"&end_date={END_DATE}"
    response = requests.get(url)
    response.raise_for_status()
    print(response.text)


if __name__ == "__main__":
    main()
