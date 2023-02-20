# Employee ID Table
"""
FULL NAME                   EMPLOYEE ID
 Nadav Zilberstein           0
 Eden Edry                   1
 Gal Levy                    2   
 Kareen Salameh              3
 Max Kotov                   4   
 Hen Ashkenazi               5
 Dan Otmazgin                6 
 Aviv Galipapa               7
 Omri Kerlman                8 
"""

# Constants
NUM_WORKERS = 9
NUM_WEEKS = 2
NUM_DAYS = 7
NUM_SHIFTS_PER_DAY = 3
WORKER_NAMES = ["Nadav", "Eden", "Gal", "Kareen", "Max", "Hen", "Dan", "Aviv", "Omri"]


from absl import app
from absl import flags
from ortools.sat.python import cp_model
from google.protobuf import text_format
import pandas as pd
from datetime import datetime
import requests


def get_df_from_url(test_mode = False):
    """Get the data frame as pandas URL from the user"""
    if not test_mode:
        print("Please enter the URL of the google sheet employee requests")
        print("Make sure the sheet is shared with the email address: test@gmail.com")
        sheets_url = input("URL: ")

        SHEET_ID = sheets_url.split('/')[-2]
        SHEET_NAME = 'requests'
        #print("Sheet ID: " + SHEET_ID)

        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
        try:
                r = requests.get(url)
                print("Status: " + str(r.status_code))
        except Exception as e:
            print(url + "\tNA FAILED TO CONNECT\t" + str(e))

    else:
        url = "https://docs.google.com/spreadsheets/d/1TdM3eMuliAY2Knp3QxCvLKucY19N8Jq0w2GTx7g2mV4/gviz/tq?tqx=out:csv&sheet=requests"
    df = pd.read_csv(url)

    #print data frame
    #print(df)

    return df


def get_last_shift_workers(test_mode = False):
    """Get the data frame as pandas URL from the user"""
    if not test_mode:
        print("Please enter the URL of the google sheet employee shift schedule of the last week")
        print("Make sure the sheet is shared with the email address: test@gmail.com")
        sheets_url = input("URL: ")

        SHEET_ID = sheets_url.split('/')[-2]
        SHEET_NAME = 'requests'
        #print("Sheet ID: " + SHEET_ID)
        
        url = f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}'
        try:
                r = requests.get(url)
                print("Status: " + str(r.status_code))
        except Exception as e:
            print(url + "\tNA FAILED TO CONNECT\t" + str(e))

    else:
        url = "https://docs.google.com/spreadsheets/d/1A5TnRjjZsAf_PF8WPPVniMumcVIeUaowrNIU9wpkY4Q/gviz/tq?tqx=out:csv&sheet=last_week_shifts"
    
    df = pd.read_csv(url)

    last_shift_workers = df.iloc[10][6]
    print("Last shift workers: " + last_shift_workers)
    return last_shift_workers


def get_start_date(requests):
    date_str = requests.columns[0]
    date_object = datetime.strptime(date_str, "%d-%m-%Y").date()


    return date_object


def convert_request_by_name(requests_df):
    shift_requests = []
    for worker in range(NUM_WORKERS):
        temp_shifts = []
        for day in range(7*NUM_WEEKS):
            temp_shifts.append([0, 0, 0])
        shift_requests.append(temp_shifts)

    for week in range(NUM_WEEKS):
        for day in range(7):
            for shift in range(3):
                #print("Week: " + str(week+1) + " Day: " + str(day+1) + " Shift: " + str(shift))
                #print("Col: " + str(day) + " Row: " + str(shift + 6 + week*3))
                temp_names = requests_df.iloc[shift + 1 + week*5][day]
                if "Nadav" in temp_names or "nadav" in temp_names:
                    shift_requests[0][day + week][shift] = 1
                if "Eden" in temp_names or "eden" in temp_names:
                    shift_requests[1][day + week][shift] = 1
                if "Gal" in temp_names or "gal" in temp_names:
                    shift_requests[2][day + week][shift] = 1
                if "Kareen" in temp_names or "kareen" in temp_names:
                    shift_requests[3][day + week][shift] = 1
                if "Max" in temp_names or "max" in temp_names:
                    shift_requests[4][day + week][shift] = 1
                if "Hen" in temp_names or "hen" in temp_names:
                    shift_requests[5][day + week][shift] = 1
                if "Dan" in temp_names or "dan" in temp_names:
                    shift_requests[6][day + week][shift] = 1
                if "Aviv" in temp_names or "aviv" in temp_names:
                    shift_requests[7][day + week][shift] = 1
                if "Omri" in temp_names or "omri" in temp_names:
                    shift_requests[8][day + week][shift] = 1
    
    #for i in range(NUM_WORKERS):
    #    print(shift_requests[i])
    return shift_requests






