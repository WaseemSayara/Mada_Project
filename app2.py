from flask import Flask, render_template, request, redirect, url_for, session, g, flash, jsonify
import datetime
from datetime import datetime
from datetime import date, timedelta
import calendar
from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import MySQLdb
import re
import hashlib

app2 = Flask(__name__)
conn = MySQLdb.connect(host="localhost", user="root", password="waseem123", db="mada")
app2.secret_key = 'secret key'

users = []


# function used in statistics page
# ------------------------------------------------------------------------------------------
def make_email(first_name, last_name, emp_id, id_, type):
    "To Auto create an email for the employee when added by the admin"

    username = str(first_name[0]).lower() + str(last_name[0]).lower() + str(emp_id[0])
    email = username + "@gmail.com"
    pass1 = id_

    cursor = conn.cursor()
    cursor.execute(
        "select b.addres from branch b, employee_work e where b.branch_number=e.branch_number and e.Employee_id = '" + str(
            emp_id) + "'")
    address = cursor.fetchone()
    cursor.close()
    phone = "05"
    if type == "Technical":
        type2 = "et"
    elif type == "Programmer":
        type2 = "ep"
    else:
        type2 = "ej"

    password = hashlib.md5(pass1.encode()).hexdigest()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users  VALUES (% s, % s, % s, % s, % s, % s, % s , %s)',
                   (email, username, first_name, last_name, password, address, phone, type2))
    conn.commit()
    return


def change_branch():
    "change the count of employees in each branch (used when adding a new employee or updating him)"

    cursor = conn.cursor()
    cursor.execute(
        "select b.branch_number,count(*) from branch b, employee_work e where e.branch_number=b.branch_number group by(b.branch_number);")
    branches = cursor.fetchall()
    cursor.close()

    cursor = conn.cursor()
    for branch in branches:
        cursor.execute(
            "UPDATE branch SET number_Employees= '" + str(branch[1]) + "' WHERE branch_number='" + str(branch[0]) + "'")
        conn.commit()
    cursor.close()
    return


def change_point(emp_id, rating):
    "change the points for the technical employee when rated by the customer"
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE technical_support t SET t.points = '" + rating + "' WHERE t.Employee_id='" + str(emp_id) + "'")
    conn.commit()
    cursor.close()
    return


def activitaion():
    "auto DeAvctivate the customer when the invoice is over"

    cursor = conn.cursor()
    cursor.execute(
        "select distinct i.serial_id , max(i.serial_number) from invoices_pay i where i.state = 'Paid' group by (i.serial_id);")
    invo = cursor.fetchall()
    if invo is not None:
        invo = list(invo)
        ms = datetime.now().timestamp() * 1000

        for i in invo:
            cursor.execute(
                "select distinct i.end_date from invoices_pay i where i.serial_number = '" + str(i[1]) + "' ")
            date2 = cursor.fetchone()
            date2 = date2[0]
            year1 = date2.year
            month1 = date2.month
            day1 = date2.day
            new_date = datetime(year1, month1, day1, 0, 0)
            time_ms = new_date.timestamp() * 1000
            # time_ms -= 4 * 86400000  # 86400000 is the number of mSec in a day (mul by 4 to make it 4 days)
            print(ms)
            print(time_ms)
            if ms > time_ms:
                print("hi")
                print(i[0])
                cursor.execute(
                    "update customer_link set line_status ='" + "InActive" + "' where serial_id = '" + str(i[0]) + "'")
                conn.commit()
    cursor.close()
    return


