import csv
import datetime
import pytz
import requests
import subprocess
import urllib
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                            ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def strong_password(password):
    if len(password) < 8:
        return False
    if " " in password:
        return False
    big_char = [chr(i) for i in range(65 , 90)]
    small_char = [chr(i) for i in range(97 , 122)]
    chars = ["@" ,"!" , "#" , "$" , "%" , "&" , "*" ,"(" , ")"]
    nums = [f"{i}" for i in range(10)]
    check = [big_char , small_char , chars , nums]
    ''
    q = 0
    for i in check:
        for letter in password:
            if letter in i :
                q += 1
                break
    if q >= 4:
        return True
    else:
        return False
    

def plan(calories , n_meals):
    chr_options = Options()
    chr_options.headless = True
    chr_options.add_experimental_option("detach", True)
    chr_driver = webdriver.Chrome(options=chr_options)
    chr_driver.get("https://www.eatthismuch.com/")
    chr_driver.implicitly_wait(3)
    try :
        input_calories = chr_driver.find_element(By.XPATH ,'//*[@id="cal_input"]')
        input_calories.send_keys(calories)
        input_num_meals = chr_driver.find_element(By.XPATH , '//*[@id="num_meals_selector"]')
        input_num_meals.send_keys(n_meals)
        submit = chr_driver.find_element(By.XPATH , '//*[@id="main_container"]/div/div[2]/div[1]/div[2]/div[6]/div/button')
        submit.click()
    except :
        return False
    meals = {}
    wait = WebDriverWait(chr_driver , 10)
    # table = chr_driver.find_element(By.XPATH , './/*[@id="main_container"]/div/div[4]/div[1]/div[1]/div')
    table = wait.until(EC.visibility_of_element_located((By.XPATH ,'.//*[@id="main_container"]/div/div[4]/div[1]/div[1]/div' )))
    cal_amount = table.find_elements(By.CLASS_NAME , 'cal_amount')
    meal_divs = table.find_elements(By.CLASS_NAME , "meal_box")
    for meal_div in meal_divs:
        meal = meal_div.find_element(By.CLASS_NAME , "print_meal_title").get_attribute("innerHTML")
        cal_amount = meal_div.find_element(By.CLASS_NAME , 'cal_amount').get_attribute("innerHTML")
        names = []
        servings = meal_div.find_elements(By.CLASS_NAME , "amount_input")
        n_servings = [n.get_attribute("value") for n in servings]
        for elem in meal_div.find_elements(By.CLASS_NAME , "print_name"):
            names.append(elem.get_attribute("innerHTML"))
        new = []
        for name,n in zip(names , n_servings):
            new.append({repr("".join(name.strip())) : n})
        meals[meal] = [cal_amount , new]
    chr_driver.close()
    return meals



def bmr(gender1, weight1 , height1 , age1 , activity1):
    gender = float(gender1)
    weight = float(weight1)
    height = float(height1)
    age = float(age1)
    activity = float(activity1)
    multipliers = {
        0 : 1 ,
        1 : 1.2 ,
        2 : 1.375 , 
        3 : 1.55 ,
        5 : 1.725 ,
        6 : 1.9
    }
    #females
    if gender == "gender":
        return False
    if gender == 0:
        x =  (10.0 * weight ) + (6.25 * height) - (5.0 *age) -161.0
        return x * multipliers[activity]
    #males
    x =  (10.0 * weight) + (6.25 * height) - (5.0 * age) + 5.0
    return x * multipliers[activity]

def plan_error(calories , meals):
    standard = {
        1 : range(200,4000),
        2 : range(200 , 8000),
        3 : range(300 , 12000),
        4 : range(400 , 16000) , 
        5 : range(500 , 20000), 
        6 : range(600 , 24000) , 
        7 : range(700 , 28000),
        8 : range(800 , 32000) ,
        9 : range(900 , 36000) ,
    }
    if calories not in standard[meals] :
        return f"{meals} meals can have a range between {min(standard[meals])} and {max(standard[meals])}"
    #if true
    return True