def solve_shift_scheduling(employees_requests, start_date, workers_last_week_last_shift):          
    print("Creating schedule \nStart Date: " + str(start_date))
    shift_requests = convert_request_by_name(employees_requests)
   
# Prints Functions
def print_request(shift_requests):
    print("Shift Requests")
    for i in range(NUM_WORKERS):
        print("Worker " + str(i+1) + ": " + WORKER_NAMES[i])
        for j in range(7*NUM_WEEKS):
            print("Day " + str(j) + ": " + str(shift_requests[i][j]))


def solve_shift_scheduling_test(employees_requests, start_date, num_weeks, num_workers):

    print("Creating schedule \nStart Date: " + str(start_date))

    shift_requests = convert_request_by_name(employees_requests, num_weeks, 9)

    num_shifts = 3
    num_days = 7 * num_weeks


    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    # shifts[(w, d, s)]: worker 'w' works shift 's' on day 'd'.
    shifts = {}
    for w in range(num_workers):
        for d in range(num_days):
            for s in range(num_shifts):
                shifts[(w, d, s)] = model.NewBoolVar('shift_n%id%is%i' % (w, d, s))

    # Each shift is assigned to exactly two workers
    for d in range(num_days):
        for s in range(num_shifts):
            model.AddExactlyOne(shifts[(w, d, s)] for w in range(num_workers))

    # Each worker works at most one shift per day.
    for w in range(num_workers):
        for d in range(num_days):
            model.AddAtMostOne(shifts[(w, d, s)] for s in range(num_shifts))

    # Try to distribute the shifts evenly, so that each worker works
    # min_shifts_per_worker shifts. If this is not possible, because the total
    # number of shifts is not divisible by the number of workers, some workers will
    # be assigned for one more shift.
    min_shifts_per_worker = (num_shifts * num_days)
    if num_shifts * num_days % num_workers == 0:
        max_shifts_per_nurse = min_shifts_per_worker
    else:
        max_shifts_per_nurse = min_shifts_per_worker + 1
    
    for w in range(num_workers):
        num_shifts_worked = 0
        for d in range(num_days):
            for s in range(num_shifts):
                num_shifts_worked += shifts[(w, d, s)]
        model.Add(min_shifts_per_worker <= num_shifts_worked)
        model.Add(num_shifts_worked <= max_shifts_per_nurse)

    # pylint: disable=g-complex-comprehension
    print()
    model.Maximize(sum(shift_requests[w][d][s] * shifts[(w, d, s)] for w in range(num_workers)
            for d in range(num_days) for s in range(num_shifts)))
    



    # Creates the solver and solve.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)


    # printing the solution
    if status == cp_model.OPTIMAL:
        print('Solution:')
        for d in range(num_days):
            print('Day', d)
            for w in range(num_workers):
                for s in range(num_shifts):
                    if solver.Value(shifts[(w, d, s)]) == 1:
                        if shift_requests[w][d][s] == 1:
                            print('Worker', w, 'works shift', s, '(requested).')
                        else:
                            print('Worker', w, 'works shift', s, '(not requested).')
            print()
        print(f'Number of shift requests met = {solver.ObjectiveValue()}',
              f'(out of {num_workers * min_shifts_per_worker})')
    else:
        print('No optimal solution found !')

    # Statistics.
    print('\nStatistics')
    print('  - conflicts: %i' % solver.NumConflicts())
    print('  - branches : %i' % solver.NumBranches())
    print('  - wall time: %f s' % solver.WallTime())


    return


def main(_):
    #TODO: create UI

    ### get data from google sheets to pandas df
    requests_df = get_df_from_url(True)
    last_shift_workers = get_last_shift_workers(True)

    ### get the start date of the next schedule 
    start_date = get_start_date(requests_df)

    toPrint = convert_request_by_name(requests_df)
    print_request(toPrint)
    ### solve
    #solve_shift_scheduling(requests_df, start_date, last_shift_workers)
    print("done")

if __name__ == '__main__':
    app.run(main)