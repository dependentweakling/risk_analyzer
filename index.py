import requests
import csv
from bs4 import BeautifulSoup

def data_source():
    try:
        lookup = requests.get("https://cit30900.github.io/strawbridge/")
        lookup.raise_for_status()
    except (requests.exceptions.RequestException, requests.exceptions.InvalidJSONError, requests.exceptions.JSONDecodeError):
        print("Error obtaining information.")
    else:
        response = lookup.text 
    return response

#I create a dictionary to access employee data.
def fire_Employees(data):
    chopping_Block = []
    machine = BeautifulSoup(data, 'html.parser')
    employees = machine.find_all(class_="card employee")

    #I collect employee data (first and last name and email and ssn.)
    for imp in employees:
        namae_ichi =  imp.find(class_= "emp_first_name").text.strip()
        namae_ni = imp.find(class_="emp_last_name").text.strip()
        meiru =  imp.find(class_= "emp_email").text.strip()
        ssn = imp.find(class_="secret").text.strip()
        temp_worker = {'first_name': namae_ichi, 'last_name': namae_ni, 'email': meiru, 'ssn': ssn}
        chopping_Block.append(temp_worker)

    return chopping_Block

def risk_Eval(ssn):
    try:
        lookup = requests.get("https://us-central1-cit-37400-elliott-dev.cloudfunctions.net/have-i-been-pwned?username={hmoloney}&ssn="+str(ssn))
    except (requests.exceptions.RequestException, requests.exceptions.InvalidJSONError):
        print("Error obtaining information.")
    else:
        data = lookup.json()
        response = data
    return response

def create_csv(fired):
    fieldnames = fired[0].keys()
    with open('employee_risk.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(fired)

def write_Email(e):
    filename = e['first_name']+"_"+e['last_name']+".txt"
    with open(filename, 'w') as file:
        file.write(f"Dear {e['first_name']} {e['last_name']},\n")
        file.write("Your personal data was accidentally exposed on the Strawbridge Industries\n")
        file.write("website and is at risk of being compromised. The company regrets this error and would\n")
        file.write("like to offer a credit monitoring service at no cost to you. \n")
        file.write("Please contact HR to establish this service. \n")
        file.write("Thank you, \n")
        file.write("Dick Strawbridge, CEO")

def main():
    high, medium, low = 0, 0, 0
    data = data_source()
    employee_List = fire_Employees(data)

    for e in employee_List:
        #checks to ensure the ssn is not empty
        if (e['ssn']):
            results = risk_Eval(e['ssn'])
            r = results['exposure']
            e['risk level'] = r
            if r =='high':
                high+=1
                write_Email(e)
            elif r == 'medium':
                medium+=1
            else:
                low +=1

    create_csv(employee_List)
    print(f"Risk occurances:\nHigh: {high}\nMedium: {medium}\nLow: {low}")
    

if __name__ == "__main__":
    main()