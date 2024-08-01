def validate_age_not_num(age): #returns True if age is not numeric
    if not age.isnumeric():
        return True
    else:
        return False
    
print(validate_age_not_num("6"))