def months():
    "get the earning in each month"

    list_of_earnings = []
    cursor = conn.cursor()
    for i in range(1, 12):
        date1 = "2021-" + str(i) + "-1"
        date2 = "2021-" + str(i + 1) + "-1"

        cursor.execute(
            "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
        mon = cursor.fetchone()
        if mon[0] is not None:
            list_of_earnings.append(mon[0])
        else:
            list_of_earnings.append(0)

    cursor.execute(
        "select sum(I.payment) from invoices_pay I where start_date >= '2021-12-1' and state='Paid' and start_date < '2021-12-31' ")
    mon = cursor.fetchone()
    if mon[0] is not None:
        list_of_earnings.append(mon[0])
    else:
        list_of_earnings.append(0)
    cursor.close()

    return list_of_earnings


def weeks():
    "get the earning in each week of the month"

    list_of_weeks = []
    cursor = conn.cursor()
    for i in range(1, 12):
        week = []
        date1 = "2021-" + str(i) + "-1"
        date2 = "2021-" + str(i) + "-8"

        cursor.execute(
            "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
        tmp = cursor.fetchone()
        if tmp[0] is not None:
            week.append(tmp[0])
        else:
            week.append(0)

        date1 = "2021-" + str(i) + "-8"
        date2 = "2021-" + str(i) + "-15"

        cursor.execute(
            "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
        tmp = cursor.fetchone()
        if tmp[0] is not None:
            week.append(tmp[0])
        else:
            week.append(0)

        date1 = "2021-" + str(i) + "-15"
        date2 = "2021-" + str(i) + "-22"

        cursor.execute(
            "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
        tmp = cursor.fetchone()
        if tmp[0] is not None:
            week.append(tmp[0])
        else:
            week.append(0)

        date1 = "2021-" + str(i) + "-22"
        date2 = "2021-" + str(i) + "-28"

        cursor.execute(
            "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date <= '" + date2 + "' ")
        tmp = cursor.fetchone()
        if tmp[0] is not None:
            week.append(tmp[0])
        else:
            week.append(0)

        if i != 2:
            date1 = "2021-" + str(i) + "-29"
            date2 = "2021-" + str(i + 1) + "-1"

            cursor.execute(
                "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
            tmp = cursor.fetchone()
            if tmp[0] is not None:
                week.append(tmp[0])
            else:
                week.append(0)

        list_of_weeks.append(week)

    week = []
    date1 = "2021-" + "12" + "-1"
    date2 = "2021-" + "12" + "-8"

    cursor.execute(
        "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
    tmp = cursor.fetchone()
    if tmp[0] is not None:
        week.append(tmp[0])
    else:
        week.append(0)

    date1 = "2021-" + "12" + "-8"
    date2 = "2021-" + "12" + "-15"

    cursor.execute(
        "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
    tmp = cursor.fetchone()
    if tmp[0] is not None:
        week.append(tmp[0])
    else:
        week.append(0)

    date1 = "2021-" + "12" + "-15"
    date2 = "2021-" + "12" + "-22"

    cursor.execute(
        "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date < '" + date2 + "' ")
    tmp = cursor.fetchone()
    if tmp[0] is not None:
        week.append(tmp[0])
    else:
        week.append(0)

    date1 = "2021-" + "12" + "-22"
    date2 = "2021-" + "12" + "-28"

    cursor.execute(
        "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date <= '" + date2 + "' ")
    tmp = cursor.fetchone()
    if tmp[0] is not None:
        week.append(tmp[0])
    else:
        week.append(0)

    date1 = "2021-" + "12" + "-29"
    date2 = "2021-" + "12" + "-31"

    cursor.execute(
        "select sum(I.payment) from invoices_pay I where start_date >= '" + date1 + " ' and state='Paid' and start_date <= '" + date2 + "' ")
    tmp = cursor.fetchone()
    if tmp[0] is not None:
        week.append(tmp[0])
    else:
        week.append(0)

    list_of_weeks.append(week)

    cursor.close()

    return list_of_weeks

def categories():
    cursor = conn.cursor()
    cursor.execute("select count(c.serial_id) from customer_link c where c.category like 'Bronze'")
    num_of_bron = list(cursor.fetchone())
    cursor.close()
    if num_of_bron[0] is None:
        num_of_bron[0] = 0

    cursor = conn.cursor()
    cursor.execute("select count(c.serial_id) from customer_link c where c.category like 'Silver'")
    num_of_sil = list(cursor.fetchone())
    cursor.close()
    if num_of_sil[0] is None:
        num_of_sil[0] = 0

    cursor = conn.cursor()
    cursor.execute("select count(c.serial_id) from customer_link c where c.category like 'Gold'")
    num_of_gol = list(cursor.fetchone())
    cursor.close()
    if num_of_gol[0] is None:
        num_of_gol[0] = 0

    cursor = conn.cursor()
    cursor.execute("select count(c.serial_id) from customer_link c where c.category like 'Platinum'")
    num_of_pla = list(cursor.fetchone())
    cursor.close()
    if num_of_pla[0] is None:
        num_of_pla[0] = 0

    list_of_cat = []

    list_of_cat.append(int(num_of_bron[0]))
    list_of_cat.append(int(num_of_sil[0]))
    list_of_cat.append(int(num_of_gol[0]))
    list_of_cat.append(int(num_of_pla[0]))

    print(list_of_cat)
    return list_of_cat



# End of statistics functions
# ------------------------------------------------------------------------------------------

# Home page functions
# ------------------------------------------------------------------------------------------
@app2.route("/")
def home():
    "clear the old sessions when starting the program"

    session.clear()
    return render_template("index.html")


# function for signing in
@app2.route("/", methods=["POST"])
def signIn():
    "check the email and password when sign in and redirect each one to its correct place"

    username = str(request.form["username_login"])
    password = str(request.form["password_login"])

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username ='" + username + "' and password1='" + hashlib.md5(
        password.encode()).hexdigest() + "'")
    user = cursor.fetchone()
    cursor.close()
    global in_user

    if user is not None:  # valid user
        myUser = list(user)
        in_user = list(user)
        print("entered")
        session['user_id'] = myUser[0]
        print("session done")
        in_user[2] = str(in_user[2]).title()
        in_user[3] = str(in_user[3]).title()
        print(user)
        tmp = user[1]
        tmp_list = list(tmp)
        tmp_list[0] = ""
        tmp_list[1] = ""
        tmp = "".join(tmp_list)
        print(tmp)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM employee_work WHERE Employee_id ='" + tmp + "'")
        tmp_emp = cursor.fetchone()
        cursor.close()
        print(tmp_emp)

        if user[7] == 'c':
            return redirect(url_for('Personal_info'))
        elif (user[7] == 'et' or user[7] == 'ep') and tmp_emp[8] == "Active":
            activitaion()
            return redirect(url_for('employee'))
        elif user[7] == 'a':
            return redirect(url_for('Admin_1'))
    else:
        print("flaaaaaaaaaash")
        flash('wrong username or password', 'danger')
        return redirect(url_for('signIn'))

    return render_template("index.html")


# End of home page functions
# ------------------------------------------------------------------------------------------

# sign up Page
# ------------------------------------------------------------------------------------------
@app2.route('/signup', methods=['GET', 'POST'])
def signup():
    "signup for the website by anyone either if subscribed in the company or not"

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']
        password = request.form['password']
        password_2 = request.form['password_2']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = % s or email = % s or phone = % s', (username,email,phone,))
        account = cursor.fetchone()
        print(account)
        if account:
            if str(account[1]) == str(username):
                msg = 'Username already exists !'
            elif str(account[0]) == str(email):
                msg = 'Email already exists !'
            elif str(account[6]) == str(phone):
                msg = 'Phone already exists !'
        elif password != password_2:
            msg = 'Password does not match !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not str(firstname).isalpha():
            msg = 'Firstname must contain only characters and numbers !'
        elif not str(lastname).isalpha():
            msg = 'Lastname must contain only characters and numbers !'
        elif not str(phone).isnumeric():
            msg = 'Phone Number must contain only numbers !'
        elif not firstname or not lastname or not username or not email or not phone or not address or not date or not password or not password_2:
            msg = 'Please fill out the form !'
        else:
            password = hashlib.md5(password.encode()).hexdigest()
            cursor.execute('INSERT INTO users  VALUES (% s, % s, % s, % s, % s, % s, % s , %s)',
                           (email, username, firstname, lastname, password, address, phone, 'c'))
            conn.commit()
            msg = 'You have successfully registered !'
            return redirect(url_for('home'))
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signup.html', msg=msg)


@app2.route("/Customer/personal_info", methods=['GET', 'POST'])
def Personal_info():
    "the home page in the customer page (shows his info)"

    print("entered profile")

    if 'user_id' in session and in_user[7] == "c":
        cursor = conn.cursor()
        cursor.execute("select * from users  WHERE email ='" + in_user[0] + "'")
        users1 = cursor.fetchone()
        cursor.close()
        global customers_1
        customers_1 = list(users1)
        print(customers_1)
        return render_template("personal_info.html", cust=customers_1,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


# End of sign up Page
# ------------------------------------------------------------------------------------------

# Employee page
# ------------------------------------------------------------------------------------------
@app2.route("/employee")
def employee():
    "the main page for the employee (contains the customers information)"

    print("entered profile")

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):

        cursor = conn.cursor()
        cursor.execute("select * from customer_link")
        users1 = cursor.fetchall()
        cursor.execute("SELECT * FROM branch ")
        branches1 = cursor.fetchall()
        cursor.close()
        global customers
        customers = list(users1)
        branches2 = list(branches1)
        return render_template("employee.html", employees=customers, branches=branches2,
                               user_name=str(in_user[2]) + " " + str(in_user[3]), type=in_user[7])
    else:
        return redirect(url_for('home'))


# Help page
@app2.route("/employee/help")
def employee_help():
    "the page for answering the pending helps (for technical employees only)"

    if 'user_id' in session and (in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("select * from complains order by type_help")
        complains = cursor.fetchall()
        cursor.close()
        complains2 = list(complains)
        return render_template("employee_help.html", type=in_user[7], complains=complains,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


# Project Statistics Page
@app2.route("/employee/statistics")
def employee_statistics():
    "the page for the company Statistics"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("select count(*) from customer_link")
        num_of_customers = cursor.fetchone()
        cursor.close()
        print(num_of_customers)
        if num_of_customers is None:
            print(num_of_customers)
            num_of_customers = 0

        cursor = conn.cursor()
        cursor.execute("select count(*) from employee_work")
        num_of_employees = cursor.fetchone()
        cursor.close()
        if num_of_employees is None:
            num_of_employees = 0

        cursor = conn.cursor()
        cursor.execute("select sum(I.payment) from invoices_pay I where state='Paid'")
        Total_earnings = cursor.fetchone()
        cursor.close()
        print(Total_earnings)
        if Total_earnings[0] is None:
            Total_earnings = [0, 0]

        cursor = conn.cursor()
        cursor.execute("select count(*) from technical_support")
        num_of_tech = cursor.fetchone()
        cursor.close()
        if num_of_tech is None:
            num_of_tech = 0

        cursor = conn.cursor()
        cursor.execute("select count(*) from programmer")
        num_of_prog = cursor.fetchone()
        cursor.close()
        if num_of_prog is None:
            num_of_prog = 0

        cursor = conn.cursor()
        cursor.execute("select count(*) from janitor ")
        num_of_jan = cursor.fetchone()
        cursor.close()
        if num_of_jan is None:
            num_of_jan = 0

        cursor = conn.cursor()
        cursor.execute("select count(p.project_id) from project p ")
        num_of_proj = cursor.fetchone()
        cursor.close()
        if num_of_proj is None:
            num_of_proj = 0

        cursor = conn.cursor()
        cursor.execute("SELECT AVG(salary) FROM employee_work e where e.state='Active' and e.Employee_id in (select d.Employee_id from dependents_has d)")
        dep_salary = list(cursor.fetchone())
        cursor.close()
        print(dep_salary)
        if dep_salary[0] is None:
            dep_salary[0] = 0

        cursor = conn.cursor()
        cursor.execute("SELECT AVG(salary) FROM employee_work e where e.state='Active' and e.Employee_id not in (select d.Employee_id from dependents_has d)")
        dep_salary1 = list(cursor.fetchone())
        cursor.close()
        print(dep_salary1)
        if dep_salary1[0] is None:
            dep_salary1[0] = 0

        dep_salaries = []
        dep_salaries.append(int(dep_salary[0]))
        dep_salaries.append(int(dep_salary1[0]))


        cursor = conn.cursor()
        cursor.execute("select i.internet_speed from invoices_pay i group by i.internet_speed order by count(i.serial_number) desc limit 1")
        top_speed = list(cursor.fetchone())
        cursor.close()
        print(top_speed)

        cursor = conn.cursor()
        cursor.execute("select i.internet_speed from invoices_pay i group by i.internet_speed order by count(i.serial_number) asc limit 1")
        down_speed = list(cursor.fetchone())
        cursor.close()
        print(down_speed)

        cursor = conn.cursor()
        cursor.execute("select count(*) from need_help n where n.need_visit like 'yes'")
        visits = list(cursor.fetchone())
        if visits[0] is None:
            visits[0] = 0

        today = date.today()
        d1 = today.strftime("%Y-%m-%d")
        d2 = d1.split("-")
        start_date = date(int(d2[0]), int(d2[1]), int(d2[2]))
        days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
        end_date = start_date - timedelta(days=days_in_month)
        print(end_date)

        cursor = conn.cursor()
        cursor.execute(
            "select count(n.employee_id), e.first_name, e.last_name from employee_work e, need_help n where e.employee_id=n.employee_id and n.rating='good'and n.visit_date >'" + str(
                end_date) + "' group by (n.employee_id) order by 1 desc limit 1;")
        emp12 = cursor.fetchone()
        cursor.close()
        if emp12 is not None:
            emp_of_the_month = str(emp12[1]) + " " + str(emp12[2])
        else:
            emp_of_the_month = "None"

        cursor = conn.cursor()
        cursor.execute("SELECT SUM(salary) FROM employee_work e where e.state='Active' ")
        sum_salary = list(cursor.fetchone())
        cursor.close()
        print(sum_salary)
        if sum_salary[0] is None:
            sum_salary[0] = 0

        cursor = conn.cursor()
        cursor.execute("SELECT SUM(payment) from invoices_pay where state = 'Paid' and issue_date > '"+ str(end_date) +"' and issue_date <= '"+ str(today)+"'  ")
        sum_payment = list(cursor.fetchone())
        cursor.close()
        print(sum_payment)
        if sum_payment[0] is None:
            sum_payment[0] = 0

        last_number= int(sum_payment[0])-int(sum_salary[0])



        list_of_earnings = months()
        list_of_weeks = weeks()
        list_of_cat = categories()

        return render_template("statistics.html", type=in_user[7], num_of_customers=num_of_customers[0],
                               num_of_employees=num_of_employees[0], Total_earnings=int(Total_earnings[0]),
                               num_of_tech=int(num_of_tech[0]), num_of_prog=int(num_of_prog[0]),
                               list_of_cat=list_of_cat,top_speed=top_speed[0],down_speed=down_speed[0],
                               num_of_jan=int(num_of_jan[0]), emp_of_the_month=emp_of_the_month,
                               visits=visits[0],last_number=last_number,
                               num_of_proj=int(num_of_proj[0]),dep_salaries=dep_salaries, list_of_earnings=list_of_earnings,
                               list_of_weeks=list_of_weeks, user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


# Answered help
@app2.route("/employee/helped/<id>/", methods=['GET', 'POST'])
def employee_helped(id):
    "the function to handle the complain when answered by the technical support"

    print("entered helpped")

    if 'user_id' in session and (in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("select * from complains where help_id = '" + id + "'")
        complains = cursor.fetchone()
        cursor.close()
        complains2 = list(complains)

        emp_id = in_user[1]
        emp_id = emp_id[2::]
        print(emp_id)

        now_date = datetime.now()
        now_date = now_date.date()
        now_date2 = now_date.strftime("%Y-%m-%d")

        cursor = conn.cursor()
        cursor.execute(
            "insert into need_help(visit_date,need_visit,serial_id,Employee_id,rating) values(%s,%s,%s,%s,%s )",
            (now_date2, complains2[3], complains2[2], emp_id, "good"))
        conn.commit()
        cursor.close()
        flash('This complain is handeled !', 'success')

        tmp = in_user[1]
        tmp_list = list(tmp)
        tmp_list[0] = ""
        tmp_list[1] = ""
        e_id = "".join(tmp_list)

        cursor = conn.cursor()
        cursor.execute("select * from technical_support where Employee_id = '" + e_id + "'")
        point = cursor.fetchone()

        point = list(point)
        print(point)
        point[2] += 1

        cursor.execute("update technical_support set points = '" + str(point[2]) + "'")
        conn.commit()
        cursor.close()

        cursor = conn.cursor()
        cursor.execute("delete from complains where help_id = '" + id + "'")
        conn.commit()
        cursor.close()

        return redirect(url_for('employee_help'))
    else:
        return redirect(url_for('home'))


# route for inserting data to mysql database via html forms
@app2.route('/insert', methods=['POST'])
def insert():
    "the function to handle the adding of a new customer ( in employee's page)"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):

        if request.method == 'POST':
            id_ = request.form['id_']
            name = request.form['name']
            phone = request.form['phone']
            speed = request.form['speed']
            category = request.form['category']
            duration = request.form['duration']
            address = request.form['address']
            branch = request.form['branch']

            l = []
            l.append(id_)
            l.append(name)
            l.append(phone)
            l.append(speed)
            l.append(category)
            l.append(duration)
            l.append(address)
            l.append(branch)

            fetched_id = []
            fetched_phone = []

            if str(id_).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM customer_link WHERE id = % s', (id_,))
                fetched_id = cursor.fetchall()
                cursor.close()

            if str(phone).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM customer_link WHERE telephone_number = % s', (phone,))
                fetched_phone = cursor.fetchall()
                cursor.close()

            if fetched_id:
                flash('This Person already exist !', 'danger')

            elif fetched_phone:
                flash('This Phone Number already exist !', 'danger')

            elif not str(id_).isnumeric():
                flash('ID must contain only numbers !', 'danger')

            elif not bool(re.match('[a-zA-Z\s]+$', name)):
                flash('The name must contain letters only !', 'danger')

            elif not str(phone).isnumeric():
                flash('Phone Number must contain only numbers !', 'danger')

            elif not str(duration).isnumeric():
                flash('Duration must contain only numbers !', 'danger')

            else:
                cursor = conn.cursor()
                cursor.execute("SELECT CURDATE()")
                today = cursor.fetchone()
                print(today)
                cursor.execute(
                    "insert into customer_link(id,customer_name,telephone_number,internet_speed,category,start_date,addres , branch_number , line_status) values(%s,%s,%s,%s,%s,%s,%s,%s,%s )",
                    (id_, name, phone, speed, category, today[0], address, branch, "Active"))
                conn.commit()
                today = date.today()
                d1 = today.strftime("%Y-%m-%d")
                d2 = d1.split("-")
                start_date = date(int(d2[0]), int(d2[1]), int(d2[2]))
                x1 = int( (int(d2[1]) + int(duration)-1) / 12)
                x2 = int((int(d2[1]) + int(duration)) % 12)
                if x2 == 0:
                    x2 = 12

                end_date = date(int(int(d2[0]) + x1), x2, int(d2[2]))

                flash("Customer Inserted Successfully", 'success')
                cursor.execute(
                    "select c.serial_id from customer_link c where c.id = '" + id_ + "'")
                serial_id = cursor.fetchone()
                cursor.execute(
                    "select s.price from speed_price s where s.speed = '" + speed + "'")
                payment = cursor.fetchone()
                payment2 = payment[0] * int(duration)
                price = list(payment)
                pay = price[0] * int(duration)

                cursor.execute(
                    "insert into invoices_pay(start_date,end_date,issue_date,payment,internet_speed,serial_id,state) values(%s,%s,%s,%s,%s,%s,%s )",
                    (d1, end_date, d1, pay, speed, serial_id, 'Paid'))
                conn.commit()
                cursor.close()

            return redirect(url_for('employee'))

    else:
        return redirect(url_for('home'))


# this is our update route where we are going to update our employee
@app2.route('/update', methods=['GET', 'POST'])
def update():
    "updating the information of a customer by the employee"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):

        if request.method == 'POST':

            # my_data = Data.query.get(request.form.get('id'))
            serial_id = request.form['Serial_id']
            print(serial_id)
            id_ = request.form['id_']
            name = request.form['name']
            phone = request.form['phone']
            speed = request.form['speed']
            speed = int(speed)
            category = request.form['category']
            address = request.form['address']
            branch = request.form['branch']

            if str(id_).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM customer_link WHERE id = % s', (id_,))
                fetched_id = cursor.fetchall()
                cursor.close()

            if str(id_).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM customer_link WHERE telephone_number = % s', (phone,))
                fetched_phone = cursor.fetchall()
                cursor.close()

            if fetched_id and int(fetched_id[0][0]) != int(serial_id) :
                flash('This Person already exist !', 'danger')

            elif fetched_phone and int(fetched_phone[0][0]) != int(serial_id) :
                flash('This phone already exist !', 'danger')

            elif not bool(re.match('[a-zA-Z\s]+$', name)):
                flash('The name must contain letters only !', 'danger')

            elif not str(id_).isnumeric():
                flash('ID must contain only numbers !', 'danger')

            elif not str(phone).isnumeric():
                flash('Phone Number must contain only numbers !', 'danger')

            else:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE customer_link SET id=%s, customer_name=%s, telephone_number=%s, internet_speed=%s, category=%s, addres=%s, branch_number=%s WHERE serial_id=%s",
                    (id_, name, phone, speed, category, address, branch, serial_id))
                conn.commit()
                cursor.close()
                flash("Customer Updated Successfully", 'success')

            return redirect(url_for('employee'))
    else:
        return redirect(url_for('home'))


# This route is for DeActivating an employee
@app2.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    "DeActivating a customer by an employee"

    print("hello")
    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("update customer_link set line_status = '" + "InActive" + "' where serial_id = '" + id + "'")
        conn.commit()
        cursor.close()

        flash("Customer DeActivated Successfully", 'success')

        return redirect(url_for('employee'))
    else:
        return redirect(url_for('home'))


# This route is for Activating an employee
@app2.route('/Activate/<id>/', methods=['GET', 'POST'])
def Activate(id):
    "Avtivate a customer by the employee"

    print("hello")
    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("update customer_link set line_status = '" + "Active" + "' where serial_id = '" + id + "'")
        conn.commit()
        cursor.close()
        flash("Customer Activated Successfully", 'success')
        return redirect(url_for('employee'))
    else:
        return redirect(url_for('home'))


@app2.route('/signout/', methods=['GET', 'POST'])
def signout():
    "handle the session when signed out"
    # serial_id = request.form['Serial_id']
    print("hello")
    session.clear()
    return redirect(url_for('employee'))


@app2.route("/employee/paidInvoices", methods=['GET', 'POST'])
def paidInvoices():
    "the page to show the paid invoices only in the employee page"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices_pay WHERE state='" + 'Paid' + "'")
        invoices_2 = list(cursor.fetchall())

        invoices = []
        for x in invoices_2:
            invoices.append(list(x))
        return render_template("C_invoices.html", type=in_user[7], invoices=invoices,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


@app2.route("/employee/unpaidInvoices", methods=['GET', 'POST'])
def unpaidInvoices():
    "the page to show the unpaid invoices only in the employee page"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM invoices_pay WHERE state='" + 'UnPaid' + "'")
        invoices_2 = list(cursor.fetchall())
        invoices = []
        for x in invoices_2:
            invoices.append(list(x))

        return render_template("C_invoices.html", type=in_user[7], invoices=invoices,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


@app2.route("/employee/edit_invoices")
def edit_invoices():
    "the function to show all the invoices in the company"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("select * from invoices_pay")
        inv = cursor.fetchall()
        cursor.close()
        Invoices_1 = list(inv)
        return render_template("edit_invoices.html", type=in_user[7], invoices=Invoices_1,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


@app2.route('/insert_invoice', methods=['POST'])
def insert_invoice():
    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):

        if request.method == 'POST':
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            issue_date = date.today()
            payment = request.form['payment']
            speed = request.form['speed']
            serial_id = request.form['serial_id']
            state = request.form['state']

            l = []
            l.append(start_date)
            l.append(end_date)
            l.append(issue_date)
            l.append(payment)
            l.append(speed)
            l.append(serial_id)
            l.append(state)
            cursor = conn.cursor()
            cursor.execute(
                "select serial_id from customer_link where serial_id = '" + serial_id + "'")

            customer = cursor.fetchone()
            if not str(payment).isnumeric():
                flash('payment must contain only numbers !', 'danger')

            elif not str(serial_id).isnumeric():
                flash('Serial_id must contain only numbers !', 'danger')

            elif customer is not None:

                today = date.today()
                d1 = today.strftime("%Y-%m-%d")
                # d2 = d1.split("-")
                # start_date = date(int(d2[0]), int(d2[1]), int(d2[2]))
                # days_in_month = calendar.monthrange(start_date.year, start_date.month)[1]
                # end_date = start_date + timedelta(days=days_in_month)
                flash("Invoice Inserted Successfully", 'success')
                cursor.execute(
                    "select s.price from speed_price s where s.speed = '" + speed + "'")
                payment = cursor.fetchone()
                cursor.execute(
                    "insert into invoices_pay (start_date,end_date,issue_date,payment,internet_speed,serial_id,state) values(%s,%s,%s,%s,%s,%s,%s )",
                    (start_date, end_date, d1, payment, speed, serial_id, state))
                conn.commit()
                cursor.close()
            else:
                flash('Serial id does not match any customer !', 'danger')
            return redirect(url_for('edit_invoices'))

    else:
        return redirect(url_for('home'))


@app2.route('/update_invoice', methods=['GET', 'POST'])
def update_invoice():
    "this function handles the editing of an invoice by the employee"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):

        if request.method == 'POST':
            serial_number = request.form['serial_number']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            issue_date = request.form['issue_date']
            payment = request.form['payment']
            speed = request.form['speed']
            serial_id = request.form['serial_id']
            state = request.form['state']

            if not str(serial_id).isnumeric():
                flash('Serial_id must contain only numbers !', 'danger')

            else:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE  invoices_pay SET start_date=%s, end_date=%s,issue_date=%s,payment=%s,internet_speed=%s,state=%s  WHERE serial_number=%s",
                    (start_date, end_date, issue_date, payment, speed, state, serial_number))
                conn.commit()
                cursor.close()
                flash("Invoice Updated Successfully", 'success')

            return redirect(url_for('edit_invoices'))
    else:
        return redirect(url_for('home'))


@app2.route('/delete_Invoice/<id>/', methods=['GET', 'POST'])
def delete_Invoice(id):
    "this function foe deleting an invoice from the database"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("delete from invoices_pay where serial_number = '" + id + "'")
        conn.commit()
        cursor.close()

        flash("Invoice Deleted Successfully", 'success')

        return redirect(url_for('edit_invoices'))
    else:
        return redirect(url_for('home'))


@app2.route("/employee/edit_speed")
def edit_speed():
    "open the page of speeds in the company"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):
        cursor = conn.cursor()
        cursor.execute("select * from  speed_price")
        speed = cursor.fetchall()
        cursor.close()
        speed_1 = list(speed)
        return render_template("edit_price.html", type=in_user[7], speeds=speed_1,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


@app2.route('/update_speed', methods=['GET', 'POST'])
def update_speed():
    "edites the data of the speeds"

    if 'user_id' in session and (in_user[7] == 'ep' or in_user[7] == 'et'):

        if request.method == 'POST':
            speed = request.form['speed']
            price = request.form['price']

            if not str(price).isnumeric():
                flash('Price must contain only numbers !', 'danger')

            else:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE speed_price SET price=%s WHERE speed=%s",
                    (price, speed))
                conn.commit()
                cursor.close()
                flash("Speed Updated Successfully", 'success')

            return redirect(url_for('edit_speed'))
    else:
        return redirect(url_for('home'))


@app2.route("/employee/edit_project")
def edit_project():
    "open the page of projects"

    if 'user_id' in session and (in_user[7] == 'ep'):
        cursor = conn.cursor()
        cursor.execute("select * from project")
        project = cursor.fetchall()
        cursor.close()
        project_1 = list(project)
        return render_template("edit_project.html", projects=project_1,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


@app2.route('/insert_project', methods=['POST'])
def insert_project():
    "creates a new project (by the admin)"

    if 'user_id' in session and (in_user[7] == 'ep'):

        if request.method == 'POST':
            title = request.form['title']
            start_date = request.form['start_date']
            end_date = request.form['end_date']

            if end_date == "":
                end_date = None

            l = []
            l.append(title)
            l.append(start_date)
            l.append(end_date)

            cursor = conn.cursor()
            cursor.execute(
                "insert into project (title,start_date,end_date) values(%s,%s,%s)",
                (title, start_date, end_date))
            flash("Project Inserted Successfully", 'success')
            conn.commit()
            cursor.close()

            return redirect(url_for('edit_project'))

    else:
        return redirect(url_for('home'))


@app2.route('/update_project', methods=['GET', 'POST'])
def update_project():
    "edites the data of a project (by the admin)"

    if 'user_id' in session and (in_user[7] == 'ep'):

        if request.method == 'POST':
            project_id = request.form['project_id']
            title = request.form['title']
            start_date = request.form['start_date']
            end_date = request.form['end_date']

            if end_date == "":
                end_date = None

            cursor = conn.cursor()
            cursor.execute(
                "UPDATE project SET title=%s,start_date=%s,end_date=%s WHERE project_id=%s",
                (title, start_date, end_date, project_id))
            conn.commit()
            cursor.close()
            flash("Project Updated Successfully", 'success')

            return redirect(url_for('edit_project'))
    else:
        return redirect(url_for('home'))


@app2.route('/delete_project/<Project>/', methods=['GET', 'POST'])
def delete_project(Project):
    "deletes a project from the company"

    if 'user_id' in session and (in_user[7] == 'ep'):
        cursor = conn.cursor()
        cursor.execute("delete from project where project_id = '" + Project + "'")
        conn.commit()
        cursor.close()

        flash("Project Deleted Successfully", 'success')

        return redirect(url_for('edit_project'))
    else:
        return redirect(url_for('home'))


@app2.route("/livesearch", methods=["POST", "GET"])
def livesearch():
    "live search by name or serial_id the employee page"

    searchbox = str(request.form.get("text"))

    print("kkkkkkkkkkkkkkkkkkkkkk")
    print(searchbox)
    cursor = conn.cursor()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    result = []
    if str(searchbox).isnumeric():
        cursor.execute("select * from customer_link where serial_id LIKE '" + searchbox + "%'")
        result = cursor.fetchall()
        cursor.close()
    else:
        cursor.execute("select * from customer_link where customer_name LIKE '" + searchbox + "%'")
        result = cursor.fetchall()
        cursor.close()

    print(result)
    return jsonify(result)


@app2.route("/livesearch2", methods=["POST", "GET"])
def livesearch2():
    "live search in the invoices page (employees page)"

    searchbox = str(request.form.get("text"))

    print("kkkkkkkkkkkkkkkkkkkkkk")
    print(searchbox)
    cursor = conn.cursor()
    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    result = []

    cursor.execute("select * from invoices_pay where serial_number LIKE '" + searchbox + "%'")
    result = cursor.fetchall()
    cursor.close()

    print(result)
    return jsonify(result)


# End of Employee Page
# ------------------------------------------------------------------------------------------

#  Customer Page
# ------------------------------------------------------------------------------------------
@app2.route("/Customer/Help", methods=['GET', 'POST'])
def Help():
    "open the page oh helps for the customer (customers only)"

    if 'user_id' in session and in_user[7] == "c":
        print(in_user[6])
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer_link WHERE telephone_number ='" + in_user[6] + "'")
        customer = cursor.fetchone()
        if customer is not None:
            customer_1 = list(customer)
            print(customer_1)
            cursor.execute("SELECT * FROM need_help WHERE serial_id ='" + str(customer[0]) + "'")
            helps2 = (cursor.fetchall())
            helps = []
            for x in helps2:
                helps.append(list(x))

            print(helps)
            ready = []
            for x in range(0, len(helps)):
                tmp = []
                tmp.append(helps[x][5])
                date1 = helps[x][0]
                str_date = date1.strftime("%Y/%m/%d")
                tmp.append(str_date)
                cursor.execute("SELECT * FROM employee_work WHERE Employee_id ='" + str(helps[x][3]) + "'")
                helps_1 = list(cursor.fetchone())
                tmp.append(helps_1[1])
                tmp.append(helps_1[0])
                tmp.append(helps[x][1])
                tmp.append(helps[x][4])
                ready.append(tmp)
            cursor.close()

            return render_template("help.html", helps=ready, user_name=str(in_user[2]) + " " + str(in_user[3]))

        else:
            return redirect(url_for('new_customer'))

    else:
        return redirect(url_for('home'))


@app2.route("/Customer/invoices", methods=['GET', 'POST'])
def Invoices():
    "open the page of the invoices for the customer (customers only)"

    print("entered invo")

    if 'user_id' in session and in_user[7] == "c":
        print("hihi")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customer_link WHERE telephone_number ='" + in_user[6] + "'")
        customer = cursor.fetchone()

        if customer is not None:
            cursor.execute("SELECT * FROM invoices_pay WHERE serial_id ='" + str(customer[0]) + "'")
            invoices_2 = list(cursor.fetchall())
            invoices = []
            for x in invoices_2:
                invoices.append(list(x))

            for x in invoices:
                print(x)
                date1 = x[1]
                x[1] = date1.strftime("%Y/%m/%d")
                date2 = x[2]
                x[2] = date2.strftime("%Y/%m/%d")
                date3 = x[3]
                x[3] = date3.strftime("%Y/%m/%d")

            return render_template("invoices.html", invoices=invoices,
                                   user_name=str(in_user[2]) + " " + str(in_user[3]))

        else:
            return redirect(url_for('Help'))

    else:
        return redirect(url_for('home'))


@app2.route("/Customer/settings", methods=['GET', 'POST'])
def Settings():
    "open the settings page for the customer (can change the password)"

    print("sdhsjd")
    if 'user_id' in session and in_user[7] == "c":
        if request.method == 'POST':
            old_password = request.form['oldPassword1']
            new_password = str(request.form["newPassword"])
            re_new_password = str(request.form["confirmPassword"])

            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username ='" + in_user[1] + "' and password1='" + hashlib.md5(
                old_password.encode()).hexdigest() + "'")
            user_pass = cursor.fetchone()
            cursor.close()
            if user_pass is not None and new_password == re_new_password:
                cursor2 = conn.cursor()
                cursor2.execute(
                    "UPDATE users SET password1='" + hashlib.md5(
                        new_password.encode()).hexdigest() + "' WHERE email='" +
                    in_user[0] + "'")
                conn.commit()
                cursor2.close()
                flash("Password Updated Successfully", 'success')

            else:
                flash('OLd password is incorrect !', 'danger')

            return redirect(url_for('Settings'))

        else:
            print("didnt enter")
            return render_template("settings.html", user_name=str(in_user[2]) + " " + str(in_user[3]))

    else:
        return redirect(url_for('home'))


@app2.route('/up/<id>', methods=['GET', 'POST'])
def Up(id):
    "a function to handle the good rating in the help page"

    if 'user_id' in session and in_user[7] == "c":
        print("hello")

        cursor = conn.cursor()

        cursor.execute("select rating from need_help where help_id ='" + id + "'")
        rating = cursor.fetchone()

        if rating[0] != 'good':
            cursor.execute(
                "UPDATE need_help SET rating= 'good' WHERE help_id='" +
                id + "'")
            conn.commit()
            cursor.execute(
                "select t.points from technical_support t, need_help n where n.employee_id=t.employee_id and n.help_id ='" + id + "'")
            points = cursor.fetchone()
            points2 = points[0]
            points2 += 1
            cursor.execute(
                "select t.Employee_id from technical_support t, need_help n where n.employee_id=t.employee_id and n.help_id ='" + id + "'")
            emp_id = cursor.fetchone()
            cursor.execute(
                "UPDATE technical_support SET points= '" + str(points2) + "' WHERE Employee_id='" +
                str(emp_id[0]) + "'")
            conn.commit()

            flash("Updated Successfully", 'success')

        cursor.close()

        print("up")
        return redirect(url_for('Help'))

    else:
        return redirect(url_for('home'))


@app2.route('/Customer/down/<id>', methods=['GET', 'POST'])
def Down(id):
    "a function to handle the bad rating in the help page"

    if 'user_id' in session and in_user[7] == "c":
        print("hello")

        cursor = conn.cursor()

        cursor.execute("select rating from need_help where help_id ='" + id + "'")
        rating = cursor.fetchone()

        if rating[0] != 'bad':
            cursor.execute(
                "UPDATE need_help SET rating= 'bad' WHERE help_id='" +
                id + "'")
            conn.commit()
            cursor.execute(
                "select t.points from technical_support t, need_help n where n.employee_id=t.employee_id and n.help_id ='" + id + "'")
            points = cursor.fetchone()
            points2 = points[0]
            points2 -= 1
            cursor.execute(
                "select t.Employee_id from technical_support t, need_help n where n.employee_id=t.employee_id and n.help_id ='" + id + "'")
            emp_id = cursor.fetchone()
            cursor.execute(
                "UPDATE technical_support SET points= '" + str(points2) + "' WHERE Employee_id='" +
                str(emp_id[0]) + "'")
            conn.commit()

            flash("Updated Successfully", 'success')

            print("points - 1")

        cursor.close()

        print("down")
        return redirect(url_for('Help'))

    else:
        return redirect(url_for('home'))


@app2.route("/Customer/new_customer", methods=['GET', 'POST'])
def new_customer():
    "subscription for the customer when opening a page for subscripers only"

    print("sdhsjd")
    if 'user_id' in session and in_user[7] == "c":
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM branch ")
        branches1 = list(cursor.fetchall())
        cursor.close()

        cursor = conn.cursor()
        cursor.execute("SELECT * FROM speed_price ")
        prices = list(cursor.fetchall())
        cursor.close()

        return render_template("new_customer.html", branches=branches1, prices=prices)

    else:
        return redirect(url_for('home'))


# this route is for inserting data to mysql database via html forms
@app2.route('/insert2', methods=['POST'])
def insert2():
    "insert the customer when subscribing online"
    if 'user_id' in session and in_user[7] == "c":

        if request.method == 'POST':
            id_ = request.form['id_']
            name = (str(in_user[2]) + " " + str(in_user[3])).title()
            phone = in_user[6]
            speed = request.form['speed']
            category = 'Bronze'
            duration = request.form['duration']
            address = in_user[5]
            branch = request.form['branch']
            payment = str(request.form['Payment'])
            payment = payment.replace('$', '')

            l = []
            l.append(id_)
            l.append(name)
            l.append(phone)
            l.append(speed)
            l.append(category)
            l.append(duration)
            l.append(address)
            l.append(branch)

            print(l)

            fetched_id = []

            if str(id_).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM customer_link WHERE id = % s', (id_,))
                fetched_id = cursor.fetchall()
                cursor.close()

            # for x in fetched_id:
            # 	if str(x[0]) == str(id_):
            # 		flag = int(1)
            # 		break
            if fetched_id:
                flash('This Person already exist !', 'danger')

            elif not str(id_).isnumeric():
                flash('ID must contain only numbers !', 'danger')

            elif not bool(re.match('[a-zA-Z\s]+$', name)):
                flash('The name must contain letters only !', 'danger')

            elif not str(phone).isnumeric():
                flash('Phone Number must contain only numbers !', 'danger')

            elif not str(duration).isnumeric():
                flash('Duration must contain only numbers !', 'danger')

            else:

                cursor = conn.cursor()
                cursor.execute("SELECT CURDATE()")
                today = cursor.fetchone()
                print(today)
                cursor.execute(
                    "insert into customer_link(id,customer_name,telephone_number,internet_speed,category,start_date,addres , branch_number,line_status) values(%s,%s,%s,%s,%s,%s,%s,%s,%s )",
                    (id_, name, phone, speed, category, today[0], address, branch, "Active"))
                conn.commit()
                cursor.close()
                flash("Customer Inserted Successfully", 'success')

                # now_date = datetime.now()
                # now_date_sec = now_date.timestamp()
                # print(now_date_sec)
                # new_date_sec = now_date_sec + int(duration) * 30 * 86400
                # new_date = datetime.fromtimestamp(new_date_sec)
                # now_date = now_date.date()
                # new_date = new_date.date()
                # now_date2 = now_date.strftime("%Y-%m-%d")
                # new_date2 = new_date.strftime("%Y-%m-%d")
                # print(now_date2)
                # print(new_date2)

                today = date.today()
                d1 = today.strftime("%Y-%m-%d")
                d2 = d1.split("-")
                start_date = date(int(d2[0]), int(d2[1]), int(d2[2]))
                x1 = int((int(d2[1]) + int(duration) - 1) / 12)
                x2 = int((int(d2[1]) + int(duration)) % 12)
                if x2 == 0:
                    x2 = 12

                end_date = date(int(int(d2[0]) + x1), x2, int(d2[2]))

                cursor = conn.cursor()
                cursor.execute(" select serial_id from customer_link where telephone_number = '" + phone + "'")
                serial = cursor.fetchone()
                print(serial[0])
                print(payment)
                cursor.close()

                cursor = conn.cursor()
                cursor.execute(
                    "insert into invoices_pay(start_date,end_date,issue_date,payment,internet_speed,serial_id,state) values(%s,%s,%s,%s,%s,%s,%s)",
                    (today, end_date, today, float(payment), speed, serial[0], "Paid"))
                print(serial)
                conn.commit()
                cursor.close()

            return redirect(url_for('Personal_info'))

    else:
        return redirect(url_for('home'))


@app2.route("/Customer/need_help", methods=['GET', 'POST'])
def need_help():
    "this function adds a complain by the employee"

    print("sdhsjd")
    if 'user_id' in session and in_user[7] == "c":
        if request.method == 'POST':
            problem = request.form['problem']
            type = str(request.form["type"])
            need_visit = str(request.form["visit"])
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customer_link WHERE telephone_number ='" + in_user[6] + "'")
            customer = cursor.fetchone()

            cursor = conn.cursor()
            cursor.execute("insert into complains (complain, type_help , Customer_id , visit ) values(%s,%s,%s,%s )",
                           (problem, type, customer[0], need_visit))
            conn.commit()
            cursor.close()
            print(problem)
            print(type)
            flash("your complain was sent and technical support will contact you as soon as possible", 'success')
            return render_template('help.html')
        else:
            return redirect(url_for('need_help'))

    else:
        return redirect(url_for('home'))


# End of Customer Page
# ------------------------------------------------------------------------------------------


# Admin Page
# ------------------------------------------------------------------------------------------

@app2.route('/admin')
def Admin_1():
    "open the main page for the admin (the bi maneger)"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute('select distinct * from  employee_work')
        data = cur.fetchall()
        cur.execute('select  * from  branch')
        branches = cur.fetchall()
        cur.execute('select  * from  project')
        projects = cur.fetchall()

        return render_template('admin_1.html', employee=data, branches=branches, projects=projects)
    else:
        return redirect(url_for('home'))


@app2.route('/add_contact', methods=['POST'])
def add_employee():
    "this function adds an employee by the admin"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur_2 = conn.cursor()
        fetched_id = None
        if request.method == 'POST':
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            id_ = request.form['id']
            branch_num = request.form['branch_num']
            s_date = request.form['s.date']
            salary = request.form['salary']
            noh = request.form['noh']
            type = request.form['speed']

            if str(id_).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM employee_work WHERE Employee_id = % s', (id_,))
                fetched_id = cursor.fetchall()
                cursor.close()

            if fetched_id:
                flash('This Person already exist !', 'danger')

            elif not str(id_).isnumeric():
                flash('ID must contain only numbers !', 'danger')

            elif not bool(re.match('[a-zA-Z \s]+$', first_name)):
                flash('The first name must contain letters only !', 'danger')

            elif not bool(re.match('[a-zA-Z \s]+$', last_name)):
                flash('The last name must contain letters only !', 'danger')

            elif not str(salary).isnumeric():
                flash('Salary Number must contain only numbers !', 'danger')

            elif not str(noh).isnumeric():
                flash('Duration must contain only numbers !', 'danger')

            else:
                cur.execute(
                    "INSERT INTO employee_work (first_name,last_name ,branch_number,id,start_date,salary,num_of_holidays) VALUES (% s, % s, % s, % s, % s, % s,% s)",
                    (first_name, last_name, branch_num, id_, s_date, salary, noh))
                conn.commit()
                cur.execute("select Employee_id from employee_work where id = '" + id_ + "'")
                emp_id = cur.fetchone()
                change_branch()
                make_email(first_name, last_name, emp_id, id_, type)

                if type == "Technical":
                    points = request.form['points']
                    if not str(points).isnumeric():
                        flash('Phone Number must contain only numbers !', 'danger')
                        return redirect(url_for('Admin_1'))
                    else:
                        cur.execute("INSERT INTO technical_support (employee_id, points) VALUES (%s, % s)",
                                    (emp_id, points))
                    conn.commit()
                elif type == "Janitor":
                    tool = request.form['tool']
                    cur_2.execute("INSERT INTO janitor (employee_id,tool) VALUES ( % s, % s)", (emp_id, tool))
                    conn.commit()

                elif type == "Programmer":
                    skill = request.form['skill']
                    project_id = request.form['Project_id']
                    if not str(project_id).isnumeric():
                        flash('Phone Number must contain only numbers !', 'danger')
                        return redirect(url_for('Admin_1'))
                    else:
                        cur_2.execute(
                            "INSERT INTO programmer (skill,project_id, employee_id) VALUES ( % s,% s ,% s)",
                            (skill, project_id, emp_id))

                flash('Employee Added successfully', 'success')
                return redirect(url_for('Admin_1'))
            return redirect(url_for('Admin_1'))
    else:
        return redirect(url_for('home'))


@app2.route('/employee/edit/<id>', methods=['POST', 'GET'])
def get_employee(id):
    "get the data of the employee to edit them"
    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute("select distinct * from  employee_work  where Employee_id = '" + id + "'")
        data = cur.fetchall()
        cur.execute('select  * from  branch')
        branches = cur.fetchall()
        cur.close()
        return render_template('edit.html', employee=data, branches=branches)

    else:
        return redirect(url_for('home'))


@app2.route('/employee/update/<id>', methods=['POST'])
def update_employee(id):
    "this function edites the information of the employee"

    if 'user_id' in session and in_user[7] == "a":

        cur_2 = conn.cursor()
        if request.method == 'POST':
            emp_Id = request.form['emp_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            branch_num = request.form['branch_num']
            id_ = request.form['id']
            s_date = request.form['s_date']
            salary = request.form['salary']
            noh = request.form['noh']

            if not bool(re.match('[0-9.\s]+$', salary)):
                flash(' Salary must contain only numbers !', 'danger')
                return redirect(url_for('get_employee', id=id))
            elif not str(noh).isnumeric():
                flash('Number of holidays must contain only numbers !', 'danger')
                return redirect(url_for('get_employee', id=id))
            elif not bool(re.match('[a-zA-Z \s]+$', first_name)):
                flash('The first name must contain letters only !', 'danger')
                return redirect(url_for('get_employee', id=id))
            elif not bool(re.match('[a-zA-Z \s]+$', last_name)):
                flash('The last name must contain letters only !', 'danger')
                return redirect(url_for('get_employee', id=id))

            else:
                cur = conn.cursor()
                print(s_date)
                cur.execute(
                    "UPDATE employee_work SET first_name  = %s,last_name  = %s, Branch_number = %s,start_date = %s,salary = %s,num_of_holidays = %s  WHERE Employee_id = %s",
                    (first_name, last_name, branch_num, s_date, salary, noh, id))
                conn.commit()
                change_branch()
                flash('Employee Updated Successfully', 'success')
                return redirect(url_for('Admin_1'))

    else:
        return redirect(url_for('home'))


@app2.route('/employee/delete/<string:id>', methods=['POST', 'GET'])
def delete_employee(id):
    "DeActivaes an employee (by the admin)"

    if 'user_id' in session and in_user[7] == "a":

        cur = conn.cursor()
        cur.execute("update employee_work set state = 'InActive' where Employee_id = '" + id + "'")
        conn.commit()
        change_branch()
        flash('Employee DeActivated Successfully', 'success')
        return redirect(url_for('Admin_1'))

    else:
        return redirect(url_for('home'))


@app2.route('/employee/activate/<string:id>', methods=['POST', 'GET'])
def activate_employee(id):
    "Activates the employee (by the admin)"
    if 'user_id' in session and in_user[7] == "a":

        cur = conn.cursor()
        cur.execute("update employee_work set state = 'Active' where Employee_id = '" + id + "'")
        conn.commit()
        change_branch()
        flash('Employee Activated Successfully', 'success')
        return redirect(url_for('Admin_1'))

    else:
        return redirect(url_for('home'))


@app2.route('/admin/Depentents')
def Depentents():
    "the page to show the dependents of the employees"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute(
            'select d.dependents_id , d.dependents_name , d.dependents_dob, d.Employee_id,e.first_name, e.last_name from employee_work e, dependents_has d where e.Employee_id=d.Employee_id ')
        data = cur.fetchall()

        return render_template('dependents.html', dependents=data)

    else:
        return redirect(url_for('home'))


@app2.route('/admin/add_Depentents', methods=['POST'])
def add_dependents():
    "insert a new dependent for an employee"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        if request.method == 'POST':
            dep_id = request.form['Dependents_ID']
            name = request.form['Name']
            dob = request.form['dob']
            emp_id = request.form['Employee_ID']

            if str(dep_id).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM dependents_has WHERE dependents_id = % s', (dep_id,))
                fetched_id = cursor.fetchall()
                cursor.close()

            if str(emp_id).isnumeric():
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM employee_work WHERE Employee_id = % s', (emp_id,))
                fetched_id2 = cursor.fetchall()
                cursor.close()

            if fetched_id:
                flash('This Person already exist !', 'danger')

            elif not bool(re.match('[a-zA-Z \s]+$', name)):
                flash('The name must contain letters only !', 'danger')


            elif not str(emp_id).isnumeric():
                flash('Employee ID must contain only numbers !', 'danger')

            elif not fetched_id2:
                flash('This Employee does not exist !', 'danger')

            else:
                cur.execute(
                    "INSERT INTO dependents_has (dependents_id,dependents_name,dependents_dob,Employee_id) VALUES ( % s, % s, % s, % s)",
                    (dep_id, name, dob, emp_id))
                conn.commit()
                flash('Employee Added successfully', 'success')
                return redirect(url_for('Depentents'))
            return redirect(url_for('Depentents'))

    else:
        return redirect(url_for('home'))


@app2.route('/admin/Depentents/edit/<id>', methods=['POST', 'GET'])
def get_dependents(id):
    "gets the data of the dependent to edit them"

    if 'user_id' in session and in_user[7] == "a":

        cur = conn.cursor()
        cur.execute("SELECT * FROM dependents_has WHERE dependents_id = '" + id + "'")
        data = cur.fetchall()
        cur.close()
        return render_template('edit_dependent.html', dependent=data)

    else:
        return redirect(url_for('home'))


@app2.route('/admin/Depentents/update/<id>', methods=['POST'])
def update_dependents(id):
    "edites the data of the dependents (by the admin)"

    if 'user_id' in session and in_user[7] == "a":
        if request.method == 'POST':
            dep_id = request.form['Dependents_ID']
            name = request.form['Name']
            age = request.form['dob']
            emp_id = request.form['Employee_ID']

            cur = conn.cursor()
            cur.execute(
                "UPDATE dependents_has SET dependents_id = %s, dependents_name = %s, dependents_dob = %s,Employee_id = %s WHERE dependents_id = %s",
                (dep_id, name, age, emp_id, int(dep_id)))

            # 			(emp_name,emp_Id,branch_num,id_,s_date,salary,noh))
            flash('Employee Updated Successfully', 'success')
            conn.commit()
            return redirect(url_for('Depentents'))

    else:
        return redirect(url_for('home'))


@app2.route('/admin/Depentents/delete/<string:id>', methods=['POST', 'GET'])
def delete_dependents(id):
    "deletes the dependent (by the admin)"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute("delete from dependents_has where dependents_id = '" + id + "'")
        conn.commit()
        flash('Employee Removed Successfully', 'success')
        return redirect(url_for('Depentents'))
    else:
        return redirect(url_for('home'))


@app2.route('/admin/technical')
def technical():
    "the page to show the technical support employees"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute(
            'select t.internal_number, t.employee_id, t.points, e.first_name, e.last_name from employee_work e, technical_support t where e.Employee_id=t.Employee_id')
        data = cur.fetchall()
        return render_template('technical.html', employee=data)
    else:
        return redirect(url_for('home'))


@app2.route('/admin/technical/edit/<id>', methods=['POST', 'GET'])
def get_technical(id):
    "gets the data of the technical to edit them"
    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute("select distinct * from  employee_work  where Employee_id = '" + id + "'")
        data = cur.fetchall()
        cur.execute('select  * from  branch')
        branches = cur.fetchall()
        cur.execute("select  * from  technical_support where Employee_id = '" + id + "'")
        tech1 = cur.fetchone()
        cur.close()
        return render_template('edit_technical.html', employee=data, branches=branches, tech=tech1)
    else:
        return redirect(url_for('home'))


@app2.route('/admin/technical/update/<id>', methods=['POST'])
def update_technical(id):
    "edites the data of the technical (by the admin)"

    if 'user_id' in session and in_user[7] == "a":
        cur_2 = conn.cursor()
        if request.method == 'POST':
            emp_Id = request.form['emp_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            branch_num = request.form['branch_num']
            id_ = request.form['id']
            s_date = request.form['s_date']
            salary = request.form['salary']
            noh = request.form['noh']
            points = request.form['points']
            internal_number = request.form['internal_number']

            if not bool(re.match('[0-9.\s]+$', salary)):
                flash(' Salary must contain only numbers !', 'danger')
                return redirect(url_for('get_technical', id=id))
            elif not str(noh).isnumeric():
                flash('Number of holidays must contain only numbers !', 'danger')
                return redirect(url_for('get_technical', id=id))
            elif not bool(re.match('[a-zA-Z \s]+$', first_name)):
                flash('The first name must contain letters only !', 'danger')
                return redirect(url_for('get_technical', id=id))
            elif not bool(re.match('[a-zA-Z \s]+$', last_name)):
                flash('The last name must contain letters only !', 'danger')
                return redirect(url_for('get_technical', id=id))
            elif not str(points).isnumeric():
                flash('Number of points must contain only numbers !', 'danger')
                return redirect(url_for('get_technical', id=id))
            else:
                cur = conn.cursor()
                print(s_date)
                cur.execute(
                    "UPDATE employee_work SET first_name  = %s,last_name  = %s, Branch_number = %s,start_date = %s,salary = %s,num_of_holidays = %s  WHERE Employee_id = %s",
                    (first_name, last_name, branch_num, s_date, salary, noh, id))
                conn.commit()

                cur.execute(
                    "UPDATE technical_support SET  points = %s  WHERE Employee_id = %s",
                    (points, id))
                conn.commit()

                change_branch()

                flash('Employee Updated Successfully', 'success')
                return redirect(url_for('technical'))
    else:
        return redirect(url_for('home'))


@app2.route('/admin/programmer')
def programmer():
    "the page to show the programmers"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute(
            'select  p.skill, p.project_id, p.Employee_id,e.first_name, e.last_name from employee_work e, programmer p where e.Employee_id=p.Employee_id')
        data = cur.fetchall()
        return render_template('programmer.html', programmer=data)
    else:
        return redirect(url_for('home'))


@app2.route('/admin/programmer/edit/<id>', methods=['POST', 'GET'])
def get_programmer(id):
    "gets the data of the programmer to edit them"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute("select distinct * from  employee_work  where Employee_id = '" + id + "'")
        data = cur.fetchall()
        cur.execute('select  * from  branch')
        branches = cur.fetchall()
        cur.execute("select distinct * from  programmer  where Employee_id = '" + id + "'")
        prog1 = cur.fetchone()
        cur.execute("select * from  project")
        project = cur.fetchall()
        cur.close()
        return render_template('edit_programmer.html', employee=data, branches=branches, prog=prog1, projects=project)
    else:
        return redirect(url_for('home'))


@app2.route('/admin/programmer/update/<id>', methods=['POST'])
def update_programmer(id):
    "edites the data of the programmer (by the admin)"

    if 'user_id' in session and in_user[7] == "a":
        cur_2 = conn.cursor()
        if request.method == 'POST':
            emp_Id = request.form['emp_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            branch_num = request.form['branch_num']
            id_ = request.form['id']
            s_date = request.form['s_date']
            salary = request.form['salary']
            noh = request.form['noh']
            skill = request.form['skill']
            project_id = request.form['project_id']

            if not bool(re.match('[0-9.\s]+$', salary)):
                flash(' Salary must contain only numbers !', 'danger')
                return redirect(url_for('get_programmer', id=id))
            elif not str(project_id).isnumeric():
                flash('Project id must contain only numbers !', 'danger')
                return redirect(url_for('get_programmer', id=id))
            elif not bool(re.match('[a-zA-Z \s]+$', first_name)):
                flash('The first name must contain letters only !', 'danger')
                return redirect(url_for('get_programmer', id=id))
            elif not bool(re.match('[a-zA-Z \s]+$', last_name)):
                flash('The last name must contain letters only !', 'danger')
                return redirect(url_for('get_programmer', id=id))
            elif not bool(re.match('[a-z A-Z.\s]+$', skill)):
                flash('Skills must be strings !', 'danger')
                return redirect(url_for('get_programmer', id=id))
            elif not str(noh).isnumeric():
                flash('Number of holidays must contain only numbers !', 'danger')
                return redirect(url_for('get_programmer', id=id))
            else:
                cur = conn.cursor()
                print(s_date)
                cur.execute(
                    "UPDATE employee_work SET first_name  = %s,last_name  = %s, Branch_number = %s,start_date = %s,salary = %s,num_of_holidays = %s  WHERE Employee_id = %s",
                    (first_name, last_name, branch_num, s_date, salary, noh, id))
                conn.commit()
                cur.execute(
                    "UPDATE programmer SET skill  = %s, project_id = %s",
                    (skill, project_id))
                conn.commit()
                change_branch()
                flash('Employee Updated Successfully', 'success')
                return redirect(url_for('programmer'))
    else:
        return redirect(url_for('home'))


@app2.route('/admin/janitor')
def janitor():
    "the page to show the janitors"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute(
            'select  j.tool, j.Employee_id,e.first_name, e.last_name from employee_work e, janitor j where e.Employee_id=j.Employee_id')
        data = cur.fetchall()
        print(data)
        return render_template('janitor.html', employee=data)
    else:
        return redirect(url_for('home'))


@app2.route('/admin/janitor/edit/<id>', methods=['POST', 'GET'])
def get_janitor(id):
    "gets the data of the janitor to edit them"

    if 'user_id' in session and in_user[7] == "a":
        cur = conn.cursor()
        cur.execute("select distinct * from  employee_work  where Employee_id = '" + id + "'")
        data = cur.fetchall()
        cur.execute('select  * from  branch')
        branches = cur.fetchall()
        cur.execute("select distinct * from janitor where Employee_id = '" + id + "'")
        jan1 = cur.fetchone()
        cur.close()
        return render_template('edit_janitor.html', employee=data, branches=branches, jan=jan1)
    else:
        return redirect(url_for('home'))


@app2.route('/admin/janitor/update/<id>', methods=['POST'])
def update_janitor(id):
    "edites the data of the janitor (by the admin)"

    if 'user_id' in session and in_user[7] == "a":
        cur_2 = conn.cursor()
        if request.method == 'POST':
            emp_Id = request.form['emp_id']
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            branch_num = request.form['branch_num']
            id_ = request.form['id']
            s_date = request.form['s_date']
            salary = request.form['salary']
            noh = request.form['noh']
            tool = request.form['tool']

            if not bool(re.match('[0-9.\s]+$', salary)):
                flash(' Salary must contain only numbers !', 'danger')
                return redirect(url_for('get_janitor', id=id))


            elif not str(noh).isnumeric():
                flash('Number of holidays must contain only numbers !', 'danger')
                return redirect(url_for('get_janitor', id=id))

            elif not bool(re.match('[a-z A-Z.\s]+$', first_name)):
                flash('Employee first name must be strings !', 'danger')
                return redirect(url_for('get_janitor', id=id))
            elif not bool(re.match('[a-z A-Z.\s]+$', last_name)):
                flash('Employee last name must be strings !', 'danger')
                return redirect(url_for('get_janitor', id=id))

            else:
                cur = conn.cursor()
                print(s_date)
                cur.execute(
                    "UPDATE employee_work SET first_name  = %s,last_name  = %s, Branch_number = %s,start_date = %s,salary = %s,num_of_holidays = %s  WHERE Employee_id = %s",
                    (first_name, last_name, branch_num, s_date, salary, noh, id))
                conn.commit()
                cur.execute(
                    "UPDATE janitor SET  tool = %s  WHERE Employee_id = %s",
                    (tool, id))
                conn.commit()
                change_branch()
                flash('Employee Updated Successfully', 'success')
                return redirect(url_for('janitor'))
    else:
        return redirect(url_for('home'))


@app2.route("/admin/edit_branch")
def edit_branch():
    "open the page of the branches of the company"

    if 'user_id' in session and in_user[7] == "a":
        cursor = conn.cursor()
        cursor.execute("select * from branch")
        branch = cursor.fetchall()
        cursor.close()
        branch_1 = list(branch)
        return render_template("edit_branch.html", branches=branch_1,
                               user_name=str(in_user[2]) + " " + str(in_user[3]))
    else:
        return redirect(url_for('home'))


@app2.route('/insert_branch', methods=['POST'])
def insert_branch():
    "adds a new branch (by the admin)"

    if 'user_id' in session and in_user[7] == "a":

        if request.method == 'POST':
            branch_number = request.form['bn']
            address = request.form['address']
            phone_number = request.form['phone']

            l = []
            l.append(branch_number)
            l.append(address)
            l.append(phone_number)

            if not str(branch_number).isnumeric():
                flash('Branch Number contain only numbers !', 'danger')

            elif not str(phone_number).isnumeric():
                flash('Phone Number  must contain only numbers !', 'danger')

            else:
                cursor = conn.cursor()
                cursor.execute(
                    "insert into branch (branch_number, addres,number_Employees ,phone_number) values(%s,%s,%s,%s )",
                    (branch_number, address, 0, phone_number))
                flash("Branch Inserted Successfully", 'success')
                conn.commit()
                cursor.close()

            return redirect(url_for('edit_branch'))

    else:
        return redirect(url_for('home'))


@app2.route('/update_branch', methods=['GET', 'POST'])
def update_branch():
    "edites the data of a branch"

    if 'user_id' in session and in_user[7] == "a":

        if request.method == 'POST':
            branch_number = request.form['bn']
            address = request.form['address']
            phone_number = request.form['phone']

            if not str(phone_number).isnumeric():
                flash('phone_number must contain only numbers !', 'danger')

            else:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE branch SET  addres=%s,phone_number=%s WHERE branch_number=%s",
                    (address, phone_number, branch_number))
                conn.commit()
                cursor.close()
                flash("Branch Updated Successfully", 'success')

            return redirect(url_for('edit_branch'))
    else:
        return redirect(url_for('home'))


# End of Admin Page
# ------------------------------------------------------------------------------------------


if __name__ == "__main__":
    app2.run(debug=True)
